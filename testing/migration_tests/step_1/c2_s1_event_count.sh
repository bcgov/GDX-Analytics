#!/bin/bash
#This script will count the number of lines in the file and subtract the lines
#containing header information (9 from sed command and 4 from SDC server) and fixes the total.
#SDC server writes each event to its own line. Output will display the adjusted number
#of events present in the log.
 
wc -l *.log | awk '$2=="total" { $1-=A; print ; next } { $1-=13; A+=13; print }'
