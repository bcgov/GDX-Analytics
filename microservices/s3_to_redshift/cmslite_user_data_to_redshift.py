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
import re  # regular expressions
from io import StringIO
import os  # to read environment variables
import psycopg2  # to connect to Redshift
import json  # to read json config files
import sys  # to read command line parameters
import os.path  # file handling
import logging
import tarfile


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

# check that configuration file was passed as argument
if (len(sys.argv) != 2):
    print('Usage: python cmslite_user_data_to_redshift.py config.json')
    sys.exit(1)
configfile = sys.argv[1]
# confirm that the file exists
if os.path.isfile(configfile) is False:
    print("Invalid file name {}".format(configfile))
    sys.exit(1)
# open the confifile for reading
with open(configfile) as f:
    data = json.load(f)

bucket = data['bucket']
source = data['source']
destination = data['destination']
directory = data['directory']
prefix = source + "/" + directory + "/"
doc = data['doc']
truncate = data['truncate']

# set up S3 connection
client = boto3.client('s3')  # low-level functional API
resource = boto3.resource('s3')  # high-level object-oriented API
bucket = resource.Bucket(bucket)  # subsitute this for your s3 bucket name.
bucket_name = bucket.name


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
# Download the tgz file, unpack it to a temp folder in the local working
# directory, process the files, and then shift the data to redshift. Finally,
# delete the temp folder. 

# downloads go to a temporary folder: ./tmp
if not os.path.exists('./tmp'):
    os.makedirs('./tmp')
for obj in objects_to_process:
    download_object(obj.key)
