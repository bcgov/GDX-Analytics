"""parse a cmslite csv file from s3 and load it into Redshift"""
###################################################################
# Script Name   : cmslitemetadata_to_redshift.py
#
# Description   : Microservice script to load a cmslite csv file from s3
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
# Usage         : pip install -r requirements.txt
#               : python cmslitemetadata_to_redshift.py configfile.json
#

import re  # regular expressions
from io import StringIO
import os  # to read environment variables
import json  # to read json config files
import sys  # to read command line parameters
import itertools  # functional tools for creating and using iterators
import datetime
import boto3  # s3 access
from botocore.exceptions import ClientError
import pandas as pd  # data processing
import psycopg2  # to connect to Redshift
import logging
import lib.logs as log

logger = logging.getLogger(__name__)
log.setup()

# we will use this timestamp to write to the cmslite.microservice_log table
# changes to that table trigger Looker cacheing. As a result, Looker refreshes
# its cmslite metadata cache each time this microservice completes
starttime = str(datetime.datetime.now())


# Read configuration file
if len(sys.argv) != 2:  # will be 1 if no arguments, 2 if one argument
    logger.error(
        "Usage: python27 cmslitemetadata_to_redshift.py configfile.json")
    sys.exit(1)
configfile = sys.argv[1]
if os.path.isfile(configfile) is False:  # confirm that the file exists
    logger.error("Invalid file name %s", configfile)
    sys.exit(1)
with open(configfile) as f:
    data = json.load(f)

# Set up variables from config file
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

column_count = data['column_count']
columns_metadata = data['columns_metadata']
columns_lookup = data['columns_lookup']
dbtables_dictionaries = data['dbtables_dictionaries']
dbtables_metadata = data['dbtables_metadata']
nested_delim = data['nested_delim']
columns = data['columns']
dtype_dic = {}
if 'dtype_dic_strings' in data:
    for fieldname in data['dtype_dic_strings']:
        dtype_dic[fieldname] = str
delim = data['delim']
truncate = data['truncate']

# set up S3 connection
client = boto3.client('s3')  # low-level functional API
resource = boto3.resource('s3')  # high-level object-oriented API
my_bucket = resource.Bucket(bucket)  # subsitute this for your s3 bucket name.
bucket_name = my_bucket.name

# prep database call to pull the batch file into redshift
conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=os.environ['pguser'],
           password=os.environ['pgpass'])


# bucket = the S3 bucket
# filename = the name of the original file being processed (eg. example.csv)
# batchfile = the name of the batch file. This will be appended to the
# original filename path (eg. part01.csv -> "example.csv/part01.csv")
# df = the dataframe to write out
# columnlist = a list of columns to use from the dataframe. Must be the same
# order as the SQL table. If null (eg None in Python), will write all columns
# in order.
# index = if not Null, add an index column with this label
def to_s3(bucket, batchfile, filename, df, columnlist, index):
    """Funcion to write a CSV to S3"""
    # Put the full data set into a buffer and write it
    # to a "   " delimited file in the batch directory
    csv_buffer = StringIO()
    if columnlist is None:  # no column list, no index
        if index is None:
            df.to_csv(csv_buffer,
                      header=True,
                      index=False,
                      sep="	",
                      encoding='utf-8')
        else:  # no column list, include index
            df.to_csv(csv_buffer,
                      header=True,
                      index=True,
                      sep="	",
                      index_label=index,
                      encoding='utf-8')
    else:
        if index is None:  # column list, no index
            df.to_csv(csv_buffer,
                      header=True,
                      index=False,
                      sep="	",
                      columns=columnlist,
                      encoding='utf-8')
        # column list, include index
        else:
            df.to_csv(csv_buffer,
                      header=True,
                      index=True,
                      sep="	",
                      columns=columnlist,
                      index_label=index,
                      encoding='utf-8')

    logger.debug("Writing " + filename + " to " + batchfile)
    resource.Bucket(bucket).put_object(Key=batchfile + "/" + filename,
                                       Body=csv_buffer.getvalue())


