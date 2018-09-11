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

conn_string = "dbname='snowplow' host='snowplow-ca-bc-gov-main-redshi-resredshiftcluster-13nmjtt8tcok7.c8s7belbz4fo.ca-central-1.redshift.amazonaws.com' port='5439' user='migrationtest' password=" + os.environ['pgpass_migrationtest']
profiles = data['profiles']
bucket_name = data['bucket']
destination = data['destination']

queries = {
    '1A - Rows in Redshift':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', events.date ), 'YYYY-MM') AS "events.date_month",
        COUNT(*) AS "events.count"
    FROM webtrends.events  AS events
        
    WHERE
            (events.dcs_id = '{0}')
    GROUP BY 1,DATE_TRUNC('month', events.date )
    ORDER BY 2
    """,
    '2A - Page View Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', events.date ), 'YYYY-MM') AS "events.date_month",
        COUNT(*) AS "events.count"
    FROM webtrends.events  AS events

    WHERE (events.dcs_id = '{0}') AND (events.wt_dl = '0')
    GROUP BY 1,DATE_TRUNC('month', events.date )
    ORDER BY 2
    """,
    '2B - Offsite Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', events.date ), 'YYYY-MM') AS "events.date_month",
        COUNT(*) AS "events.count"
    FROM webtrends.events  AS events

    WHERE (events.dcs_id = '{0}') AND (events.wt_dl = '24')
    GROUP BY 1,DATE_TRUNC('month', events.date )
    ORDER BY 2 
    """,
    '2C - Download Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', events.date ), 'YYYY-MM') AS "events.date_month",
        COUNT(*) AS "events.count"
    FROM webtrends.events  AS events

    WHERE (events.dcs_id = '{0}') AND (events.wt_dl = '20')
    GROUP BY 1,DATE_TRUNC('month', events.date )
    ORDER BY 2 
    """,
    '2D - Miscellaneous Events':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', events.date ), 'YYYY-MM') AS "events.date_month",
        COUNT(*) AS "events.count"
    FROM webtrends.events  AS events

    WHERE (events.dcs_id = '{0}') AND ((events.wt_dl  NOT IN ('24', '0', '20') OR events.wt_dl IS NULL))
    GROUP BY 1,DATE_TRUNC('month', events.date )
    ORDER BY 2 
    """,
    '3A - Visitor Sessions in Redshift':
    """
    SELECT
        TO_CHAR(DATE_TRUNC('month', events.date ), 'YYYY-MM') AS "events.date_month",
        COUNT(DISTINCT events.wt_vt_sid ) AS "events.session_count"
    FROM webtrends.events  AS events

    WHERE 
        (events.dcs_id = '{0}')
    GROUP BY 1,DATE_TRUNC('month', events.date )
    ORDER BY 2 
    """
}

# set up S3 connection
client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
bucket = resource.Bucket(bucket_name) #subsitute this for your s3 bucket name.


# prep database call to pull the batch file into redshift
with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        curs.execute("SET search_path TO " + data['schema'])
        for dcsid in profiles:
            result = pd.DataFrame()
            for header,query in queries.items():
                query = query.format(dcsid)
                log(query)
                try:
                    curs.execute(query)
                except psycopg2.Error as e: # if the DB call fails, print error and place file in /bad
                    log("Execution failed\n\n")
                    log(e.pgerror)
                else:
                    log("Execution successful\n\n")
                data = np.array(curs.fetchall())
                df = pd.DataFrame(data, columns=['0',header])
                if not result.empty:
                    result = pd.merge(result,df,how='outer',on=['0'])
                else:
                    result = df

            # reindexes a results dataframe ordered lexically on columns, and in descending session chronology on rows
            result = result.sort_values(by=['0']).sort_index(axis=1).rename(columns={'0': 'session'}).reset_index(drop=True)

            csv_buffer = BytesIO()
            result.to_csv(csv_buffer, header=True, index=False, sep=",")
            resource.Bucket(bucket_name).put_object(Key=destination + "/" + dcsid + "_step5.csv", Body=csv_buffer.getvalue())
