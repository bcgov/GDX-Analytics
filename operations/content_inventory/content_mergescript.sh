#!/bin/bash
# merge Client Inventory Analysis for Content CSV files
# Expecting three input varaibles in the order
# 1st parameter is the Explore CSV
# 2nd parameter is the SQL CSV
# 3rd parameter is the Output CSV

if [ $# -eq 0 ] # if there are no input variables
  then
    printf "Invalid options - this script is expecting three input variables, not zero\nAborting\n"
    exit 1 # abort the script
fi

if [ $# -eq 1 ] # if there is only one input variable
  then
    printf "Invalid options - this script is expecting three input variables, not one\nAborting\n"
    exit 1 # abort the script
fi

if [ $# -eq 2 ] # if there is only two input variables
  then
    printf "Invalid options - this script is expecting three input variables, not two\nAborting\n"
    exit 1 # abort the script
fi

# The operational code for merging files

if [ $# -eq 3 ]
  then
    explore_var=$1
    if ! test -f $explore_var; then
            printf "ERROR: The file \"$explore_var\" does not exist\nAborting\n"
            exit 1
    fi
    sql_var=$2
    if ! test -f $sql_var; then
            printf "ERROR: The file \"$sql_var\" does not exist\nAborting\n"
            exit 1
    fi
    output_var=$3
    if  test -f $output_var; then
            printf "ERROR: The file \"$output_var\" already exists\nAborting\n"
            exit 1
    fi
    (sed 's/Page View Start Month/metadata.node_id/g' $explore_var |grep -v 'Node ID' > temp.csv ) && join -j1 -t,  $sql_var temp.csv   > $output_var   && join -j1 -t, -v 1 $sql_var temp.csv >> $output_var && rm temp.csv;
    printf "SUCCESS: The file \"$output_var\" created\n"
    exit 0
fi
printf "Invalid options - this script is expecting three input variables\nAborting\n"
exit 1 # abort the script