# Create a dictionary dataframe based on a column
def to_dict(df, section):
    '''build a dictionary type dataframe for a column with nested delimeters'''
    # drop any nulls and wrapping delimeters, split and flatten:
    clean = df.copy().dropna(
        subset=[section])[section].str[1:-1].str.split(
            nested_delim).values.flatten()
    # set to exlude duplicates
    L = list(set(itertools.chain.from_iterable(clean)))
    # make a dataframe of the list
    return pd.DataFrame({section: sorted(L)})


# Check to see if the file has been processed already
def is_processed(object_summary):
    '''check S3 for objects already processed'''
    # Check to see if the file has been processed already
    key = object_summary.key
    filename = key[key.rfind('/')+1:]  # get the filename (after the last '/')
    goodfile = destination + "/good/" + key
    badfile = destination + "/bad/" + key
    try:
        client.head_object(Bucket=bucket, Key=goodfile)
    except ClientError:
        pass  # this object does not exist under the good destination path
    else:
        return True
    try:
        client.head_object(Bucket=bucket, Key=badfile)
    except ClientError:
        pass  # this object does not exist under the bad destination path
    else:
        return True
    logger.debug("%s has not been processed.", filename)
    return False


# This bucket scan will find unprocessed objects.
# objects_to_process will contain zero or one objects if truncate=True;
# objects_to_process will contain zero or more objects if truncate=False.
objects_to_process = []
for object_summary in my_bucket.objects.filter(Prefix=source + "/"
                                               + directory + "/"):
    key = object_summary.key
    # skip to next object if already processed
    if is_processed(object_summary):
        continue

    logger.debug("Processing %s", object_summary)
    # only review those matching our configued 'doc' regex pattern
    if re.search(doc + '$', key):
        # under truncate, we will keep list length to 1
        # only adding the most recently modified file to objects_to_process
        if truncate:
            if len(objects_to_process) == 0:
                objects_to_process.append(object_summary)
                continue
            # compare last modified dates of the latest and current obj
            if (object_summary.last_modified
                    > objects_to_process[0].last_modified):
                objects_to_process[0] = object_summary
            else:
                logger.debug(
                    "skipping %s; less recent than %s", key,
                    object_summary.last_modified)
        else:
            # no truncate, so the list may exceed 1 element
            objects_to_process.append(object_summary)

if truncate and len(objects_to_process) == 1:
    logger.info(('truncate is set. processing most recent file match: '
                 '%s (modified %s)'), objects_to_process[0].key,
                objects_to_process[0].last_modified)

