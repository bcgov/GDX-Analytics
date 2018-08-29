#!/bin/bash
# File:   c2_s1_event_count.sh
# Usage:  $ ./c2_s1_event_count.sh <path_to_logs>

# This script will count the number of lines in the files under <path_to_logs>
# and subtract the 5 lines from SDC server containing header information and
# fixes the total. SDC server writes each event to its own line. Output will
# display the adjusted event counts present in each logs.

# Caveats:
# - months contributing 0 log files result in a wc error message
# - months contributing only 1 log file will fail to produce any output
# - these do not cause a failure; the next line is proceessed with no interrupt

path_to_logs="$1"

MONTHS=(ZERO Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)

echo "SN/LK - Testing Iteration Step 1 - Transform logs to remove IP addresses"
echo " ---------------------------------- "
echo " | Case #2 - SDC Log Event Counts | "
echo " ---------------------------------- "
for ((year=16;year<=17;year++));
do
  for ((month=1;month<=12;month++));
  do
    echo -n "${MONTHS[$month]} $year: ";wc -l $path_to_logs*20$year-`printf %02d $month`*.log | awk '$2=="total" { $1-=A; print ; next } { $1-=5; A+=5; print }' | grep 'total'
  done
done
echo "==============="
echo -n "Total: ";wc -l $path_to_logs*dcs*.log | awk '$2=="total" { $1-=A; print ; next } { $1-=5; A+=5; print }' | grep 'total'
