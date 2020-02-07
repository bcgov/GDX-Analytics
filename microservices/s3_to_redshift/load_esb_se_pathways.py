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

import boto3  # s3 access
from botocore.exceptions import ClientError
import pandas as pd  # data processing
import re  # regular expressions
from io import StringIO
import os  # to read environment variables
import psycopg2  # to connect to Redshift
import json  # to read json config files
import sys  # to read command line parameters
import os.path  # file handling
import logging


# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create stdout handler for logs at the INFO level
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# create file handler for logs at the DEBUG level in /logs/s3_to_redshift.log
log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
handler = logging.FileHandler(os.path.join('logs', log_filename), "a",
                              encoding=None, delay="true")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Take one argument: bucketname
if (len(sys.argv) != 2):
    print "Usage: python load_esb_se_pathways.py bucketname"
    sys.exit(1)
bucket = sys.argv[1]

source = 'brendan_test'
filename = 'se_pathways.csv'

# set up S3 connection
client = boto3.client('s3')  # low-level functional API
resource = boto3.resource('s3')  # high-level object-oriented API
my_bucket = resource.Bucket(bucket)  # subsitute this for your s3 bucket name.
key = ''

# find the latest file matching filename se_pathways.csv
for object_summary in sorted(my_bucket.objects.filter(Prefix=source),key=attrgetter('last_modified'),reverse=True):
    if re.search(filename, object_summary.key):
        logger.info('\nhttps://s3.console.aws.amazon.com/s3/object/sp-ca-bc-gov-131565110619-12-microservices/'
                    + object_summary.key
                    + '\n' + object_summary.last_modified
                    + '\n---')
        key = object_summary.key
        break

obj = client.get_object(Bucket=bucket, Key=object_summary.key)
body = obj['Body']
query = body.read().decode('utf-8')

# prep database call to pull the batch file into redshift
conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=os.environ['pguser'],
           password=os.environ['pgpass'])

with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        except psycopg2.Error as e: # if the DB call fails, print error and place file in /bad
            logger.exception("Loading failed\n{0}".format(e.pgerror))
        else:
            logger.info("Loaded successfully")

