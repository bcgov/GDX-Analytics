#!/usr/bin/env bash
##################################################
# THIS IS A TEST SCRIPT TO USE FOR GDXDSD-7198
##################################################

echo "*Start of the TEST script*"

# Script Arguments
# In the final code, we can take below as an argument to the script
# so that we can edit through crontab
#REPORT_EMAIL="ozdemir.ozcelik@gov.bc.ca"

# Check if REPORT_EMAIL environment variable is set
if [ -z "$REPORT_EMAIL" ]; then
    echo "Error: REPORT_EMAIL environment variable is not set."
    exit 1
fi

# Use the REPORT_EMAIL environment variable
REPORT_EMAIL="$REPORT_EMAIL"

REPORT_INTERVAL_HOURS=1

FORCE_REPORT=false

# Check for --force-report argument
for arg in "$@"
do
    if [ "$arg" == "--force-report" ]; then
        FORCE_REPORT=true
    fi
done


# Define script variables
REPORT_LOG_PATH="ReportLogs/"
mkdir -p "$REPORT_LOG_PATH"
REPORT_LOG_PREFIX="Report_"
DATE=$(date -u +"%Y-%m-%d")
REPORT_LOG_FILE=${REPORT_LOG_PATH}${REPORT_LOG_PREFIX}$DATE
REPORT_SUBJECT_HOURLY="TEST- Hourly Job Summary"

# Current timestamp
current_time=$(date +"%Y-%m-%d %H:%M:%S")

# Get the current minute
minute=$(date +"%M")

# Get the current hour
hour=$(date +"%H")

run_table_size_task() {
    # echo "TEST: JUST PRINTING getRsTableSize FUNCTIONS:"
    # echo "TEST: Construction SQL query ..."
    # echo "TEST: Output log file and clean ..."
    # echo "TEST: Upload logs to S3 Clint..."
    # echo "TEST: Import from S3 to Redshift ..."
    # echo "TEST: Move files to S3 Good ..."
    # echo "TEST: Delete >7 days old logs from EC2 ..."
    
    # Simulate random return 0 (success) or 1 (failure)
    local random_exit_status=$((RANDOM % 2))
    if [ $random_exit_status -eq 0 ]; then
        echo "$current_time: INFO:  Load into table 'table_sizes' completed, ### record(s) loaded successfully ..."
    else
        echo "$current_time: INFO:  CRON ERROR ..."
    fi
    return $random_exit_status 
}

# Run the main task and log the output
run_table_size_task >> $REPORT_LOG_FILE 2>&1

# Capture the exit status of the task
status=$?
echo "Exit status of the task: $status"

# Check the report interval and send the log report, and delete logs for >7 days
if [ "$FORCE_REPORT" = true ] || ([ $((hour % REPORT_INTERVAL_HOURS)) -eq 0 ] && [ "$minute" -eq 00 ]); then
    if [ -s $REPORT_LOG_FILE ]; then
        # Send an email with the log content
        echo "Sending report email at $current_time"
        cat $REPORT_LOG_FILE | mail -s "$REPORT_SUBJECT_HOURLY" $REPORT_EMAIL
        echo "Email sent!"
        
        # Delete log files older than 1 week
        find $REPORT_LOG_PATH -mindepth 1 -mtime +7 -delete;
    else
        echo "Log file is empty at $current_time, nothing to report." >> $REPORT_LOG_FILE
    fi
fi

echo "*End of TEST script*"