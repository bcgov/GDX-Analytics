#!/usr/bin/env bash
##################################################
# THIS IS A TEST SCRIPT TO USE FOR GDXDSD-7198
##################################################

echo "*start of TEST script*"

REPORT_LOG_PATH="ReportLogs/"
mkdir -p "$REPORT_LOG_PATH"
REPORT_LOG_PREFIX="Report_"
REPORT_LOG_FILE=${REPORT_LOG_PATH}${REPORT_LOG_PREFIX}$DATE
REPORT_EMAIL="ozdemir.ozcelik@gov.bc.ca"
REPORT_SUBJECT_HOURLY="Hourly Job Summary"
REPORT_MESSAGE=""

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
        echo "TEST ECHO TASK: INFO:  Load into table 'table_sizes' completed, ### record(s) loaded successfully ..."
    else
        echo "TEST ECHO TASK: INFO:  CRON ERROR ..."
    fi
    return $random_exit_status 
}

# Run the main task and log the output
run_table_size_task >> $REPORT_LOG_FILE 2>&1

# Capture the exit status of the task
status=$?
echo "Exit status of the task: $status"

# Current timestamp
current_time=$(date +"%Y-%m-%d %H:%M:%S")

# Get the current minute
minute=$(date +"%M")

# If it's the top of the hour (minute == 00), send the hourly log report, and delete logs for >7 days
if [ "$minute" == "00" ]; then
    if [ -s $REPORT_LOG_FILE ]; then
        # Send an email with the log content
        cat $REPORT_LOG_FILE | mail -s "$REPORT_SUBJECT_HOURLY" $REPORT_EMAIL
        
        # Delete log files older than 1 week
        find $REPORT_LOG_PATH -mindepth 1 -mtime +7 -delete;
    else
        echo "Log file is empty at $current_time, nothing to report." >> $REPORT_LOG_FILE
    fi
fi

echo "*end of TEST script*"