###################################################################
# Script Name   : load_esb_se_pathways.py
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
# Usage         : python load_esb_se_pathways.py bucketname
#

import os  # to read environment variables
import psycopg2  # to connect to Redshift
import sys  # to read command line parameters


# Take one argument: bucketname
if (len(sys.argv) != 2):
    print "Usage: python load_esb_se_pathways.py bucketname"
    sys.exit(1)
bucket_name = sys.argv[1]

filename = 'se_pathways.csv'
dbtable = 'esb.se_pathways'
aws_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']

# Constructs the database copy query string
query = """ COPY {0}\nFROM 's3://{1}/{2}'\n\
    CREDENTIALS 'aws_access_key_id={3};aws_secret_access_key={4}' CSV;\n
    """.format(dbtable, bucket_name, filename, aws_key, aws_secret_key)

# Database connection string
conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=os.environ['pguser'],
           password=os.environ['pgpass'])

# Execute the transaction against Redshift using the psycopg2 library
with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        # if the DB call fails, print error msg
        except psycopg2.Error as e:
            print ("Loading {0} to RedShift failed\n{1}"
                   .format(filename, e.pgerror))
        # if the DB call succeeds, print success msg
        else:
            print ("Loaded {0} to RedShift successfully"
                   .format(filename))
