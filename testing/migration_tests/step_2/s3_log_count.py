###################################################################
# Script Name   : s3_log_count.py
#
# Description   : counts the number of log files in an S3 bucket 
#               : with a file name matching 2016-01 through 2017-12
#               : anywhere. Allows filtering on the file name prefix
#
# Requirements  : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#
#
# Usage         : python s3_log_count.py <<bucket_name>> <<optional_path>>
#
# NOTE:         : At present, the script does no error handling. It 
#               : will die if it hits an error. 

import boto3 # s3 acces
import sys # to read command line parameters
import re # to bin file names by regex group
import collections # for dictionary sorting

# Read command line parameter
if (len(sys.argv) < 2): # will be 1 if no arguments, 2 if one argument
    print "Usage: python s3_log_count.py <<bucket_name>> <<optional_path>>"
    sys.exit(1)
bucket_name = sys.argv[1]
if (len(sys.argv) > 2): # if there are two arguments, set directory as well
    directory = sys.argv[2]
else: 
    directory = ""

client = boto3.client('s3') #low-level functional API
s3 = boto3.resource('s3') #high-level object-oriented API
bucket = s3.Bucket(bucket_name) #subsitute this for your s3 bucket name.

log_counts = {} # initializing log_counts keyed on 'YYYY-MM' to zero
for i in range(1,13):
    log_counts['2016-' + str(i).rjust(2,'0')] = 0
    log_counts['2017-' + str(i).rjust(2,'0')] = 0

# count filenames that match log_counts key by respective YYYY-MM regex match
for object_summary in bucket.objects.filter(Prefix=directory):
    m = re.search(r'(201[6-7]-(0[1-9]|1[0-2]))', object_summary.key)
    if bool(m):
        log_counts[m.group(0)] += 1

print 'SN/LK - Testing Iteration Step 2 - Uploading SDC logs to S3'
print ' '+ '-'*18
print " | SDC logs on S3 | "
print ' '+ '-'*18

# sort and output dictionary
log_counts = collections.OrderedDict(sorted(log_counts.items()))
for i in log_counts.iterkeys():
    print i + ': ' + str(log_counts[i])

print '==============='
print 'Total: ' + str(sum(log_counts.values()))