###################################################################
# Script Name   : s3_to_sfts.py
#
# Description   : Uploads previously un-loaded objects from a location on S3
#               : to a location on the SFTS system.
#
# Requirements  : You must set the following environment variable
#
#               : export sfts_user=<<sfts_service_account_username>>
#               : export sfts_pass=<<sfts_service_account_password>>
#
# Usage         : python s3_to_sfts.py config.json

import os
import boto3
from botocore.exceptions import ClientError
import re
import logging
import argparse
import json
import subprocess

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

bucket = config['bucket']
source = config['source']
directory = config['directory']
destination = config['destination']
dbtable = config['dbtable']
sfts_path = config['sfts_path']

# Get required environment variables
sfts_user = os.environ['sfts_user']
sfts_pass = os.environ['sfts_pass']

# set up S3 connection
client = boto3.client('s3')  # low-level functional API
resource = boto3.resource('s3')  # high-level object-oriented API
my_bucket = resource.Bucket(bucket)  # subsitute this for your s3 bucket name.
bucket_name = my_bucket.name


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
filename_regex = (
    '^{{dbtable}}_[0-9]{{2}}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])'
    'T(2[0-3]|[01][0-9]):[0-5][0-9]:[0-6][0-9]_part[0-9]{{3}}$'
    .format(dbtable=dbtable))
objects_to_process = []
for object_summary in my_bucket.objects.filter(Prefix=source + "/"
                                               + directory + "/"):
    key = object_summary.key
    # skip to next object if already processed
    if is_processed(object_summary):
        continue
    else:
        if re.search(filename_regex, key):
            objects_to_process.append(object_summary)

###
# TODO
###
# A: Download S3 files to local disk
# get the files from S3 and store them on the local volume

# B: Copy to SFTS
# write a -s file for the xfer.sh service
sfts_file = 'path/to/file'
# write the username and password as the first two lines
# write all file names downloaded in "A" in the objects_to_process list

# C: Download downloaded files and -s file from local disk
# delete the files.

subprocess.call(
    [('/home/microservice/MOVEit-Xfer/xfer.sh '
      '-user:{sfts_user} -password:{sfts_pass} -s {}'.format(
          sfts_user=sfts_user,
          sfts_pass=sfts_pass,
          sfts_file=sfts_file))])
