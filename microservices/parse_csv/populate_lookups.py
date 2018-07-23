###################################################################
#Script Name    : populate_lookups.py
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
import psycopg2 # to connect to Redshift
import numpy as np # to handle numbers
import json # to read json config files
import sys # to read command line parameters
import os.path #file handling
import itertools
import string #string functions

# set up debugging
debug = True
def log(s):
    if debug:
        print s

# define a function to output a dataframe to a CSV on S3
def to_s3(bucket, batchfile, filename, df, columnlist = None):
    # Put the full data set into a buffer and write it to a "   " delimited file in the batch directory
    csv_buffer = BytesIO()
    if (columnlist is None):
        df.to_csv(csv_buffer, header=True, index=False, sep="	")
    elif (columnlist == "key"):
        df.to_csv(csv_buffer, header=True, index=True, sep="	", index_label="key")
    else:
        df.to_csv(csv_buffer, header=True, index=False, sep="	", columns=columnlist)

    log("Writing " + filename + " to " + batchfile)
    resource.Bucket(bucket).put_object(Key=batchfile + "/" + filename, Body=csv_buffer.getvalue())


# Read configuration file
if (len(sys.argv) != 2): #will be 1 if no arguments, 2 if one argument
    print "Usage: python27 populate_lookups.py configfile.json"
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
dbtable = data['dbtable']

column_count = data['column_count']
columns_metadata = data['columns_metadata']
columns_lookup = data['columns_lookup']
dbtables_dictionaries = data['dbtables_dictionaries']
dbtables_metadata = data['dbtables_metadata']
nested_delim = data['nested_delim']
columns = data['columns']
dtype_dic = {}
if 'dtype_dic_strings' in data:
    for fieldname in data['dtype_dic_strings']:
        dtype_dic[fieldname] = str
delim = data['delim']
truncate = data['truncate']

# set up S3 connection
client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
my_bucket = resource.Bucket(bucket) #subsitute this for your s3 bucket name.

for object_summary in my_bucket.objects.filter(Prefix=source + "/" + directory + "/"):
    if re.search(doc + '$', object_summary.key):
        log('{0}:{1}'.format(my_bucket.name, object_summary.key))

        # Check to see if the file has been processed already
        batchfile = destination + "/batch/" + object_summary.key
        goodfile = destination + "/good_XYZ/" + object_summary.key
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
        # We have hard coded the encoding here to 'iso-8859-1' as that seems to be the encoding provided. We should confirm. 
        csv_string = body.read().decode('iso-8859-1')

        # temporary fix while we figure out better delimiter handling
        csv_string = csv_string.replace('	',' ')

        # Check for an empty file. If it's empty, accept it as good and move on
        try:
            df = pd.read_csv(StringIO(csv_string), sep=delim, index_col=False, dtype = dtype_dic, usecols=range(column_count))
        except Exception as e: 
            if (str(e) == "No columns to parse from file"):
                log("Empty file, proceeding")
                outfile = goodfile
            else:
                print "Parse error: " + str(e) 
                outfile = badfile 
            client.copy_object(Bucket="sp-ca-bc-gov-131565110619-12-microservices", CopySource="sp-ca-bc-gov-131565110619-12-microservices/"+object_summary.key, Key=goodfile)
            continue

        df.columns = columns

        # Run replace on some fields to clean the data up 
        if 'replace' in data:
            for thisfield in data['replace']:
                df[thisfield['field']].replace (thisfield['old'], thisfield['new'])

        # Clean up date fields
        # for each field listed in the dateformat array named "field" apply "format"
        if 'dateformat' in data:
            for thisfield in data['dateformat']:
                df[thisfield['field']] = pd.to_datetime(df[thisfield['field']], format=thisfield['format'])


        # prep database call to pull the batch file into redshift
        conn_string = "dbname='snowplow' host='snowplow-ca-bc-gov-main-redshi-resredshiftcluster-13nmjtt8tcok7.c8s7belbz4fo.ca-central-1.redshift.amazonaws.com' port='5439' user='microservice' password=" + os.environ['pgpass']

        # TODO: Loop on known pipe separated value columns, e.g., ancestor node (below)
	for i in range (-1, len(columns_lookup)): 
            if (i == -1):
                column = "metadata"
                dbtable = "metadata"
                key = columns_metadata
                df_new = df.copy()
            else:
                column = columns_lookup[i]
                key = "key"
                dbtable = dbtables_dictionaries[i]
    
                # make a working copy of the df
                df_0 = df.copy()
    
                # drop any nulls and wrapping delimeters, split and flatten:
                clean = df_0.dropna(subset = [column])[column].str[1:-1].str.split(nested_delim).values.flatten()
    
                # set to exlude duplicates
                L = list(set(itertools.chain.from_iterable(clean)))
    
                # make a dataframe of the list
                df_new = pd.DataFrame({column:L})
    
            # output the the dataframe as a csv
            to_s3(bucket, batchfile, dbtable +'.csv', df_new, key)
     
            # NOTE: batchfile is replaces by: batchfile + "/" + dbtable + ".csv" below
            # if truncate is set to true, truncate the db before loading
            if (truncate):
                truncate_str = "TRUNCATE " + dbtable + "; "
            else:
                truncate_str = ""

            query = "SET search_path TO " + dbschema + ";" + truncate_str + "copy " + dbtable +" FROM 's3://" + my_bucket.name + "/" + batchfile + "/" + dbtable + ".csv" + "' CREDENTIALS 'aws_access_key_id=" + os.environ['AWS_ACCESS_KEY_ID'] + ";aws_secret_access_key=" + os.environ['AWS_SECRET_ACCESS_KEY'] + "' IGNOREHEADER AS 1 MAXERROR AS 0 DELIMITER '	' NULL AS '-' ESCAPE;"
            logquery = "SET search_path TO " + dbschema + ";" + truncate_str + "copy " + dbtable +" FROM 's3://" + my_bucket.name + "/" + batchfile + "/" + dbtable + ".csv" + "' CREDENTIALS 'aws_access_key_id=" + 'AWS_ACCESS_KEY_ID' + ";aws_secret_access_key=" + 'AWS_SECRET_ACCESS_KEY' + "' IGNOREHEADER AS 1 MAXERROR AS 0 DELIMITER '	' NULL AS '-' ESCAPE;"
    
            log(logquery)
            with psycopg2.connect(conn_string) as conn:
                with conn.cursor() as curs:
                    try:
                        curs.execute(query)
                    except psycopg2.Error as e: # if the DB call fails, print error and place file in /bad
                        log("Loading failed\n\n")
                        log(e.pgerror)
                        outfile = badfile       # if the DB call succeed, place file in /good
                    else:
                        log("Loaded successfully\n\n")
                        outfile = goodfile


