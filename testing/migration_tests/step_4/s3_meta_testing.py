###################################################################
# Script Name   : s3_meta_testing.py
#
# Description   : counts the number of lines of  objects in an S3
#               : bucket 
#
# Requirements  : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#
#
# Usage         : python27 s3_meta_testing.py <<log_load.json>>

import boto3 # s3 acces
import sys # to read command line parameters
import os # to read environment variables
import os.path #file handling
import json # to read json config files
from datetime import datetime # handle stripping string date to datetime objects

# Read configuration file
if (len(sys.argv) != 2): #will be 1 if no arguments, 2 if one argument
    print "Usage: python27 s3_file_count.py <<log_load.json>>"
    sys.exit(1)
configfile = sys.argv[1] 
if (os.path.isfile(configfile) == False): # confirm that the file exists
    print "Invalid file name " + configfile
    sys.exit(1)
with open(configfile) as f:
    data = json.load(f)

# Set up variables from config file
bucket = data['bucket']
directory = data['directory']
profiles = data['profiles']
date_start = data['read_date_from_byte']

# set up S3 connection
client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
s3 = resource.Bucket(bucket) #subsitute this for your s3 bucket name.

for profile in profiles:

    profile_s3_metadata = {}
    profile_s3_exceptions = {profile:{}}
    empty_file_count = 0
    lastdate = None

    # enumerating so as to get a file count
    for i, object_summary in enumerate(s3.objects.filter(Prefix=directory + "/" + profile + "/")):

        # log any empty files and files with exceptions to the expected format, and skip over them
        if object_summary.size == 0:
            profile_s3_exceptions[profile].setdefault('empty_file_keys',[]).append(object_summary.key)
            continue
        date_string = object_summary.get()["Body"].read(date_start+ 10)[date_start:]
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
        except:
            profile_s3_exceptions[profile].setdefault('exception_file_keys',[]).append(object_summary.key)
            continue

        key = str(date.year) + "-" + str(date.month).zfill(2)                       # key this session as 'YYYY-MM'

        file_contents = object_summary.get()["Body"].read()                         # read the entire file
        event_count = (file_contents.count('\n'))                                   # each new line is an event

        if key in profile_s3_metadata:
            profile_s3_metadata[key]['files'] += 1
            profile_s3_metadata[key]['events'] += event_count
        else:
            profile_s3_metadata[key]={'files':1, 'events':event_count}              # log that there is a new key

    if 'empty_file_keys' in profile_s3_exceptions[profile]:
        profile_s3_exceptions[profile]['empty_file_count'] = len(profile_s3_exceptions[profile]['empty_file_keys'])
    if 'exception_file_keys' in profile_s3_exceptions[profile]:
        profile_s3_exceptions[profile]['exception_file_count'] = len(profile_s3_exceptions[profile]['exception_file_keys'])

    try:
        os.makedirs('./out/{0}'.format(directory))
    except:
        if not os.path.isdir('./out/{0}'.format(directory)):
            raise

    with open('out/{0}/{1}.json'.format(directory, profile), 'w') as fp:            # open a new file to write the monthwise metadata to
        json.dump(profile_s3_metadata, fp, indent=4, sort_keys=True)                # sort the output file for easy reading

    with open('out/{0}/exceptions_{1}.json'.format(directory, profile), 'w') as fp: # open a new file to write the monthwise metadata to
        json.dump(profile_s3_exceptions, fp, indent=4, sort_keys=True)              # sort the output file for easy reading


