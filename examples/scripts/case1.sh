#!/bin/bash

dcsIDs="$1"

echo "SN/LK - Testing Iteration Step 4 - Parsing log files in Spark"
echo "---"
echo "Case #1"

while read dcsID; do
  echo -n $dcsID
  echo -n " -- "
  aws s3 ls s3://sp-ca-bc-gov-2018-sdc-log-load/00_output/$dcsID/ --recursive --summarize | grep "Total Objects:"
done <$dcsIDs
