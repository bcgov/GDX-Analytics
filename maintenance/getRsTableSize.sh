#!/usr/bin/env bash
##################################################
#
# Queries Redshift for the list of tables ordered by their size
#
# The results are returned without the column names printed out.
#
# The column order is:
# date, schema, table, size
#
# The date column is a timestamp in the America/Vancouver timezone
# The schema column is what schema the table is in
# the table columnn is the table name
# the size column is the size of the table, in 1 MB data blocks.
#
# An optional positive number positional argument limits the rows returned.
#
##################################################

# uncomment the following shell options to expand aliases and source the current ~/.bashrc file if not running as cron
shopt -s expand_aliases
source ~/.bashrc

# for no positional arguments return the full list of tables
if [ $# -eq 0 ]
  then
    sql="select convert_timezone('America/Vancouver', getdate()) as date, schema, \"table\",size FROM SVV_TABLE_INFO order by size desc"
else
    limit=$1
    # validate that the positional argument is a positive number
    re='^[0-9]+$'
    if ! [[ $limit =~ $re ]] ; then
        echo "error: Argument must be a number" >&2; exit 1
    else
    # limit the rows returned to the number provided as an argument
        sql="select convert_timezone('America/Vancouver', getdate()) as date, schema, \"table\",size FROM SVV_TABLE_INFO order by size desc limit $limit"
    fi
fi

# execute the query using the adminuser_rs alias
adminuser_rs -tqc "$sql"
