###################################################################
# Script Name   : countlines.py
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
# Usage         : python countlines.py <<bucketname>> <<optional path>>
#
# NOTE:         : At present, the script does no error handling. It 
#               : will die if it hits an error. 
version='0.1'
import boto3 # s3 acces
import sys # to read command line parameters

# Read command line parameter
if (len(sys.argv) < 2): # will be 1 if no arguments, 2 if one argument
    print "Usage: python countlines.py <<bucketname>> <<optional path>>"
    sys.exit(1)
bucket = sys.argv[1]
if (len(sys.argv) > 2): # if there are two arguments, set directory as well
    directory = sys.argv[2]
else: 
    directory = ""


client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
my_bucket = resource.Bucket(bucket) #subsitute this for your s3 bucket name.

for object_summary in my_bucket.objects.filter(Prefix=directory):
    file_contents = object_summary.get()["Body"].read()
    print object_summary.key + ": " + str(file_contents.count('\n'))
