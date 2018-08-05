###################################################################
# Script Name   : s3_meta_testing.py
# Version       : 0.1 
#
# Description   : Quick script that counts the number of lines of 
#               : objects in an S3 bucket 
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

    event_count = 0
    empty_file_count = 0
    files = 0
    monthly_counts = []
    monthly_events = []

    lastdate = None

    # enumerating so as to get a file count
    for i, object_summary in enumerate(s3.objects.filter(Prefix=directory + "/" + profile + "/")):
        if object_summary.size == 0:
            empty_file_count += 1                                               # only one empty file, "_SUCCESS", should exist in path
            profile_s3_metadata['empty_file_count'] = empty_file_count          # track the empty files count
            profile_s3_metadata.setdefault('empty_file_keys',[]).append(object_summary.key) # and keynames for later debugging
            continue                                                            # skip this loop if the file is empty
        date_string = object_summary.get()["Body"].read(date_start+ 10)[date_start:] # read the 10 byte date string
        try:
            date = datetime.strptime(date_string, '%Y-%m-%d')                   # handle the date string as a datetime object
        except:                                                                 # tracks lines that don't conform to expected format
            profile_s3_metadata.setdefault('exception_file_keys',[]).append(object_summary.key)
            continue                                                            # skip the misformatted file

        if lastdate:    
            if lastdate.month != date.month:                                    # every new month
                monthly_counts.append(files)                                    # append that last months' count to the month count list
                monthly_events = []                                             # reset the monthly events count list
            files = 1 + i - sum(monthly_counts) - empty_file_count              # grows with index, left offset from sum of past monthly counts

        file_contents = object_summary.get()["Body"].read()                     # read the entire file
        monthly_events.append(file_contents.count('\n'))                        # to count the newlines as events, storing that value

        key   = str(date.year) + "-" + str(date.month).zfill(2)                 # keying on YYYY-MM
        value = {'files': files, 'events':sum(monthly_events)}                  # create the entry as a dictionary containing files and events
        profile_s3_metadata[key] = value                                        # update the existing entry, or create new entry on new month

        lastdate = date                                                         # before next iteration, reset the lastdate to this date

    try:
        os.makedirs('./out/{0}'.format(directory))
    except:
        if not os.path.isdir('./out/{0}'.format(directory)):
            raise

    with open('out/{0}/{1}.json'.format(directory, profile), 'w') as fp:        # open a new file to write the monthwise metadata to
        json.dump(profile_s3_metadata, fp, indent=4, sort_keys=True)            # sort the output file for easy reading
