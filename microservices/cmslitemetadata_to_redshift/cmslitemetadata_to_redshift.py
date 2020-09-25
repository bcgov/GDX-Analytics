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
import logging
import boto3  # s3 access
from botocore.exceptions import ClientError
import pandas as pd  # data processing
import numpy as np
import psycopg2  # to connect to Redshift
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

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

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
def to_s3(loc_batchfile, filename, loc_df, loc_columnlist, loc_index):
    """Funcion to write a CSV to S3"""
    # Put the full data set into a buffer and write it
    # to a "   " delimited file in the batch directory
    csv_buffer = StringIO()
    if loc_columnlist is None:  # no column list, no index
        if loc_index is None:
            loc_df.to_csv(csv_buffer,
                          header=True,
                          index=False,
                          sep="	",
                          encoding='utf-8')
        else:  # no column list, include index
            loc_df.to_csv(csv_buffer,
                          header=True,
                          index=True,
                          sep="	",
                          index_label=loc_index,
                          encoding='utf-8')
    else:
        if loc_index is None:  # column list, no index
            loc_df.to_csv(csv_buffer,
                          header=True,
                          index=False,
                          sep="	",
                          columns=loc_columnlist,
                          encoding='utf-8')
        # column list, include index
        else:
            loc_df.to_csv(csv_buffer,
                          header=True,
                          index=True,
                          sep="	",
                          columns=loc_columnlist,
                          index_label=loc_index,
                          encoding='utf-8')

    logger.debug("Writing " + filename + " to " + loc_batchfile)
    resource.Bucket(bucket).put_object(Key=loc_batchfile + "/" + filename,
                                       Body=csv_buffer.getvalue())


# Create a dictionary dataframe based on a column
def to_dict(loc_df, section):
    '''build a dictionary type dataframe for a column with nested delimeters'''
    # drop any nulls and wrapping delimeters, split and flatten:
    clean = loc_df.copy().dropna(
        subset=[section])[section].str[1:-1].str.split(
            nested_delim).values.flatten()
    # set to exlude duplicates
    L = list(set(itertools.chain.from_iterable(clean)))
    # make a dataframe of the list
    return pd.DataFrame({section: sorted(L)})


