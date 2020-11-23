"""Uploads objects from S3 to the SFTS system."""
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
import re
import logging
import argparse
import json
import subprocess
import boto3
from botocore.exceptions import ClientError
import lib.logs as log

logger = logging.getLogger(__name__)
log.setup()


def clean_exit(code, message):
    """Exits with a logger message and code"""
    logger.info('Exiting with code %s : %s', str(code), message)
    sys.exit(code)


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

config_bucket = config['bucket']
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
res_bucket = resource.Bucket(config_bucket)  # resource bucket object
bucket_name = res_bucket.name


def download_object(o):
    '''downloads object to a tmp directoy'''
    dl_name = o.replace(prefix, '')
    try:
        res_bucket.download_file(o, './tmp/{0}{1}'.format(dl_name, extension))
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.error("The object %s does not exist.", dl_name)
            logger.exception("ClientError 404:")
            clean_exit(1, 'Expected object is missing on S3.')
        else:
            raise


def is_processed():
    '''Check to see if the file has been processed already'''
    try:
        client.head_object(Bucket=config_bucket, Key=goodfile)
    except ClientError:
        pass  # this object does not exist under the good destination path
    else:
        logger.debug("%s was processed as good already.", filename)
        return True
    try:
        client.head_object(Bucket=config_bucket, Key=badfile)
    except ClientError:
        pass  # this object does not exist under the bad destination path
    else:
        logger.debug("%s was processed as bad already.", filename)
        return True
    logger.debug("%s has not been processed.", filename)
    return False


# This bucket scan will find unprocessed objects matching on the object prefix
# objects_to_process will contain zero or one objects if truncate = True
# objects_to_process will contain zero or more objects if truncate = False
filename_regex = fr'^{object_prefix}'
objects_to_process = []
for object_summary in res_bucket.objects.filter(Prefix=prefix):
    key = object_summary.key
    filename = key[key.rfind('/')+1:]  # get the filename (after the last '/')
    goodfile = f"{destination}/good/{key}"
    badfile = f"{destination}/bad/{key}"
    # skip to next object if already processed
    if is_processed():
        continue
    if re.search(filename_regex, filename):
        objects_to_process.append(object_summary)
        logger.debug('added %a for processing', filename)

if not objects_to_process:
    clean_exit(1, 'Failing due to no files to process')

# downloads go to a temporary folder: ./tmp
if not os.path.exists('./tmp'):
    os.makedirs('./tmp')
for obj in objects_to_process:
    download_object(obj.key)

# Copy to SFTS
# write a file to use with the -s flag for the xfer.sh service
sfts_conf = './tmp/sfst_conf'
sf = open(sfts_conf, 'w')
sf_full_path = os.path.realpath(sf.name)
# switch to the writable directory
sf.write('cd {}\n'.format(sfts_path))
# write all file names downloaded in "A" in the objects_to_process list
for obj in objects_to_process:
    transfer_file = f"./tmp/{obj.key.replace(prefix, '')}{extension}"
    sf.write('put {}\n'.format(transfer_file))
sf.write('quit\n')
sf.close()

logger.debug('file for xfer -s call is %s', os.path.realpath(sf.name))
with open(sfts_conf, 'r') as sf:
    logger.debug('Contents:\n%s', sf.read())
sf.close()

# as a subprocess pass the credentials and the sfile to run xfer in batch mode
# https://docs.ipswitch.com/MOVEit/Transfer2017Plus/FreelyXfer/MoveITXferManual.html
# TODO: do uploads one at a time and treat them on S3 one-by-one
try:
    xfer_jar = f"{xfer_path}/xfer.jar"
    jna_jar = f"{xfer_path}/jna.jar"
    print(("trying to call subprocess:\nxfer.jar: "
           f"{xfer_jar}\njna.jar : {jna_jar}"))
    subprocess.check_call(
        ["java", "-classpath", f"{xfer_jar}:{jna_jar}",
         "xfer",
         f"-user:{sfts_user}",
         f"-password:{sfts_pass}",
         f"-s:{sfts_conf}",
         "filetransfer.gov.bc.ca"])
    xfer_proc = True
except subprocess.CalledProcessError:
    logger.exception('Non-zero exit code calling XFer:')
    xfer_proc = False

# copy the processed files to their outfile destination path
for obj in objects_to_process:
    key = obj.key
    # TODO: check SFTS endpoint to determine which files reached SFTS
    # currently it's all based on whether or not the XFER call returned 0 or 1
    if xfer_proc:
        outfile = f"{destination}/good/{key}"
    else:
        outfile = f"{destination}/bad/{key}"
    try:
        client.copy_object(
            Bucket=config_bucket,
            CopySource='{}/{}'.format(config_bucket, obj.key),
            Key=outfile)
    except ClientError:
        logger.exception('Exception copying object %s', obj.key)
    else:
        logger.debug('copied %s to %s', obj.key, outfile)

# Remove the temporary local files used to transfer
try:
    shutil.rmtree('./tmp')
except (os.error, OSError):
    logger.exception('Exception deleting temporary folder:')
    clean_exit(1,'Could not delete tmp folder')

if xfer_proc:
    clean_exit(0,'Finished successfully.')
clean_exit(1, 'Finished with a subroutine error.')
