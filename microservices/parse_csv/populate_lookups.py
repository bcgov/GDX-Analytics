###################################################################
#Script Name    : s3_to_redshift.py
#
#Description    : Microservice script to load a csv file from s3
#               : and load it into Redshift
#
#Requirements   : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#               : export pgpass=<<DB_PASSWD>>
#
#
#Usage          : pip2 install -r requirements.txt
#               : python27 populate_lookups.py configfile.json
#

import boto3 # s3 access
import pandas as pd # data processing
import re # regular expressions
from io import StringIO
from io import BytesIO
import os # to read environment variables
import numpy as np # to handle numbers
import json # to read json config files
import sys # to read command line parameters
import os.path #file handling
import itertools

# set up debugging
debug = True
def log(s):
    if debug:
        print s

# Read configuration file
if (len(sys.argv) != 2): #will be 1 if no arguments, 2 if one argument
    print "Usage: python s3_to_redshift.py config.json"
    sys.exit(1)
configfile = sys.argv[1] 
if (os.path.isfile(configfile) == False): # confirm that the file exists
    print "Invalid file name " + configfile
    sys.exit(1)
with open(configfile) as f:
    data = json.load(f)

# Set up variables from config file
bucket = data['bucket']
source = data['source']
destination = data['destination']
directory = data['directory']
doc = data['doc']
dbschema = data['dbschema']
column_count = data['column_count']
columns_metadata = data['columns_metadata']
columns_lookup = data['columns_lookup']
delim = data['delim']
nested_delim = data['nested_delim']
truncate = data['truncate']
if 'dtype_dic_strings' in data:
    for fieldname in data['dtype_dic_strings']:
        dtype_dic[fieldname] = str

# TODO: use boto, load this csv from S3
# set up S3 connection
client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
my_bucket = resource.Bucket(bucket) #subsitute this for your s3 bucket name.

for object_summary in my_bucket.objects.filter(Prefix=source + "/" + directory + "/"):
    if re.search(doc + '$', object_summary.key):
        log('{0}:{1}'.format(my_bucket.name, object_summary.key))

        # Check to see if the file has been processed already
        batchfile = destination + "/batch/" + object_summary.key
        goodfile = destination + "/good/" + object_summary.key
        badfile = destination + "/bad/" + object_summary.key
        try:
            client.head_object(Bucket=bucket, Key=goodfile)
        except:
            True
        else:
            log("File processed already. Skip.\n\n")
            continue
        try:
            client.head_object(Bucket=bucket, Key=badfile)
        except:
            True
        else:
            log("File failed already. Skip.\n\n")
            continue
        log("File not already processed. Proceed.\n")

        obj = client.get_object(Bucket=bucket, Key=object_summary.key)
        body = obj['Body']
        csv_string = body.read().decode('utf-8')


        # Check for an empty file. If it's empty, accept it as good and move on
        try:
            df_0 = pd.read_csv(StringIO(csv_string), sep=delim, index_col=False, dtype = dtype_dic, usecols=range(column_count))
        except Exception as e: 
            if (str(e) == "No columns to parse from file"):
                log("Empty file, proceeding")
                outfile = goodfile
            else:
                print "Parse error: " + str(e) 
                outfile = badfile 
            client.copy_object(Bucket="sp-ca-bc-gov-131565110619-12-microservices", CopySource="sp-ca-bc-gov-131565110619-12-microservices/"+object_summary.key, Key=goodfile)
            continue


        df = df_0.copy()
        # TODO: Loop on known pipe separated value columns, e.g., ancestor node (below)
        for column in columns_lookup:
            a= df.dropna(subset = [column])[column] # drop NANs from column "ancesor nodes"
            b=a.str[1:-1] # drop the proceeding and preceding nested delimeter
            c= b.str.split(nested_delim).values.flatten() # split on the nested delimeter, then flatten to a list
            d = list(set(itertools.chain.from_iterable(c))) # get unique elements by making a set, then back to a list
            for i in d:
                print i
                # TODO: copy to redshift table