# Check to see if the file has been processed already
def is_processed(loc_object_summary):
    '''check S3 for objects already processed'''
    # Check to see if the file has been processed already
    loc_key = loc_object_summary.key
    filename = loc_key[loc_key.rfind('/') + 1:]  # get the filename string
    loc_goodfile = destination + "/good/" + key
    loc_badfile = destination + "/bad/" + key
    try:
        client.head_object(Bucket=bucket, Key=loc_goodfile)
    except ClientError:
        pass  # this object does not exist under the good destination path
    else:
        return True
    try:
        client.head_object(Bucket=bucket, Key=loc_badfile)
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
    except pd.errors.EmptyDataError:
        logger.debug("Empty file, proceeding")
        outfile = goodfile
    except pd.errors.ParserError:
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
                if row[column] is not np.nan:
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
        to_s3(batchfile, dbtable + '.csv', df_new, columnlist, key)

        # append the formatted copy query to the copy_queries dictionary
        copy_queries[dbtable] = (
            f"COPY {dbtable}_scratch FROM \n"
            f"'s3://{bucket_name}/{batchfile}/{dbtable}.csv' \n"
            f"CREDENTIALS 'aws_access_key_id={aws_access_key_id};"
            f"aws_secret_access_key={aws_secret_access_key}' \n"
            "IGNOREHEADER AS 1 MAXERROR AS 0 \n"
            "DELIMITER '	' NULL AS '-' ESCAPE;\n")

    # prepare the single-transaction query
    query = f'BEGIN; \nSET search_path TO {dbschema};'
    for table, copy_query in copy_queries.items():
        start_query = (
            f'DROP TABLE IF EXISTS {table}_scratch;\n'
            f'DROP TABLE IF EXISTS {table}_old;\n'
            f'CREATE TABLE {table}_scratch (LIKE {table});\n'
            f'ALTER TABLE {table}_scratch OWNER TO microservice;\n'
            f'GRANT SELECT ON {table}_scratch TO looker;\n')
        end_query = (
            f'ALTER TABLE {table} RENAME TO {table}_old;\n'
            f'ALTER TABLE {table}_scratch RENAME TO {table};\n'
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
query = """
-- perform this as a transaction.
-- Either the whole query completes, or it leaves the old table intact
BEGIN;
SET search_path TO {dbschema};
DROP TABLE IF EXISTS {dbschema}.themes;
CREATE TABLE IF NOT EXISTS {dbschema}.themes (
  "node_id"	       VARCHAR(255),
  "title"		   VARCHAR(2047),
  "hr_url"	       VARCHAR(2047),
  "parent_node_id" VARCHAR(255),
  "parent_title"   VARCHAR(2047),
  "theme_id"	   VARCHAR(255),
  "subtheme_id"	   VARCHAR(255),
  "topic_id"	   VARCHAR(255),
  "subtopic_id"	   VARCHAR(255),
  "subsubtopic_id" VARCHAR(255),
  "theme"		   VARCHAR(2047),
  "subtheme"	   VARCHAR(2047),
  "topic"		   VARCHAR(2047),
  "subtopic"	   VARCHAR(2047),
  "subsubtopic"	   VARCHAR(2047)
);
ALTER TABLE {dbschema}.themes OWNER TO microservice;
GRANT SELECT ON {dbschema}.themes TO looker;

INSERT INTO {dbschema}.themes
WITH ids
AS (SELECT cm.node_id,
      cm.title,
      cm.hr_url,
      cm.parent_node_id,
      cm_parent.title AS parent_title,
      cm.ancestor_nodes,
      CASE
        -- page is root: Gov, Intranet, ALC, MCFD or Training SITE
        WHEN cm.node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',
                            'A9A4B738CE26466C92B45A66DD8C2AFC',
                            '7B239105652B4EBDAB215C59B75A453B',
                            'AFE735F4ADA542ACA830EBC10D179FBE',
                            'D69135AB037140D880A4B0E725D15774')
          THEN '||'
        -- parent page is root: Gov, Intranet, ALC, MCFD or Training SITE
        WHEN cm.parent_node_id IN ('CA4CBBBB070F043ACF7FB35FE3FD1081',
                            'A9A4B738CE26466C92B45A66DD8C2AFC',
                            '7B239105652B4EBDAB215C59B75A453B',
                            'AFE735F4ADA542ACA830EBC10D179FBE',
                            'D69135AB037140D880A4B0E725D15774')
          THEN '|' || cm.node_id || '|'
        -- "first" page is root: Gov, Intranet, ALC, MCFD or Training SITE
        WHEN TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 2)) IN
                           ('CA4CBBBB070F043ACF7FB35FE3FD1081',
                            'A9A4B738CE26466C92B45A66DD8C2AFC',
                            '7B239105652B4EBDAB215C59B75A453B',
                            'AFE735F4ADA542ACA830EBC10D179FBE',
                            'D69135AB037140D880A4B0E725D15774')
          THEN REPLACE(cm.ancestor_nodes, '|' ||
            TRIM(SPLIT_PART(cm.ancestor_nodes, '|', 2)), '') ||
            cm.parent_node_id || '|' || cm.node_id || '|'
        -- an exception for assets, push the parent node to level2 and
        -- leave the node out of the hierarchy
        WHEN cm.ancestor_nodes = '||' AND cm.page_type = 'ASSET'
          THEN cm.ancestor_nodes || cm.parent_node_id
        -- no ancestor nodes
        WHEN cm.ancestor_nodes = '||'
          THEN '|' || cm.parent_node_id || '|' || cm.node_id || '|'
        ELSE cm.ancestor_nodes || cm.parent_node_id || '|' || cm.node_id || '|'
      END AS full_tree_nodes,
      -- The first SPLIT_PART of full_tree_nodes is always blank as the
      -- string has '|' on each end
      CASE
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 2)) <> ''
          THEN TRIM(SPLIT_PART(full_tree_nodes, '|', 2))
        ELSE NULL
      END AS level1_id,
      CASE
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 3)) <> ''
          THEN TRIM(SPLIT_PART(full_tree_nodes, '|', 3))
        ELSE NULL
      END AS level2_id,
      --  exception for Service BC pages:
      -- "promote" FD6DB5BA2A5248038EEF54D9F9F37C4D as a topic and
      -- raise up its children as sub-topics
      CASE
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 7)) =
          'FD6DB5BA2A5248038EEF54D9F9F37C4D'
          THEN 'FD6DB5BA2A5248038EEF54D9F9F37C4D'
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 4)) <> ''
          THEN TRIM(SPLIT_PART(full_tree_nodes, '|', 4))
        ELSE NULL
      END AS level3_id,
      CASE
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 7)) =
          'FD6DB5BA2A5248038EEF54D9F9F37C4D'
          AND TRIM(SPLIT_PART(full_tree_nodes, '|', 8)) <> ''
          THEN TRIM(SPLIT_PART(full_tree_nodes, '|', 8))
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 7)) <
          'FD6DB5BA2A5248038EEF54D9F9F37C4D'
          AND TRIM(SPLIT_PART(full_tree_nodes, '|', 5)) <> '
          THEN TRIM(SPLIT_PART(full_tree_nodes, '|', 5))
        ELSE NULL
      END AS level4_id,
      CASE
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 7)) =
          'FD6DB5BA2A5248038EEF54D9F9F37C4D'
          AND TRIM(SPLIT_PART(full_tree_nodes, '|', 9)) <> ''
          THEN TRIM(SPLIT_PART(full_tree_nodes, '|', 9))
        WHEN TRIM(SPLIT_PART(full_tree_nodes, '|', 7)) <>
          'FD6DB5BA2A5248038EEF54D9F9F37C4D'
          AND TRIM(SPLIT_PART(full_tree_nodes, '|', 6)) <> ''
          THEN TRIM(SPLIT_PART(full_tree_nodes, '|', 6))
        ELSE NULL
      END AS level5_id
    FROM {dbschema}.metadata AS cm
      LEFT JOIN {dbschema}.metadata AS cm_parent
        ON cm_parent.node_id = cm.parent_node_id),
biglist
  AS (SELECT
    ROW_NUMBER () OVER ( PARTITION BY ids.node_id ) AS index,
    ids.*,
    l1.title AS theme,
    l2.title AS subtheme,
    l3.title AS topic,
    l4.title AS subtopic,
    l5.title AS subsubtopic,
  CASE
    WHEN theme IS NOT NULL
      THEN level1_ID
    ELSE NULL
  END AS theme_ID,
  CASE
    WHEN subtheme IS NOT NULL
      THEN level2_ID
    ELSE NULL
  END AS subtheme_ID,
  CASE
    WHEN topic IS NOT NULL
      THEN level3_ID
    ELSE NULL
  END AS topic_ID,
  CASE
    WHEN subtopic IS NOT NULL
      THEN level4_ID
    ELSE NULL
  END AS subtopic_ID,
  CASE
    WHEN subsubtopic IS NOT NULL
      THEN level5_ID
    ELSE NULL
  END AS subsubtopic_ID
FROM ids
    LEFT JOIN {dbschema}.metadata AS l1
      ON l1.node_id = ids.level1_id
    LEFT JOIN {dbschema}.metadata AS l2
      ON l2.node_id = ids.level2_id
    LEFT JOIN {dbschema}.metadata AS l3
      ON l3.node_id = ids.level3_id
    LEFT JOIN {dbschema}.metadata AS l4
      ON l4.node_id = ids.level4_id
    LEFT JOIN {dbschema}.metadata AS l5
      ON l5.node_id = ids.level5_id
)
SELECT node_id,
       title,
       hr_url,
       parent_node_id,
       parent_title,
       theme_id,
       subtheme_id,
       topic_id,
       subtopic_id,
       subsubtopic_id,
       theme,
       subtheme,
       topic,
       subtopic,
       subsubtopic
FROM biglist
WHERE index = 1
COMMIT;
""".format(dbschema=dbschema)

# Execute the query and log the outcome
logger.debug('Executing query:\n%s', query)
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
            query = (f"SET search_path TO {dbschema}; "
                     "INSERT INTO microservice_log VALUES "
                     f"('{starttime}', '{endtime}');")
            try:
                curs.execute(query)
            except psycopg2.Error:  # if the DB call fails, print error
                logger.exception(
                    "Failed to write to %s.microservice_log", dbschema)
            else:
                logger.info("timestamp row added to microservice_log table")
                logger.debug("start time: %s -- end time: %s",
                             starttime, endtime)
