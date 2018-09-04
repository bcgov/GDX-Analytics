#!/bin/bash

# takes the bucket, the output folder, and the file containing newline separated dcsIDs
# e.g., ./case2.sh sp-ca-bc-gov-2018-sdc-log-load  00_output dcsIDs.txt
###################################################################
# Script Name   : case1.sh
#
# Description   : counts the total lines for each csv specified in
#               : the bucket-directory-dcsID path reading dcsID
#               : from dcsIDs.txt, a list of one dcsID per new line
#               : results are saved in ./countlines_output/*.txt
#
# Requirements  : You must set the following environment variables
#               : to establish credentials for the microservice user
#
#               : export AWS_ACCESS_KEY_ID=<<KEY>>
#               : export AWS_SECRET_ACCESS_KEY=<<SECRET_KEY>>
#
#
# Usage         : ./case2.sh <<bucketname>> <<optional path>> <<dcsIDs.txt>>
# Example       : ./case2.sh sp-ca-bc-gov-2018-sdc-log-load 00_output dcsIDs.txt
#

bucket="$1"
folder="$2"
dcsIDs="$3"

echo "SN/LK - Testing Iteration Step 4 - Parsing log files in Spark"
echo "---"
echo "Case #2"

while read dcsID; do
  echo -n $dcsID
  echo -n " -- "
  python countlines.py $bucket $folder/$dcsID/ > countlines_output/$dcsID.txt
  echo "done"
done <$dcsIDs