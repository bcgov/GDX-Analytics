###################################################################
# Script Name   : s3_to_sfts.py
#
# Description   : Uploads previously un-loaded objects from a location on S3
#               : to a location on the SFTS system.
#
# Requirements  : the XFer java client tool must be extracted into a path
#               : available to the executing environment.
#               :
#               : You must set the following environment variables:
#
#               : export sfts_user=<<sfts_service_account_username>>
#               : export sfts_pass=<<sfts_service_account_password>>
#               : export xfer_path=<</path/to/xfer/jar/files/>>
#
# Usage         : python s3_to_sfts.py -c config.d/config.json
#
# XFer          : Download the XFer jar files as "Client Tools Zip" from:
# https://community.ipswitch.com/s/article/Direct-Download-Links-for-Transfer-and-Automation-2018

import os
import sys
import shutil
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
prefix = source + "/" + directory + "/"
destination = config['destination']
object_prefix = config['object_prefix']
sfts_path = config['sfts_path']
extension = config['extension']

# Get required environment variables
sfts_user = os.environ['sfts_user']
sfts_pass = os.environ['sfts_pass']
xfer_path = os.environ['xfer_path']

# set up S3 connection
client = boto3.client('s3')  # low-level functional API
resource = boto3.resource('s3')  # high-level object-oriented API
my_bucket = resource.Bucket(bucket)  # subsitute this for your s3 bucket name.
bucket_name = my_bucket.name


def download_object(o):
    dl_name = o.replace(prefix, '')
    try:
        my_bucket.download_file(o, './tmp/{0}{1}'.format(dl_name, extension))
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.error("The object does not exist.")
            logger.debug("ClientError 404: {}".format(e))
        else:
            raise


# Check to see if the file has been processed already
def is_processed(object_summary):
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
# filenames example: pmrp_YYYYMMDD_YYYYMMDD_YYYYMMDDTHH:MM:SS_part000
# where the first date is the query start date, the second date is the query
# end date, and the last timestamp is when the file was created.
filename_regex = (
    '^{object_prefix}_[0-9]{{4}}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])_'
    '[0-9]{{4}}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])_'
    '[0-9]{{4}}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])T'
    '(2[0-3]|[01][0-9])[0-5][0-9][0-6][0-9]_part[0-9]{{3}}$'
    .format(object_prefix=object_prefix))
objects_to_process = []
for object_summary in my_bucket.objects.filter(Prefix=prefix):
    key = object_summary.key
    goodfile = destination + "/good/" + object_summary.key
    badfile = destination + "/bad/" + object_summary.key
    filename = key[key.rfind('/')+1:]  # get the filename (after the last '/')
    # skip to next object if already processed
    if is_processed(key):
        continue
    else:
        if re.search(filename_regex, filename):
            objects_to_process.append(object_summary)
            logger.debug('added {} for processing'.format(filename))

if not objects_to_process:
    logger.debug('no files to process')
    sys.exit(1)

# downloads go to a temporary folder: ./tmp
if not os.path.exists('./tmp'):
    os.makedirs('./tmp')
for object in objects_to_process:
    download_object(object.key)

# Copy to SFTS
# write a file to use with the -s flag for the xfer.sh service
sfts_conf = './tmp/sfst_conf'
sf = open(sfts_conf, 'w')
sf_full_path = os.path.realpath(sf.name)
# switch to the writable directory
sf.write('cd {}\n'.format(sfts_path))
# write all file names downloaded in "A" in the objects_to_process list
for object in objects_to_process:
    transfer_file = './tmp/{0}{1}'.format(object.key.replace(prefix, ''), extension)
    sf.write('put {}\n'.format(transfer_file))
sf.write('quit\n')
sf.close()

logger.debug('file for xfer -s call is {}'.format(os.path.realpath(sf.name)))
with open(sfts_conf, 'r') as sf:
    logger.debug('Contents:\n{}'.format(sf.read()))
sf.close()

# as a subprocess pass the credentials and the sfile to run xfer in batch mode
# https://docs.ipswitch.com/MOVEit/Transfer2017Plus/FreelyXfer/MoveITXferManual.html
try:
    xfer_jar = "{}/xfer.jar".format(xfer_path)
    jna_jar = "{}/jna.jar".format(xfer_path)
    print("trying to call subprocess:\nxfer.jar: {}\njna.jar : {}".format(
        xfer_jar, jna_jar))
    subprocess.check_call(
        ["java", "-classpath", "{}:{}".format(xfer_jar, jna_jar), "xfer",
         "-user:{}".format(sfts_user),
         "-password:{}".format(sfts_pass),
         "-s:{}".format(sfts_conf),
         "filetransfer.gov.bc.ca"])
    outfile = goodfile
except subprocess.CalledProcessError as e:
    logger.error('Non-zero exit code calling XFer.')
    logger.debug('{}'.format(e))
    outfile = badfile

# copy the file to the outfile destination path
try:
    client.copy_object(
        Bucket=bucket,
        CopySource='{}/{}'.format(bucket, object_summary.key),
        Key=outfile)
except ClientError as e:
    logger.error('Exception copying object')
    logger.debug('{}'.format(e))

# Remove the temporary local files used to transfer
try:
    shutil.rmtree('./tmp')
except Exception as e:
    logger.error('Exception deleting temporary folder')
    logger.debug('{}'.format(e))
