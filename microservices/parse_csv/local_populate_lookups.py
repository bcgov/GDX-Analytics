###################################################################
#Script Name    : local_populate_lookups.py
#
#Description    : Microservice script to load a csv file containing
#               : nested lists of values, and split that into a 
#               : series of CSV files as an indexed dictionary
#               : and one metadata table without nested arrays
#               : TODO: create node_id lookup tables as CSVs
#               : TODO: move from local to an AWS microservice
#
#Requirements   : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#               : export pgpass=<<DB_PASSWD>>
#               : (this is not applicable to local version)
#
#
#Usage          : pip2 install -r requirements.txt
#               : python27 local_populate_lookups.py configfile.json
#

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
doc = data['doc']
column_count = data['column_count']
columns_metadata = data['columns_metadata']
columns_lookup = data['columns_lookup']
delim = data['delim']
nested_delim = data['nested_delim']

# Check for an empty file. If it's empty, accept it as good and move on
try:
    df = pd.read_csv(doc)
except Exception as e: 
    if (str(e) == "No columns to parse from file"):
        log("Empty file, proceeding")
    else:
        print "Parse error: " + str(e) 

# Output Metadata csv
df.to_csv("out\metadata.csv", index=False, columns=columns_metadata)

for column in columns_lookup:
    df_0 = df.copy() # make a working copy of the df
    # drop any nulls and wrapping delimeters, split and flatten:
    clean = df_0.dropna(subset = [column])[column].str[1:-1].str.split(nested_delim).values.flatten() 
    L = list(set(itertools.chain.from_iterable(clean))) # set to exlude duplicates
    df_new = pd.DataFrame({column:L}) # make a dataframe of the list
    df_new.to_csv("out\{0}.csv".format(column), index_label="key") # output the the dataframe as a csv
