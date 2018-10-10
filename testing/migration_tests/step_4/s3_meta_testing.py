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
# Usage         : python27 s3_meta_testing.py <<config.json>>

import boto3 # s3 access
import sys # to read command line parameters
import os # to read environment variables
import os.path #file handling
from io import BytesIO # to create buffers
import json # to read write json
import csv # to write csv files
import collections # to sort collections
from datetime import datetime # handle stripping string date to datetime objects

# check invocation
if (len(sys.argv) != 2): #will be 1 if no arguments, 2 if one argument
    print "Usage: python27 s3_file_count.py <<config.json>> "
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

# Set up variables from config file
input_bucket = data['input_bucket']
directory = data['directory'] # the S3 location of the input files
profiles = data['profiles']
date_start = data['read_date_from_byte'] # critical to determining date of a file
output_bucket = data['output_bucket']
destination = data['destination']

# set up S3 connection
client = boto3.client('s3') #low-level functional API
s3 = boto3.resource('s3') #high-level object-oriented API
input_bucket = s3.Bucket(input_bucket)   # bucket to read from
output_bucket = s3.Bucket(output_bucket) # bucket to write to

for profile in profiles:

    profile_s3_metadata = {} # the collection of files and events by YYYY-MM key
    profile_s3_exceptions = {profile:{}} # a list of exceptions by profile name
    empty_file_count = 0
    lastdate = None

    # enumerating so as to get a file count
    for i, object_summary in enumerate(input_bucket.objects.filter(Prefix=directory + "/" + profile + "/")):

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

    ### Write output to S3
    # write out the results for this profile
    with BytesIO() as csv_buffer:
        writer = csv.writer(csv_buffer)
        for key,value in profile_s3_metadata.iteritems():
            writer.writerow([key,value['files'],value['events']])
        output_bucket.put_object(Key="{0}/{1}.csv".format(destination,profile), Body=csv_buffer.getvalue())

    # write out exceptions for this profile
    with BytesIO() as json_buffer: # write the monthwise metadata to a buffer
        json.dump(profile_s3_exceptions, json_buffer, indent=4, sort_keys=True) # sort the output file for human readability
        output_bucket.put_object(Key="{0}/exceptions_{1}.json".format(destination,profile), Body=json_buffer.getvalue())