# process the objects that were found during the earlier directory pass
for object_summary in objects_to_process:
    # Check to see if the file has been processed already
    batchfile = destination + "/batch/" + object_summary.key
    goodfile = destination + "/good/" + object_summary.key
    badfile = destination + "/bad/" + object_summary.key

    # Load the object from S3 using Boto and set body to be its contents
    obj = client.get_object(Bucket=bucket, Key=object_summary.key)
    body = obj['Body']

    csv_string = body.read().decode('utf-8')

    # XX  temporary fix while we figure out better delimiter handling
    csv_string = csv_string.replace('	', ' ')

    # Check for an empty file. If it's empty, accept it as good and move on
    try:
        df = pd.read_csv(StringIO(csv_string),
                         sep=delim,
                         index_col=False,
                         dtype=dtype_dic,
                         usecols=range(column_count))
    except Exception as e:
        if str(e) == "No columns to parse from file":
            logger.debug("Empty file, proceeding")
            outfile = goodfile
        else:
            logger.exception("Parse error:")
            outfile = badfile

        # For the two exceptions cases, write to either the Good or Bad folder.
        # Otherwise, continue to process the file.
        client.copy_object(
            Bucket="sp-ca-bc-gov-131565110619-12-microservices",
            CopySource=("sp-ca-bc-gov-131565110619-12-microservices/"
                        f"{object_summary.key}"),
            Key=outfile)
        continue

    # set the data frame to use the columns listed in the .conf file.
    # Note that this overrides the columns in the file, and will give an error
    # if the wrong number of columns is present.
    # It will not validate the existing column names.
    df.columns = columns

    # Run rename to change column names
    if 'rename' in data:
        for thisfield in data['rename']:
            if thisfield['old'] in df.columns:
                df.rename(columns={thisfield['old']: thisfield['new']},
                          inplace=True)

    # Run replace on some fields to clean the data up
    if 'replace' in data:
        for thisfield in data['replace']:
            df[thisfield['field']].str.replace(thisfield['old'],
                                               thisfield['new'])

    # Clean up date fields, for each field listed in the dateformat array named
    # "field" apply "format". Leaves null entries as blanks instead of NaT.
    if 'dateformat' in data:
        for thisfield in data['dateformat']:
            df[thisfield['field']] = pd.to_datetime(
                df[thisfield['field']]).apply(
                    lambda x: x.strftime(
                        thisfield['format']) if not pd.isnull(x) else '')

    # We loop over the columns listed in the JSON configuration file.
    # There are three sets of values that should match to consider:
    # - columns_lookup
    # - dbtables_dictionaries
    # - dbtables_metadata

    # The table is built in the same way as the others, but this allows us
    # to resuse the code below in the loop to write the batch file and run
    # the SQL command.

    dictionary_dfs = {}  # keep the dictionaries in storage
    # loop starts at index -1 to process the main metadata table.

    # build an aggregate query which will be used to make one transaction
    copy_queries = {}
    for i in range(-1, len(columns_lookup)*2):
        # the metadata table is built once
        if i == -1:
            column = "metadata"
            dbtable = "metadata"
            key = None
            columnlist = columns_metadata
            df_new = df.copy()
        # the column lookup tables are built
        elif i < len(columns_lookup):
            key = "key"
            column = columns_lookup[i]
            columnlist = [columns_lookup[i]]
            dbtable = dbtables_dictionaries[i]
            df_new = to_dict(df, column)  # make dict a df of this column
            dictionary_dfs[columns_lookup[i]] = df_new
        # the metadata tables are built
        else:
            i_off = i - len(columns_lookup)
            key = None
            column = columns_lookup[i_off]
            columnlist = ['node_id', 'lookup_id']
            dbtable = dbtables_metadata[i_off]

            df_dictionary = dictionary_dfs[column]  # retrieve the dict in mem

            # for each row in df
            df_new = pd.DataFrame(columns=columnlist)
            for index, row in df.copy().iterrows():
                # iterate over the list of delimited terms
                if row[column] is not pd.np.nan:
                    # get the full string of delimited values to be looked up
                    entry = row[column]
                    # remove wrapping delimeters
                    entry = entry[1:-1]
                    if entry:  # skip empties
                        # split on delimiter and iterate on resultant list
                        for lookup_entry in entry.split(nested_delim):
                            node_id = row.node_id
                            # its dictionary index
                            lookup_id = df_dictionary.loc[
                                df_dictionary[column] == lookup_entry].index[0]
                            # create the data frame to concat
                            d = pd.DataFrame(
                                [[node_id, lookup_id]], columns=columnlist)
                            df_new = pd.concat([df_new, d], ignore_index=True)

        # output the the dataframe as a csv
        to_s3(bucket, batchfile, dbtable + '.csv', df_new, columnlist, key)

        copy_query_unformatted = (
            "COPY {dbtable}_scratch FROM \n"
            "'s3://{my_bucket_name}/{batchfile}/{dbtable}.csv' \n"
            "CREDENTIALS 'aws_access_key_id={aws_access_key_id};"
            "aws_secret_access_key={aws_secret_access_key}' \n"
            "IGNOREHEADER AS 1 MAXERROR AS 0 \n"
            "DELIMITER '	' NULL AS '-' ESCAPE;\n")

        # append the formatted copy query to the copy_queries dictionary
        copy_queries[dbtable] = copy_query_unformatted.format(
            dbtable=dbtable,
            my_bucket_name=bucket_name,
            batchfile=batchfile,
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

    # prepare the single-transaction query
    query = 'BEGIN; \nSET search_path TO {dbschema};'.format(
        dbschema=dbschema)
    for table, copy_query in copy_queries.items():
        start_query = (
            f'DROP TABLE IF EXISTS {table}_scratch;\n'
            f'DROP TABLE IF EXISTS {table}_old;\n'
            f'CREATE TABLE {table}_scratch (LIKE {table});\n'
            f'ALTER TABLE {table}_scratch OWNER TO microservice;\n'
            f'GRANT SELECT ON {table}_scratch TO looker;\n')
        end_query = (
            f'ALTER TABLE {table} RENAME TO {table}_old;\n',
            f'ALTER TABLE {table}_scratch RENAME TO {table};\n',
            f'DROP TABLE {table}_old;\n')
        query = query + start_query + copy_query + end_query
    query = query + 'COMMIT;\n'
    logquery = (
        query.replace
        (os.environ['AWS_ACCESS_KEY_ID'], 'AWS_ACCESS_KEY_ID').replace
        (os.environ['AWS_SECRET_ACCESS_KEY'], 'AWS_SECRET_ACCESS_KEY'))

    logger.debug('\n%s', logquery)
    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as curs:
            try:
                curs.execute(query)
            except psycopg2.Error:
                logger.exception("Executing transaction for %s failed.",
                                 object_summary.key)
                outfile = badfile
            else:  # if the DB call succeed, place file in /good
                logger.info("Executing transaction %s succeeded.",
                            object_summary.key)
                outfile = goodfile

    # Copies the uploaded file from client into processed/good or /bad
    client.copy_object(
        Bucket=f"{bucket}",
        CopySource=f"{bucket}/{object_summary.key}",
        Key=outfile)

# now we run the single-time load on the cmslite.themes
query = (
    f"SET search_path TO {dbschema};"
    f"TRUNCATE {dbschema}.themes;"
    f"INSERT INTO {dbschema}.themes"
    "WITH ids AS ("
    "\tSELECT cm.node_id,"
    "\t\tcm.title,"
    "\t\tcm.hr_url,"
    "\t\tcm.parent_node_id,"
    "\t\tcm_parent.title AS parent_title,"
    "\t\tCASE"
    "\t\t\tWHEN cm.node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',"
    "'A9A4B738CE26466C92B45A66DD8C2AFC') THEN NULL "
    "-- page is a home page either web or intranet home"
    "\t\t\tWHEN cm.parent_node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',"
    "'A9A4B738CE26466C92B45A66DD8C2AFC') AND cm.page_type IN ('BC Gov Theme',"
    "'Intranet Home') THEN cm.node_id "
    "-- page is a theme -- NOTE we call intranet 'homes' as Themes"
    "\t\t\tWHEN cm.ancestor_nodes = '||' AND cm_parent.page_type IN ('BC Gov"
    " Theme','Intranet Home') THEN cm.parent_node_id -- parent is a theme"
    "\t\t\tWHEN TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 2)) <> '' THEN TRIM("
    "SPLIT_PART(cm.ancestor_nodes, '|', 2)) "
    "-- take the second entry. The first is always blank as the string has"
    " '|' on each end"
    "\t\t\tELSE NULL"
    "\t\tEND AS theme_id,"
    "\t\tCASE"
    "\t\t\tWHEN cm.node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',"
    "'A9A4B738CE26466C92B45A66DD8C2AFC') THEN NULL -- page is a home page"
    "\t\t\tWHEN cm.parent_node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',"
    "'A9A4B738CE26466C92B45A66DD8C2AFC') AND cm.page_type IN ('BC Gov Theme',"
    "'Intranet Home') THEN NULL "
    "-- page is a theme -- NOTE we call intranet 'homes' as Themes"
    "\t\t\tWHEN cm.ancestor_nodes = '||' AND cm_parent.page_type IN "
    "('BC Gov Theme','Intranet Home') THEN cm.node_id "
    "-- parent is a theme, so this is a subtheme"
    "\t\t\tWHEN TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 3)) = '' THEN "
    "cm.parent_node_id -- the parent is a subtheme"
    "\t\t\tWHEN TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 3)) <> '' THEN "
    "TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 3)) -- take the third entry. "
    "The first is always blank as the string has '|' on each end and the "
    "second is the theme, the third is a subtheme"
    "\t\t\tELSE NULL"
    "\t\tEND AS subtheme_id,"
    "\t\tCASE"
    "\t\t\tWHEN cm.node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',"
    "'A9A4B738CE26466C92B45A66DD8C2AFC') THEN NULL -- page is a home page"
    "\t\t\tWHEN cm.parent_node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',"
    "'A9A4B738CE26466C92B45A66DD8C2AFC') AND cm.page_type IN ('BC Gov Theme',"
    "'Intranet Home') THEN NULL -- page is a theme"
    "\t\t\tWHEN cm.node_id = 'FD6DB5BA2A5248038EEF54D9F9F37C4D' OR "
    "cm_parent.node_id = 'FD6DB5BA2A5248038EEF54D9F9F37C4D' THEN "
    "'FD6DB5BA2A5248038EEF54D9F9F37C4D' "
    "-- built in override to make all ServiceBC pages one topic"
    "\t\t\tWHEN TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 3)) = '' AND "
    "cm_parent.page_type IN ('BC Gov Theme','Intranet Theme') AND "
    "cm.page_type = 'Topic' THEN cm.node_id "
    "-- the page's parent is a sub-theme and it is a topic page"
    "\t\t\tWHEN TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 4)) = '' AND "
    "cm_parent.page_type = 'Topic' THEN cm.parent_node_id "
    "-- the page's parent is a topic"
    "\t\t\tWHEN TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 4)) <> '' THEN "
    "TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 4)) -- take the fourth entry. "
    "The first is always blank as the string has '|' on each end and the "
    "second is the theme, third is sub-theme"
    "\t\t\tELSE NULL"
    "\t\tEND AS topic_id"
    f"\t\tFROM {dbschema}.metadata AS cm"
    f"\t\tLEFT JOIN {dbschema}.metadata AS cm_parent ON cm_parent.node_id = "
    "cm.parent_node_id"
    "\t),"
    "biglist AS ("
    "\tSELECT"
    "\t\tROW_NUMBER () OVER ( PARTITION BY ids.node_id ) AS index,"
    "\t\tids.*,"
    "\t\tcm_theme.title AS theme,"
    "\t\tcm_sub_theme.title AS subtheme,"
    "\t\tcm_topic.title AS topic"
    "\t\tFROM ids"
    f"\t\tLEFT JOIN {dbschema}.metadata AS cm_theme ON cm_theme.node_id = "
    "theme_id"
    f"\t\tLEFT JOIN {dbschema}.metadata AS cm_sub_theme ON cm_sub"
    "_theme.node_id = subtheme_id"
    f"\t\tLEFT JOIN {dbschema}.metadata AS cm_topic ON cm_topic.node_id = "
    "topic_id"
    "\t)"
    "SELECT node_id, title, hr_url, parent_node_id, parent_title, theme_id, "
    "subtheme_id, topic_id, theme, subtheme, topic FROM biglist WHERE"
    " index = 1 ;"
)

# Execute the query and log the outcome
logger.debug(query)
with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        # if the DB call fails, print error and place file in /bad
        except psycopg2.Error:
            logger.exception("Themes table loading failed")
        # if the DB call succeed, place file in /good
        else:
            logger.info("Themes table loaded successfully")
            # if the job was succesful, write to cmslite.microservice_log
            endtime = str(datetime.datetime.now())
            query = "".join(("SET search_path TO {dbschema}; ",
                             "INSERT INTO microservice_log VALUES ",
                             "('{starttime}', '{endtime}');")).format(
                                 dbschema=dbschema,
                                 starttime=starttime,
                                 endtime=endtime)
            try:
                curs.execute(query)
            except psycopg2.Error:  # if the DB call fails, print error
                logger.exception(
                    "Failed to write to %s.microservice_log", dbschema)
