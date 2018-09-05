###################################################################
#Script Name    : redshift_counts.py
#
#Description    : Counts the rows, events, visit
#               : and load it into Redshift
#
#Requirements   : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#               : export pgpass=<<DB_PASSWD>>
#
#
#Usage          : python s3_to_redshift.py <<config.json>>
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
debug = True
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

queries = [
    """
    SELECT 
        events.dcs_id  AS "events.dcs_id",
        TO_CHAR(DATE_TRUNC('month', events.date ), 'YYYY-MM') AS "events.date_month",
        COUNT(*) AS "events.count"
    FROM webtrends.events  AS events
        
    WHERE
            (events.dcs_id = '{0}')
    GROUP BY 1,DATE_TRUNC('month', events.date )
    ORDER BY 2
    LIMIT 500
    """,
    ]

# prep database call to pull the batch file into redshift
with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        curs.execute("SET search_path TO " + data['schema'])
        for dcsid in profiles:
            for query in queries:
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
                df = pd.DataFrame(data)
                df.to_csv(dcsid + '.csv', encoding='utf-8')
