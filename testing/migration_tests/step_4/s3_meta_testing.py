###################################################################
# Script Name   : s3_meta_testing.py
#
# Description   : counts the number of dcsID log events in a Spark
#               : migrated collection of dcsID logs on S3, emitting
#               : JSON files for each dscID separating monthly sub-
#               : totals over 2016 and 2017. 
#
# Configuration : the JSON configuartion schema, by key-values desc:
#               : : bucket - the S3 bucket sting
#               : : directoy - a parent directory to the profiles
#               : : profiles - a list of dscID strings
#               : : read_date_from_byte - a number representing the
#               : :   datetime start index on all logs' first line
#
# Requirements  : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#
# Usage         : python27 s3_meta_testing.py <<config.json>> [output_path]

import boto3 # s3 acces
import sys # to read command line parameters
import os # to read environment variables
import os.path #file handling
import json # to read json config files
import csv # to write csv files
import collections # to sort collections
from datetime import datetime # handle stripping string date to datetime objects

# check invocation
if (len(sys.argv) not in [2,3]): #will be 1 if no arguments, 2 if one argument
    print "Usage: python27 s3_file_count.py <<config.json>> [output_path]"
    sys.exit(1)
# Read configuration file
configFile = sys.argv[1] 
if (os.path.isfile(configFile) == False): # confirm that the file exists
    print "Invalid file name " + configFile
    sys.exit(1)
if (configFile.endswith('.json') == False): # confirm the file is of json
    print "Invalid file type " + configFile
    sys.exit(1)
with open(configFile) as f:
    data = json.load(f)

# set the output folder, creating if it doesn't exist
if len(sys.argv) == 3:
    out = sys.argv[2] + '/'   # add trailing / to path
    while out.endswith('//'): # leave only one trailing /
        out = out[:-1]
else:
    out = './' # default to current path

try:
    os.mkdir(out)
except:
    if not os.path.isdir(out):
        raise

# Set up variables from config file
bucket_name = data['bucket']
directory = data['directory']
profiles = data['profiles']
date_start = data['read_date_from_byte']

# set up S3 connection
client = boto3.client('s3') #low-level functional API
s3 = boto3.resource('s3') #high-level object-oriented API
bucket = s3.Bucket(bucket_name) #subsitute this for your s3 bucket name.

for profile in profiles:

    profile_s3_metadata = {} # the collection of files and events by YYYY-MM key
    profile_s3_exceptions = {profile:{}} # a list of exceptions by profile name
    empty_file_count = 0
    lastdate = None

    # enumerating so as to get a file count
    for i, object_summary in enumerate(bucket.objects.filter(Prefix=directory + "/" + profile + "/")):

        # log any empty files and files with exceptions to the expected format, and skip over them
        if object_summary.size == 0: # report on empty files
            profile_s3_exceptions[profile].setdefault('empty_file_keys',[]).append(object_summary.key)
            continue # skip this iteration if there was nothing in the file
        date_string = object_summary.get()["Body"].read(date_start+ 10)[date_start:] #YYYY-MM-DD is 10 bytes
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')
        except:
            profile_s3_exceptions[profile].setdefault('exception_file_keys',[]).append(object_summary.key)
            continue # skip this iteration if datetime read had discrepantices from an expected datetime

        key = str(date.year) + "-" + str(date.month).zfill(2)                       # key this session as 'YYYY-MM'

        file_contents = object_summary.get()["Body"].read()                         # read the entire file
        event_count = (file_contents.count('\n'))                                   # count each new line as an event

        if key in profile_s3_metadata:
            profile_s3_metadata[key]['files'] += 1                                  # increment the file count (unpacked)
            profile_s3_metadata[key]['events'] += event_count                       # and the event count
        else:
            profile_s3_metadata[key]={'files':1, 'events':event_count}              # log that there is a new key

    # report counts on all empty file keys and exception file keys
    if 'empty_file_keys' in profile_s3_exceptions[profile]:
        profile_s3_exceptions[profile]['empty_file_count'] = len(profile_s3_exceptions[profile]['empty_file_keys'])
    if 'exception_file_keys' in profile_s3_exceptions[profile]:
        profile_s3_exceptions[profile]['exception_file_count'] = len(profile_s3_exceptions[profile]['exception_file_keys'])

    profile_s3_metadata = collections.OrderedDict(sorted(profile_s3_metadata.items()))

    # write out the csv for this profile
    with open('{0}{1}.csv'.format(out,profile), 'w') as fp:          # open a new file to write the monthwise metadata to
        writer = csv.writer(fp)
        for key,value in profile_s3_metadata.iteritems():
            writer.writerow([key,value['files'],value['events']])

    # write out exceptions for this profile
    with open('{0}exceptions_{1}.json'.format(out,profile), 'w') as fp: # open a new file to write the monthwise metadata to
        json.dump(profile_s3_exceptions, fp, indent=4, sort_keys=True)              # sort the output file for easy reading
