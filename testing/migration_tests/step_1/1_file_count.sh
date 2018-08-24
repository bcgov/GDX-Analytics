#!/bin/bash
#file: file_count.sh
#usage: $ ./file_count.sh <path>

path = "$1"

MONTHS=(ZERO Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)
 
 
echo "SN/LK - Testing Iteration Step 1 - Transform logs to remove IP addresses"
echo " -------------------------------- "
echo " | Case #1 - SDC Log file counts | "
echo " -------------------------------- "
for ((year=16;year<=17;year++));
do
  for ((month=1;month<=12;month++));
  do
    echo -n "${MONTHS[$month]} $year: ";find $path -type f -print | grep -c "20$year-`printf %02d $month`"
  done
done
echo "==============="
echo -n "Total: ";find $path -type f -print | grep '.log' | wc -l
