#!/bin/bash
# File:   c2_s1_event_count.sh
# Usage:  $ ./c2_s1_event_count.sh <path_to_logs>

# This script will count the number of lines in the files under <path_to_logs>
# and subtract the lines containing header information (9 from sed command and
# 4 from SDC server) and fixes the total. SDC server writes each event to its 
# own line. Output will display the adjusted event counts present in each logs.
 
wc -l *.log | awk '$2=="total" { $1-=A; print ; next } { $1-=13; A+=13; print }'
