#!/bin/bash
# merge Client Inventory Analysis for Asset CSV files
# Expecting no input variables or three input varaibles in the order
# 1st parameter is the Explore CSV
# 2nd parameter is the SQL CSV
# 3rd parameter is the Output CSV

# The operational code for merging files

if [ $# -eq 3 ] # if there are three input parameters when the script is executed
  then
    explore_var=$1 # store the first input parameter as the explore file
    if ! test -f $explore_var; then # see if the file exists, error if not
            printf "ERROR: The file \"$explore_var\" does not exist\nAborting\n"
            exit 1
    fi
    sql_var=$2 # store the second input parameter as the sql file
    if ! test -f $sql_var; then # see if the file exists, error if not
            printf "ERROR: The file \"$sql_var\" does not exist\nAborting\n"
            exit 1
    fi
    output_var=$3 # store the third input parameter as the output file
    if  test -f $output_var; then # see if the file exists, error if it DOES exist
            printf "ERROR: The file \"$output_var\" already exists\nAborting\n"
            exit 1
    fi

    # The line below is the merge command for the first two input variables and stores in the third file
    (sed 's/Download Time Month/metadata.node_id/g' $explore_var |grep -v 'Node ID' > temp.csv ) && join -j1 -t,  $sql_var temp.csv   > $output_var   && join -j1 -t, -v 1 $sql_var temp.csv >> $output_var && rm temp.csv
    printf "SUCCESS: The file \"$output_var\" created\n"
    exit 0
fi
#the following only executes if there is NOT 3 input parameters
printf "Invalid options - this script is expecting three input variables\nusage: asset_mergescript.sh EXPLORERCSV SQLCSV OUTPUTCSV\nAborting\n"
exit 1 # abort the script