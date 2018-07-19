#!/bin/bash

# takes the bucket, the output folder, and the file containing newline separated dcsIDs
# e.g., ./case2.sh sp-ca-bc-gov-2018-sdc-log-load  00_output dcsIDs.txt

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