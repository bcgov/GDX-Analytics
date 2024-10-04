#!/usr/bin/env bash
##################################################
#
# Queries Redshift for the list of tables ordered by their size
#
# The results are written to a Redshift table.
#
# The column order is:
# date, schema, table, tbl_rows, size
#
# The date column is a timestamp in the America/Vancouver timezone
# The schema column is what schema the table is in
# The table columnn is the table name
# The tbl_rows column is the table row count
# The size column is the size of the table, in 1 MB data blocks.
#
# An optional positive number positional argument limits the rows returned.
#
# An optional --force-report positional argument sends a log report.
#
##################################################

# DELETE
echo "*Start of the TEST script*"

# uncomment the following shell options to expand aliases and source the current ~/.bashrc file if not running as cron
shopt -s expand_aliases
source ~/.bashrc

# Check if REPORT_EMAIL environment variable is set
if [ -z "$REPORT_INTERVAL_HOURS" ]; then
    echo "Error: REPORT_INTERVAL_HOURS environment variable is not set."
    exit 1
fi

# Check if REPORT_EMAIL_TO environment variable is set
if [ -z "$REPORT_EMAIL_TO" ]; then
    echo "Error: REPORT_EMAIL_TO environment variable is not set."
    exit 1
fi

# Check for --force-report argument
FORCE_REPORT=false
for arg in "$@"
do
    if [ "$arg" == "--force-report" ]; then
        FORCE_REPORT=true
    fi
done


# Variables
#DATE=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
# LOG_PATH="RsTableLogs/"
# LOG_PREFIX="RedShift_Table_Size_"
DATE="2024-10-01T23:00:01+00:00"
LOG_PATH="TEST_RsTableLogs/"
LOG_PREFIX="RedShift_Table_Size_"
OUT_FILE=${LOG_PATH}${LOG_PREFIX}$DATE
S3_PATH="s3://sp-ca-bc-gov-131565110619-12-microservices/client/oz_test/GDXDSD-7198/client_redshift_table_size/"
S3_DEST="s3://sp-ca-bc-gov-131565110619-12-microservices/client/oz_test/GDXDSD-7198/processed_good_client_redshift_table_size/"


# Variables used for reporting
REPORT_EMAIL_TO="$REPORT_EMAIL_TO"
REPORT_INTERVAL_HOURS="$REPORT_INTERVAL_HOURS"
REPORT_LOG_PATH="ReportLogs/"
mkdir -p "$REPORT_LOG_PATH"
REPORT_LOG_PREFIX="Report_"
REPORT_DATE=$(date -u +"%Y-%m-%d")
REPORT_LOG_FILE=${REPORT_LOG_PATH}${REPORT_LOG_PREFIX}$REPORT_DATE
REPORT_SUBJECT="TEST- Hourly Job Summary"
CURRENT_TIME=$(date +"%Y-%m-%d %H:%M:%S")
MINUTE=$(date +"%M")
HOUR=$(date +"%H")

# Color-code the output of the task
process_task_output() {
    while IFS= read -r line; do
        if echo "$line" | grep -q -i "error"; then
            log_message "$line" "red"
        elif echo "$line" | grep -q -i "success"; then
            log_message "$line" "green"
        else
            log_message "$line" "black"
        fi
    done
}


# Log messages with timestamps and colors (sending as HTML)
log_message() {
    local message="$1"
    local color="$2"
    local reset="</span>"  # reset color in HTML
    local timestamp="$(date +"%Y-%m-%d %H:%M:%S")"
    echo "<span style=\"color: ${color};\">[${timestamp}] ${message}${reset}</span><br>" >> "$REPORT_LOG_FILE"
}

