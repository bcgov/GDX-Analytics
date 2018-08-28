#!/bin/bash
# File:   c1_s1_file_count.sh
# Usage:  $ ./c1_s1_file_count.sh <path_to_logs>

# This script will output counts of logs where the filename
# contains "YYYY-MM" for all months over 2016 and 2017.
# The "Total" logs will be all files with the ".log" extesnsion.
# As a result, the Total may differ from the sum of YYYY-MM parts
# if there were any other .log files in the path specified.

path_to_logs="$1"

MONTHS=(ZERO Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)
 
 
echo "SN/LK - Testing Iteration Step 1 - Transform logs to remove IP addresses"
echo " -------------------------------- "
echo " | Case #1 - SDC Log file counts | "
echo " -------------------------------- "
for ((year=16;year<=17;year++));
do
  for ((month=1;month<=12;month++));
  do
    echo -n "${MONTHS[$month]} $year: ";find $path_to_logs -maxdepth 1 -type f -print | grep -c "20$year-`printf %02d $month`.*\.log"
  done
done
echo "==============="
echo -n "Total: ";find $path_to_logs -type f -print | grep -c '\.log'
