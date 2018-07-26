###################################################################
#Script Name    : local_populate_lookups.py
#
#Description    : prototype to create csv artifacts from processing
#               : a flat file input having multidimensional entires
#               : 
#               : file and characteristics are defined by json argv
#               : TODO: move from prototype to an AWS microservice
#
#Requirements   : a csv file to process, and json instruction file
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


# Check for an empty file. If it's empty, accept it as good and move on
try:
    df = pd.read_csv(doc)
except Exception as e: 
    if (str(e) == "No columns to parse from file"):
        log("Empty file, proceeding")
    else:
        print "Parse error: " + str(e) 


# Output Metadata csv
df.to_csv("out/metadata.csv", index=False, columns=columns_metadata)


# Build dictionary dataframes
dictionary_dfs = {}
for i in range (len(columns_lookup)): 
    section = columns_lookup[i]
    key = "key"
    dbtable = dbtables_dictionaries[i]

    # drop any nulls and wrapping delimeters, split and flatten:
    clean = df.copy().dropna(subset = [section])[section].str[1:-1].str.split(nested_delim).values.flatten()

    # set to exlude duplicates
    L = list(set(itertools.chain.from_iterable(clean)))

    # make a dataframe of the list
    df_new = pd.DataFrame({section:L})

    # add this dictionary DF to  dictionaries map
    dictionary_dfs[columns_lookup[i]] = df_new

# Save dictionary dataframes as .csv files locally
for i,section in enumerate(columns_lookup):
    save_dictionary_df = dictionary_dfs[section]
    save_dictionary_path = 'out/%s.csv' % dbtables_dictionaries[i]
    save_dictionary_df.to_csv(save_dictionary_path, index_label="id", header='value')


# Build lookup dataframes
lookup_dfs = {}
for section in columns_lookup:

    # get the dictionary of interest
    df_dictionary = dictionary_dfs[section]

    # for each row in df
    df_lookup = pd.DataFrame(columns=['node_id','lookup_id'])
    for index, row in df.copy().iterrows():
        if row[section] is not pd.np.nan:
            # iterate over the list of delimited terms
            entry = row[section] # get the full string of delimited values to be looked up
            entry = entry[1:-1] # remove wrapping delimeters
            if entry: # skip empties
                for lookup_entry in entry.split(nested_delim): # split on delimiter and iterate on resultant list
                    node_id = row.node_id # the node id from the current row
                    lookup_id = df_dictionary.loc[df_dictionary[section] == lookup_entry].index[0] # its dictionary index
                    d = pd.DataFrame([[node_id,lookup_id]], columns=['node_id','lookup_id']) # create the data frame to concat
                    df_lookup = pd.concat([df_lookup,d], ignore_index=True)
                lookup_dfs[section] = df_lookup


# Save lookup dataframes as .csv files locally
for i,section in enumerate(columns_lookup):
    save_metadata_df = lookup_dfs[section]
    save_metadata_path = 'out/%s.csv' % dbtables_metadata[i]
    save_metadata_df.to_csv(save_metadata_path, index=False, header=['node_id','id'])
    