run_table_size_task() {

# DELETE - fail test
ls /non_existent_directory  # this command will fail

echo "$CURRENT_TIME: Executing the task for ${LOG_PREFIX}$DATE"

# For no positional arguments return the full list of tables
# if [ $# -eq 0 ]
#   then
#     read -r -d '' sql <<EOF
# 	SELECT convert_timezone('America/Vancouver', getdate()) as date, schema, "table", tbl_rows, size, estimated_visible_rows, tbl_rows-estimated_visible_rows AS tombstoned_rows
# 	FROM SVV_TABLE_INFO
# 	ORDER BY size DESC
# EOF
# else
#     limit=$1
#     # validate that the positional argument is a positive number
#     re='^[0-9]+$'
#     if ! [[ $limit =~ $re ]] ; then
#         echo "error: Argument must be a number" >&2; exit 1
#     else
#     # limit the rows returned to the number provided as an argument
#     read -r -d '' sql <<EOF
#         SELECT convert_timezone('America/Vancouver', getdate()) as date, schema, "table", tbl_rows, size, estimated_visible_rows, tbl_rows-estimated_visible_rows AS tombstoned_rows
#         FROM SVV_TABLE_INFO
#         ORDER BY size DESC
# 	LIMIT $limit
# EOF
#     fi
# fi

# Execute the query using the adminuser_rs alias and redirect output to file
# adminuser_rs -tqc "$sql" >> $OUT_FILE

# Clean the file before s3 upload
sed -r -i 's/[\t ]//g;/^$/d' $OUT_FILE

# Copy output to  s3
aws s3 --quiet cp "$OUT_FILE" $S3_PATH

# Build table_size table
read -r -d '' rs_copy <<EOF
        COPY test.gdxdsd_7198_table_sizes
        FROM '$S3_PATH'
        CREDENTIALS
        'aws_access_key_id=$AWS_ACCESS_KEY_ID;aws_secret_access_key=$AWS_SECRET_ACCESS_KEY'
        escape
	ignoreblanklines
        trimblanks
        delimiter '|';
EOF

# Initiate copy to RedShift
# adminuser_rs -tqc "$rs_copy"

# DELETE
echo "INFO:  Load into table 'gdxdsd_7198_table_sizes' completed, XXX record(s) loaded successfully."

# Move log file to processed
aws s3 mv $S3_PATH $S3_DEST --quiet --recursive

# Remove log files +7 days old
find $LOG_PATH -mindepth 1 -mtime +7 -delete

return 0

}

# Run the main task in a subshell to capture the exit status of the task
# and redirect subshell's stderr to parent's stderr
error_message=$( (
    set -e
    run_table_size_task | process_task_output
) 2>&1 )
status=${PIPESTATUS[0]}

echo "Exit status of the task: $status"
echo "$error_message"

if [ $status -ne 0 ]; then
    log_message "ERROR: Task failed with exit status $status" "red"
else
    log_message "SUCCESS: Task completed successfully with exit status $status" "green"
fi

# Check the report interval and send the log report, and delete logs for >7 days
if [ "$FORCE_REPORT" = true ] || ([ $((HOUR % REPORT_INTERVAL_HOURS)) -eq 0 ] && [ "$MINUTE" -eq 00 ]); then
    if [ -s $REPORT_LOG_FILE ]; then
        # Send an email with the log content
        echo "Sending report email at $CURRENT_TIME"
        # use below to send as text
        # cat $REPORT_LOG_FILE | mail -s "$REPORT_SUBJECT" $REPORT_EMAIL_TO
        # use below to send as html
        (echo "Subject: $REPORT_SUBJECT"; echo "To: $REPORT_EMAIL_TO"; echo "MIME-Version: 1.0"; echo "Content-Type: text/html; charset=UTF-8"; echo ""; cat $REPORT_LOG_FILE) | sendmail -t
        echo "Email sent!"     
    else
        echo "Log file is empty at $CURRENT_TIME, nothing to report." >> $REPORT_LOG_FILE
    fi
fi

# Delete log files older than 1 week
find $REPORT_LOG_PATH -mindepth 1 -mtime +7 -delete;

echo "*End of TEST script*"


