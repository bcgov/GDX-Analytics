###############################################################################
# Script Name    : redshift_counts.py
#
# Description    : Automates the RedShift queries for iteration testing step 5
#                : loads the results into S3
#
# Requirements   : You must set the following environment variables
#                : to establish credentials for the microservice user
#
#                : export AWS_ACCESS_KEY_ID=<<KEY>>
#                : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#                : export pgpass_migrationtest=<<DB_PASSWD>>
#
# Usage          : python redshift_counts.py <<config.json>>
#
# Configuration  : config file must be json and contain
#                   "bucket" : "bucket-name",
#                   "destination": "path/to/folder",
#                   "schema" : "webtrends",
#                   "profiles" : [ "dcsIDs-list" ]
#

import boto3 # s3 access
import pandas as pd # data processing
import re # regular expressions
from io import StringIO
from io import BytesIO
import os # to read environment variables
import psycopg2 # to connect to Redshift
import numpy as np # to handle numbers
import csv # read input and write results as
import json # to read json config files
import sys # to read command line parameters
import os.path #file handling

# set up debugging
debug = False
def log(s):
    if debug:
        print s

# Read configuration file
if (len(sys.argv) != 2 ): #will be 1 if no arguments, 2 if one argument
    print "Usage: python s3_to_redshift.py <<config.json>>"
    sys.exit(1)
configfile = sys.argv[1]
if (os.path.isfile(configfile) == False): # confirm that the file exists
    print "Invalid file name " + configfile
    sys.exit(1)
with open(configfile) as f:
    data = json.load(f)

# acquire properties from configuration file
conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=os.environ['pguser_migrationtest'],
           password=os.environ['pgpass_migrationtest'])

profiles = data['profiles']
output_bucket = data['output_bucket']
destination = data['destination']
schema = data['schema']
table = data['table']

# model an empty data result for error handling null data responses
empty_data = {
    '2016-01':'0',
    '2016-02':'0',
    '2016-03':'0',
    '2016-04':'0',
    '2016-05':'0',
    '2016-06':'0',
    '2016-07':'0',
    '2016-08':'0',
    '2016-09':'0',
    '2016-10':'0',
    '2016-11':'0',
    '2016-12':'0',
    '2017-01':'0',
    '2017-02':'0',
    '2017-03':'0',
    '2017-04':'0',
    '2017-05':'0',
    '2017-06':'0',
    '2017-07':'0',
    '2017-08':'0',
    '2017-09':'0',
    '2017-10':'0',
    '2017-11':'0',
    '2017-12':'0',
}

# Iteration Testing Step 5 pre-formatted queries
queries = {
    '1A - Rows in Redshift':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', {table}.date ), 'YYYY-MM') AS "{table}.date_month",
        COUNT(*) AS "{table}.count"
    FROM webtrends.{table}  AS {table}

    WHERE
            ({table}.dcs_id = '{dcsid}')
    GROUP BY 1,DATE_TRUNC('month', {table}.date )
    ORDER BY 2
    """,
    '2A - Page View Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', {table}.date ), 'YYYY-MM') AS "{table}.date_month",
        COUNT(*) AS "{table}.count"
    FROM webtrends.{table}  AS {table}

    WHERE ({table}.dcs_id = '{dcsid}') AND ({table}.wt_dl = '0')
    GROUP BY 1,DATE_TRUNC('month', {table}.date )
    ORDER BY 2
    """,
    '2B - Offsite Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', {table}.date ), 'YYYY-MM') AS "{table}.date_month",
        COUNT(*) AS "{table}.count"
    FROM webtrends.{table}  AS {table}

    WHERE ({table}.dcs_id = '{dcsid}') AND ({table}.wt_dl = '24')
    GROUP BY 1,DATE_TRUNC('month', {table}.date )
    ORDER BY 2
    """,
    '2C - Download Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', {table}.date ), 'YYYY-MM') AS "{table}.date_month",
        COUNT(*) AS "{table}.count"
    FROM webtrends.{table}  AS {table}

    WHERE ({table}.dcs_id = '{dcsid}') AND ({table}.wt_dl = '20')
    GROUP BY 1,DATE_TRUNC('month', {table}.date )
    ORDER BY 2
    """,
    '2D - Miscellaneous Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', {table}.date ), 'YYYY-MM') AS "{table}.date_month",
        COUNT(*) AS "{table}.count"
    FROM webtrends.{table}  AS {table}

    WHERE ({table}.dcs_id = '{dcsid}') AND (({table}.wt_dl  NOT IN ('24', '0', '20') OR {table}.wt_dl IS NULL))
    GROUP BY 1,DATE_TRUNC('month', {table}.date )
    ORDER BY 2
    """,
    '3A - Visitor Sessions in Redshift':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', {table}.date ), 'YYYY-MM') AS "{table}.date_month",
        COUNT(DISTINCT {table}.wt_vt_sid ) AS "{table}.session_count"
    FROM webtrends.{table}  AS {table}

    WHERE
        ({table}.dcs_id = '{dcsid}')
    GROUP BY 1,DATE_TRUNC('month', {table}.date )
    ORDER BY 2
    """
}

# set up S3 connection
client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
output_bucket = resource.Bucket(output_bucket) #subsitute this for your s3 bucket name.


# prep database call to pull the batch file into redshift
with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        curs.execute("SET search_path TO " + schema) # specify the schema
        for dcsid in profiles:
            result = pd.DataFrame()
            for header,query in queries.items():
                query = query.format(dcsid=dcsid, table=table) # formats each SQL queries
                log(query)
                try:
                    curs.execute(query) # try to run the formatted query
                except psycopg2.Error as e: # if the DB call fails, print error and place file in /bad
                    log("Execution {0} failed\n\n".format(header))
                    log(e.pgerror)
                else:
                    log("Execution {0} successful\n\n".format(header))

                try:
                    data = np.array(curs.fetchall())
                except  psycopg2.ProgrammingError as e: # the query did not produce a result set
                    log("No result set from query execution {0}\n\n".format(header))
                    log(e.pgerror)
                else: # there was a query result
                    #TODO: handle if the data is empty
                    if data.size is 0:
                        log("Result set {0} was empty\n\n".format(header))
                        data=empty_data
                    df = pd.DataFrame(data, columns=['0',header]) # make a dataframe of the query result
                    if not result.empty:
                        result = pd.merge(result,df,how='outer',on=['0']) # merge this dataframe with the existing results
                    else:
                        result = df # the first query with a result set will initialize the result

            if not result.empty:
                # keeps session column leftmost while reindexes the remaining results dataframe lexically,
                # and in descending session chronology on rows
                result = result.sort_values(by=['0']).sort_index(axis=1).rename(columns={'0': 'session'}).reset_index(drop=True)

                # save the results as a csv into S3
                csv_buffer = BytesIO()
                result.to_csv(csv_buffer, header=True, index=False, sep=",")
                output_bucket.put_object(Key="{0}/{1}.csv".format(destination,dcsid), Body=csv_buffer.getvalue())
