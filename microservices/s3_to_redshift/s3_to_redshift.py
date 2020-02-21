###################################################################
# Script Name   : s3_to_redshift.py
#
# Description   : Microservice script to load a csv file from s3
#               : and load it into Redshift
#
# Requirements  : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#               : export pgpass=<<DB_PASSWD>>
#
#
# Usage         : python s3_to_redshift.py configfile.json
#

import boto3  # s3 access
from botocore.exceptions import ClientError
import pandas as pd  # data processing
import re  # regular expressions
from io import StringIO
import os  # to read environment variables
import json  # to read json config files
import sys  # to read command line parameters
import os.path  # file handling
from ua_parser import user_agent_parser
from referer_parser import Referer
from lib.redshift import RedShift
import logging
import lib.logs as GDXLogging

logger = logging.getLogger(__name__)
GDXLogging.setup()

# check that configuration file was passed as argument
if (len(sys.argv) != 2):
    print('Usage: python s3_to_redshift.py config.json')
    sys.exit(1)
configfile = sys.argv[1]
# confirm that the file exists
if os.path.isfile(configfile) is False:
    print("Invalid file name {}".format(configfile))
    sys.exit(1)
# open the confifile for reading
with open(configfile) as f:
    data = json.load(f)

# get variables from config file
bucket = data['bucket']
source = data['source']
destination = data['destination']
directory = data['directory']
doc = data['doc']
if 'dbschema' in data:
    dbschema = data['dbschema']
else:
    dbschema = 'microservice'
dbtable = data['dbtable']
table_name = dbtable[dbtable.rfind(".")+1:]
column_count = data['column_count']
columns = data['columns']
dtype_dic = {}
if 'dtype_dic_strings' in data:
    for fieldname in data['dtype_dic_strings']:
        dtype_dic[fieldname] = str
if 'dtype_dic_bools' in data:
    for fieldname in data['dtype_dic_bools']:
        dtype_dic[fieldname] = bool
delim = data['delim']
truncate = data['truncate']
if 'drop_columns' in data:
    drop_columns = data['drop_columns']
else:
    drop_columns = {}

# set up S3 connection
client = boto3.client('s3')  # low-level functional API
resource = boto3.resource('s3')  # high-level object-oriented API
my_bucket = resource.Bucket(bucket)  # subsitute this for your s3 bucket name.
bucket_name = my_bucket.name

# Database connection string
conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=os.environ['pguser'],
           password=os.environ['pgpass'])


# Constructs the database copy query string
def copy_query(dbtable, batchfile, log):
    if log:
        aws_key = 'AWS_ACCESS_KEY_ID'
        aws_secret_key = 'AWS_SECRET_ACCESS_KEY'
    else:
        aws_key = os.environ['AWS_ACCESS_KEY_ID']
        aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    query = """
COPY {0}\nFROM 's3://{1}/{2}'\n\
CREDENTIALS 'aws_access_key_id={3};aws_secret_access_key={4}'\n\
IGNOREHEADER AS 1 MAXERROR AS 0 DELIMITER '|' NULL AS '-' ESCAPE;\n
""".format(dbtable, bucket_name, batchfile, aws_key, aws_secret_key)
    return query


# Check to see if the file has been processed already
def is_processed(object_summary):
    key = object_summary.key
    filename = key[key.rfind('/')+1:]  # get the filename (after the last '/')
    goodfile = destination + "/good/" + key
    badfile = destination + "/bad/" + key
    try:
        client.head_object(Bucket=bucket, Key=goodfile)
    except ClientError:
        pass  # this object does not exist under the good destination path
    else:
        logger.debug("{0} was processed as good already.".format(filename))
        return True
    try:
        client.head_object(Bucket=bucket, Key=badfile)
    except ClientError:
        pass  # this object does not exist under the bad destination path
    else:
        logger.debug("{0} was processed as bad already.".format(filename))
        return True
    logger.debug("{0} has not been processed.".format(filename))
    return False


# This bucket scan will find unprocessed objects.
# objects_to_process will contain zero or one objects if truncate = True
# objects_to_process will contain zero or more objects if truncate = False
objects_to_process = []
for object_summary in my_bucket.objects.filter(Prefix=source + "/"
                                               + directory + "/"):
    key = object_summary.key
    # skip to next object if already processed
    if is_processed(object_summary):
        continue
    else:
        # only review those matching our configued 'doc' regex pattern
        if re.search(doc + '$', key):
            # under truncate = True, we will keep list length to 1
            # only adding the most recently modified file to objects_to_process
            if truncate:
                if len(objects_to_process) == 0:
                    objects_to_process.append(object_summary)
                    continue
                else:
                    # compare last modified dates of the latest and current obj
                    if (object_summary.last_modified
                            > objects_to_process[0].last_modified):
                        objects_to_process[0] = object_summary
            else:
                # no truncate, so the list may exceed 1 element
                objects_to_process.append(object_summary)

