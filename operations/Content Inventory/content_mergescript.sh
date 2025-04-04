#!/bin/bash
# merge Client Inventory Analysis for Content CSV files
# Expecting no input variables or three input varaibles in the order
# 1st parameter is the Explore CSV
# 2nd parameter is the SQL CSV
# 3rd parameter is the Output CSV

if [ $# -eq 1 ] # if there is only one input variable
  then
    printf "This script is expecting zero or three input variables, not one\nAborting\n"
    exit 1 # abort the script
fi

if [ $# -eq 2 ] # if there is only two input variables
  then
    printf "This script is expecting zero or three input variables, not two\nAborting\n"
    exit 1 # abort the script
fi

if [ $# -eq 0 ]
     then

        read -p 'Page Explore CSV: ' explore_var
        if ! test -f $explore_var; then #check if the provided file exists
            printf "ERROR: The file \"$explore_var\" does not exist\nAborting\n"
            exit 22 # abort the script
        fi

        read -p 'Page SQL CSV: ' sql_var
        if ! test -f $sql_var; then #check if the provided file exists
            printf "ERROR: The file \"$sql_var\" does not exist\nAborting\n"
            exit 22 # abort the script
        fi

        read -p 'Output CSV: ' output_var
        if  test -f $output_var; then #check if the provided DOES NOT file exists
            printf "ERROR: The file \"$output_var\" already exists\nAborting\n"
            exit 22 # abort the script
        fi
        # line below is the merge command based on the first column of Node ID
        # merge takes the Meta Data and merges on the Page Views
        # there is a temp file "temp.csv" that is created and destoryed
        (sed 's/Page View Start Month/metadata.node_id/g' $explore_var |grep -v 'Node ID' > temp.csv ) && join -j1 -t,  $sql_var temp.csv   > $output_var   && join -j1 -t, -v 1 $sql_var temp.csv >> $output_var && rm temp.csv
fi

# The same as above but with the file names in the order EXPLORE SQL OUTOUT

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
fi

printf "SUCCESS: The file \"$output_var\" created\n"
exit 0