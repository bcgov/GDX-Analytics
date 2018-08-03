#!/bin/bash
###################################################################
# Script Name   : case1.sh
#
# Description   : counts the total objects for each dcsID specified
#               : in dcsIDs.txt as a list of one dcsID per new line
#
# Requirements  : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#
#
# Usage         : ./case1.sh <<dcsIDs.txt>>
#

dcsIDs="$1"

echo "SN/LK - Testing Iteration Step 4 - Parsing log files in Spark"
echo "Case #1"
echo "---"

while read dcsID; do
  echo -n $dcsID
  echo -n " -- "
  aws s3 ls s3://sp-ca-bc-gov-2018-sdc-log-load/00_output/$dcsID/ --recursive --summarize | grep "Total Objects:"
done <$dcsIDs
