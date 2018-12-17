###################################################################
#Script Name    : s3_encryption_checker.py
#
#Description    : A script to find any unencrypted S3 objects
#
#Requirements   : You must set the following environment variables
#               : to establish credentials for the S3 user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#
#Usage          : python s3_encryption_checker.py bucket
import boto3 # S3 access
import sys # to read command line parameters

# Read configuration file
if (len(sys.argv) != 2): #will be 1 if no arguments, 2 if one argument
    print "python s3_encryption_checker.py bucket"
    sys.exit(1)
bucket = sys.argv[1]

# set up S3 connection
client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
my_bucket = resource.Bucket(bucket)

for object_summary in my_bucket.objects.filter():
    try:
        head = client.head_object(Bucket=bucket, Key=object_summary.key)
    except Exception as e:
        print "Error on " + bucket + "/" + object_summary.key + ": " +  str(e)

    if 'ServerSideEncryption' not in head:
        print bucket + "/" + object_summary.key + " is not encrypted"
