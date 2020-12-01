###################################################################
# Script Name   : cmslite_user_data_to_redshift.py
#
# Description   :
#
# Requirements  : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#               : export pgpass=<<DB_PASSWD>>
#
#
# Usage         : python cmslite_user_data_to_redshift.py configfile.json
#

import boto3  # s3 access
from botocore.exceptions import ClientError
import pandas as pd  # data processing
import pandas.errors
import re  # regular expressions
from io import StringIO
import os  # to read environment variables
# import psycopg2  # to connect to Redshift
import json  # to read json config files
import sys  # to read command line parameters
from lib.redshift import RedShift
import os.path  # file handling
import logging
from shutil import unpack_archive


# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create stdout handler for logs at the INFO level
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# create file handler for logs at the DEBUG level in
# /logs/asset_data_to_redshift.log
log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
handler = logging.FileHandler(os.path.join('logs', log_filename), "a",
                              encoding=None, delay="true")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# Handle exit code
def clean_exit(code, message):
    """Exits with a logger message and code"""
    logger.info('Exiting with code %s : %s', str(code), message)
    sys.exit(code)


# check that configuration file was passed as argument
if (len(sys.argv) != 2):
    print('Usage: python cmslite_user_data_to_redshift.py config.json')
    clean_exit(1, 'Bad command use.')
configfile = sys.argv[1]
# confirm that the file exists
if os.path.isfile(configfile) is False:
    print("Invalid file name {}".format(configfile))
    clean_exit(1, 'Bad file name.')
# open the confifile for reading
with open(configfile) as f:
    data = json.load(f)

bucket = data['bucket']
source = data['source']
destination = data['destination']
directory = data['directory']
prefix = source + "/" + directory + "/"
doc = data['doc']
dbschema = data['schema']
truncate = data['truncate']
delim = data['delim']

# set up S3 connection
client = boto3.client('s3')  # low-level functional API
resource = boto3.resource('s3')  # high-level object-oriented API
bucket = resource.Bucket(bucket)  # subsitute this for your s3 bucket name.
bucket_name = bucket.name

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


def download_object(o):
    '''downloads object to a tmp directoy'''
    dl_name = o.replace(prefix, '')
    try:
        bucket.download_file(o, './tmp/{0}'.format(dl_name))
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.error("The object does not exist.")
            logger.exception("ClientError 404:")
        else:
            raise


# Check to see if the file has been processed already
def is_processed(object_summary):
    key = object_summary.key
    filename = key[key.rfind('/')+1:]  # get the filename (after the last '/')
    goodfile = destination + "/good/" + key
    badfile = destination + "/bad/" + key
    try:
        client.head_object(Bucket=bucket.name, Key=goodfile)
    except ClientError:
        pass  # this object does not exist under the good destination path
    else:
        logger.debug("{0} was processed as good already.".format(filename))
        return True
    try:
        client.head_object(Bucket=bucket.name, Key=badfile)
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
for object_summary in bucket.objects.filter(Prefix=source + "/"
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


# Process the objects that were found during the earlier directory pass.
# Download the tgz file, unpack it to a temp directory in the local working
# directory, process the files, and then shift the data to redshift. Finally,
# delete the temp directory.

if not os.path.exists('./tmp'):
    os.makedirs('./tmp')

for object_summary in objects_to_process:

    # Download and unpack to a temporary folder: ./tmp
    download_object(object_summary.key)

    # Get the filename from the full path in the object summary key
    filename = re.search("(cms-analytics-csv)(.)*tgz$",
                         object_summary.key).group()

    # Unpack the object in the tmp directory
    unpack_archive('./tmp/' + filename, './tmp/' + filename.rstrip('.tgz'))

    # process files for upload to batch folder on S3
    for file in os.listdir('./tmp/' + filename.rstrip('.tgz')):
        batchfile = destination + "/batch/client/" + directory + '/' + file
        goodfile = destination + "/good/client/" + directory + '/' + file
        badfile = destination + "/bad/client/" + directory + '/' + file

        # Read config data for this file
        file_config = data['files'][file.split('.')[0]]
        dbtable = data['schema'] + '.' + file_config['dbtable']
        table_name = file_config['dbtable']

        file_obj = open('./tmp/' + filename.rstrip('.tgz') + '/' + file,
                        "r",
                        encoding="utf-8")

        # Read the file and build the parsed version
        try:
            df = pd.read_csv(
                file_obj,
                usecols=range(file_config['column_count']))
        except pandas.errors.EmptyDataError as e:
            logger.exception('exception reading %s', file)
            if str(e) == "No columns to parse from file":
                logger.warning('%s is empty, keying to goodfile '
                               'and proceeding.',
                               file)
                outfile = goodfile
            else:
                logger.warning('%s not empty, keying to badfile '
                               'and proceeding.',
                               file)
                outfile = badfile
            try:
                client.copy_object(Bucket=f"{bucket}",
                                   CopySource=f"{bucket}/{object_summary.key}",
                                   Key=outfile)
            except ClientError:
                logger.exception("S3 transfer failed")
                clean_exit(1, f'Bad file {object_summary.key} in objects to '
                           'process,no further processing.')
            continue
        except ValueError:
            logger.exception('ValueError exception reading %s',
                             file)
            logger.warning('Keying to badfile and proceeding.')
            outfile = badfile
            try:
                client.copy_object(Bucket=f"{bucket}",
                                   CopySource=f"{bucket}/{object_summary.key}",
                                   Key=outfile)
            except ClientError:
                logger.exception("S3 transfer failed")
                clean_exit(1, f'Bad file {object_summary.key} in objects to '
                           'process,no further processing.')
            continue

        # Map the dataframe column names to match the columns
        # from the configuration
        df.columns = file_config['columns']

        # Clean up date fields
        # for each field listed in the dateformat
        # array named "field" apply "format"
        if 'dateformat' in file_config:
            for thisfield in file_config['dateformat']:
                df[thisfield['field']] = \
                    pd.to_datetime(df[thisfield['field']],
                                   format=thisfield['format'])

        # Put the full data set into a buffer and write it
        # to a "|" delimited file in the batch directory
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, header=True, index=False, sep="|")
        resource.Bucket(bucket.name).put_object(Key=batchfile,
                                                Body=csv_buffer.getvalue())
        # prep database call to pull the batch file into redshift
        query = copy_query(dbtable, batchfile, log=False)
        logquery = copy_query(dbtable, batchfile, log=True)
        # Execute the transaction against Redshift using local lib
        # redshift module
        logger.debug(logquery)
        spdb = RedShift.snowplow(batchfile)
        if spdb.query(query):
            outfile = destination + "/good/" + object_summary.key
        else:
            outfile = destination + "/bad/" + object_summary.key
        spdb.close_connection()

    # copy the object to the S3 outfile (processed/good/ or processed/bad/)
    try:
        client.copy_object(
            Bucket="sp-ca-bc-gov-131565110619-12-microservices",
            CopySource=(
                "sp-ca-bc-gov-131565110619-12-microservices/"
                f"{object_summary.key}"
            ),
            Key=outfile)
    except ClientError:
        logger.exception("S3 transfer failed")

    if outfile == badfile:
        clean_exit(1, f'Bad file {object_summary.key} in objects to process, '
                   'no further processing.')
    logger.debug("finished %s", object_summary.key)

clean_exit(0, 'Finished all processing cleanly.')