# an object exists to be processed as a truncate copy to the table
if truncate and len(objects_to_process) == 1:
    logger.info(
        'truncate is set. processing only one file: {0} (modified {1})'.format(
            objects_to_process[0].key, objects_to_process[0].last_modified))

# process the objects that were found during the earlier directory pass
for object_summary in objects_to_process:
    batchfile = destination + "/batch/" + object_summary.key
    goodfile = destination + "/good/" + object_summary.key
    badfile = destination + "/bad/" + object_summary.key

    # get the object from S3 and take its contents as body
    obj = client.get_object(Bucket=bucket, Key=object_summary.key)
    body = obj['Body']

    # Create an object to hold the data while parsing
    csv_string = ''

    # Perform apache access log parsing according to config, if defined
    if 'access_log_parse' in data:
        linefeed = ''
        parsed_list = []
        if(data['access_log_parse']['string_repl']):
            inline_pattern = data['access_log_parse']['string_repl']['pattern']
            inline_replace = data['access_log_parse']['string_repl']['replace']
        body_stringified = body.read()
        # perform regex replacements by line
        for line in body_stringified.splitlines():
            if(data['access_log_parse']['string_repl']):
                line = line.replace(inline_pattern, inline_replace)
            for exp in data['access_log_parse']['regexs']:
                parsed_line, num_subs = re.subn(
                    exp['pattern'], exp['replace'], line)
                if num_subs:
                    user_agent = re.match(exp['pattern'], line).group(9)
                    referrer_url = re.match(exp['pattern'], line).group(8)
                    parsed_ua = user_agent_parser.Parse(user_agent)
                    parsed_referrer_url = Referer(referrer_url,
                                                  data['access_log_parse']
                                                  ['referrer_parse']
                                                  ['curr_url'])

                    # Parse OS family and version
                    ua_string = '|' + parsed_ua['os']['family']
                    if parsed_ua['os']['major'] is not None:
                        ua_string += '|' + parsed_ua['os']['major']
                        if parsed_ua['os']['minor'] is not None:
                            ua_string += '.' + parsed_ua['os']['minor']
                        if parsed_ua['os']['patch'] is not None:
                            ua_string += '.' + parsed_ua['os']['patch']
                    else:
                        ua_string += '|'

                    # Parse Browser family and version
                    ua_string += '|' + parsed_ua['user_agent']['family']
                    if parsed_ua['user_agent']['major'] is not None:
                        ua_string += '|' + parsed_ua['user_agent']['major']
                    else:
                        ua_string += '|' + 'NULL'
                    if parsed_ua['user_agent']['minor'] is not None:
                        ua_string += '.' + parsed_ua['user_agent']['minor']
                    if parsed_ua['user_agent']['patch'] is not None:
                        ua_string += '.' + parsed_ua['user_agent']['patch']

                    # Parse referrer urlhost and medium
                    referrer_string = ''
                    if parsed_referrer_url.referer is not None:
                        referrer_string += '|' + parsed_referrer_url.referer
                    else:
                        referrer_string += '|'
                    if parsed_referrer_url.medium is not None:
                        referrer_string += '|' + parsed_referrer_url.medium
                    else:
                        referrer_string += '|'

                    # use linefeed if defined in config, or default "/r/n"
                    if(data['access_log_parse']['linefeed']):
                        linefeed = data['access_log_parse']['linefeed']
                    else:
                        linefeed = '\r\n'
                    parsed_line += ua_string + referrer_string
                    parsed_list.append(parsed_line)
        csv_string = linefeed.join(parsed_list)
        logger.info(object_summary.key + " parsed successfully")

    # This is not an apache access log
    if 'access_log_parse' not in data:
        csv_string = body.read()

    # Check that the file decodes as UTF-8. If it fails move to bad and end
    try:
        csv_string = csv_string.decode('utf-8')
    except UnicodeDecodeError as e:
        e_object = e.object.splitlines()
        logger.exception(
            ''.join((
                "Decoding UTF-8 failed for file {0}\n"
                .format(object_summary.key),
                "The input file stopped parsing after line {0}:\n{1}\n"
                .format(len(e_object), e_object[-1]),
                "Keying to badfile and skipping.\n")))
        try:
            client.copy_object(
                Bucket="sp-ca-bc-gov-131565110619-12-microservices",
                CopySource="sp-ca-bc-gov-131565110619-12-microservices/"
                + object_summary.key, Key=badfile)
        except Exception as e:
            logger.exception("S3 transfer failed.\n{0}".format(e.message))
        continue

    # Check for an empty file. If it's empty, accept it as good and skip
    # to the next object to process
    try:
        df = pd.read_csv(StringIO(csv_string), sep=delim, index_col=False,
                         dtype=dtype_dic, usecols=range(column_count))
    except Exception as e:
        logger.exception('exception reading {0}'.format(object_summary.key))
        if (str(e) == "No columns to parse from file"):
            logger.warning('File is empty, keying to goodfile \
                           and proceeding.')
            outfile = goodfile
        else:
            logger.warning('File not empty, keying to badfile \
                           and proceeding.')
            outfile = badfile
        client.copy_object(Bucket="sp-ca-bc-gov-131565110619-12-microservices",
                           CopySource="sp-ca-bc-gov-\
                           131565110619-12-microservices/"
                           + object_summary.key, Key=outfile)
        continue

    # map the dataframe column names to match the columns from the configuation
    df.columns = columns

    # Truncate strings according to config set column string length limits
    if 'column_string_limit' in data:
        for key, value in data['column_string_limit'].items():
            df[key] = df[key].str.slice(0, value)

    if 'drop_columns' in data:  # Drop any columns marked for dropping
        df = df.drop(columns=drop_columns)

    # Run replace on some fields to clean the data up
    if 'replace' in data:
        for thisfield in data['replace']:
            df[thisfield['field']].replace(
                thisfield['old'], thisfield['new'])

    # Clean up date fields
    # for each field listed in the dateformat
    # array named "field" apply "format"
    if 'dateformat' in data:
        for thisfield in data['dateformat']:
            df[thisfield['field']] = \
                pd.to_datetime(df[thisfield['field']],
                               format=thisfield['format'])

    # Put the full data set into a buffer and write it
    # to a "|" delimited file in the batch directory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, header=True, index=False, sep="|")
    resource.Bucket(bucket).put_object(Key=batchfile,
                                       Body=csv_buffer.getvalue())

    # prep database call to pull the batch file into redshift
    query = copy_query(dbtable, batchfile, log=False)
    logquery = copy_query(dbtable, batchfile, log=True)

    # if truncate is set to true, perform a transaction that will
    # replace the existing table data with the new data in one commit
    # if truncate is not true then the query remains as just the copy command
    if (truncate):
        scratch_start = """
BEGIN;
-- Clean up from last run if necessary
DROP TABLE IF EXISTS {0}_scratch;
DROP TABLE IF EXISTS {0}_old;
-- Create scratch table to copy new data into
CREATE TABLE {0}_scratch (LIKE {0});
ALTER TABLE {0}_scratch OWNER TO microservice;
-- Grant access to Looker and to Snowplow pipeline users
GRANT SELECT ON {0}_scratch TO looker;\n
GRANT SELECT ON {0}_scratch TO datamodeling;\n
""".format(dbtable)

        scratch_copy = copy_query(
            dbtable + "_scratch", batchfile, log=False)
        scratch_copy_log = copy_query(
            dbtable + "_scratch", batchfile, log=True)

        scratch_cleanup = """
-- Replace main table with scratch table, clean up the old table
ALTER TABLE {0} RENAME TO {1}_old;
ALTER TABLE {0}_scratch RENAME TO {1};
DROP TABLE {0}_old;
COMMIT;
""".format(dbtable, table_name)

        query = scratch_start + scratch_copy + scratch_cleanup
        logquery = scratch_start + scratch_copy_log + scratch_cleanup

    # Execute the transaction against Redshift using local lib redshift module
    logger.debug(logquery)
    spdb = RedShift.snowplow(batchfile)
    try:
        if spdb.query(query):
            outfile = goodfile
        else:
            logger.error("Loading {0} to RedShift failed\n{1}"
                             .format(batchfile, e.pgerror))
            outfile = badfile
    except:
        outfile = badfile
    spdb.close_connection()

    # copy the object to the S3 outfile (processed/good/ or processed/bad/)
    try:
        client.copy_object(
            Bucket="sp-ca-bc-gov-131565110619-12-microservices",
            CopySource="sp-ca-bc-gov-131565110619-12-microservices/"
            + object_summary.key, Key=outfile)
    except boto3.exceptions.ClientError:
        logger.exception("S3 transfer failed")

    logger.debug("finished")
