###################################################################
# Script Name   : redshift_to_s3.py
#
# Description   : Creates an object in S3, the result of a query on Redshift
#               : defined by the DML file referenced in the configuration file.
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the pgpass user microservice
#
#               : export pguser=<<database_username>>
#               : export pgpass=<<database_password>>
#
# Usage         : python generate_prmp_csv.py config.json
#
import os
import psycopg2
import logging
import argparse
import json
from datetime import datetime

# Logging has two handlers: INFO to stdout and DEBUG to a file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
handler = logging.FileHandler(os.path.join('logs', log_filename),
                              "a", encoding=None, delay="true")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# Command line arguments
parser = argparse.ArgumentParser(
    description='GDX Analytics ETL utility for PRMP.')
parser.add_argument('-c', '--conf', help='Microservice configuration file.',)
parser.add_argument('-d', '--debug', help='Run in debug mode.',
                    action='store_true')
flags = parser.parse_args()

config = flags.conf

# Parse the CONFIG file as a json object and load its elements as variables
with open(config) as f:
    config = json.load(f)

object_prefix = config['object_prefix']
bucket = config['bucket']
s3_prefix = config['source'] + '/' + config['directory']
dml_file = config['dml']

# Get required environment variables
pguser = os.environ['pguser']
pgpass = os.environ['pgpass']

# AWS Redshift and S3 configuration
conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=pguser,
           password=pgpass)

nowtime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

# the _substantive_ query, one that users expect to see as output in S3.
# TODO: MAKE AS CONFIG
request_query = open('dml/{}'.format(dml_file), 'r').read()

# The UNLOAD query to support S3 loading direct from a Redshift query
# ref: https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html
query = '''
UNLOAD ('{request_query}')
TO 's3://{bucket}/{s3_prefix}/{object_prefix}_{nowtime}_part'
credentials 'aws_access_key_id={aws_access_key_id};\
aws_secret_access_key={aws_secret_access_key}'
PARALLEL OFF
'''.format(
    request_query=request_query,
    bucket=bucket,
    s3_prefix=s3_prefix,
    object_prefix=object_prefix,
    nowtime=nowtime,
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        except psycopg2.Error as e:
            logger.error(('Error: UNLOAD transaction on {dml_file} failed '
                          'See debug log for the Error output.'.format(
                                dml_file=dml_file)))
            logger.debug("psycopg2.Error: {}".format(e))
        else:
            logger.info((
                'Success processing UNLOAD transaction on {dml_file} to '
                '{s3_prefix} in bucket: {bucket}.'
                .format(
                    dml_file=dml_file,
                    bucket=bucket,
                    s3_prefix=s3_prefix,
                    object_prefix=object_prefix,
                    nowtime=nowtime)))
