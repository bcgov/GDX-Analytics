#!/usr/bin/env bash
##################################################
#
# Queries Redshift for the list of tables ordered by their size and writes the results to a Redshift table:
# - The raw query results are stored locally in a log file with a predefined prefix
# - Log files (with table size information) are uploaded to S3 for processing
# - After successful processing, logs are moved to S3 destination folder
# - Local log files older than 7 days are automatically deleted
#
# The Redshift table column order is:
# - date: Timestamp in the America/Vancouver timezone
# - schema: Schema the table belongs to
# - table: Table name
# - tbl_rows: Row count of the table
# - size: Size of the table in 1 MB data blocks
#
# Optional Positional Arguments:
#  -h, --help: Displays help information and usage.
#  --force-report: Forces a log report to be generated immediately, bypassing the set interval.
#  --report-interval=H: Sets the interval (in H hours) for automatic report generation (default: 1 hour).
#  --limit-rows=N: Limits the results written to Redshift to N rows.
#
# Logging for Reporting:
# - The script logs the Redshift table size query output for reporting.
# - Reports are generated at regular intervals defined by --report-interval (default is 1 hour).
# - The report log file is maintained daily, and logs older than 7 days are automatically deleted.
#
# Reporting:
# - The script checks if the current hour is divisible by the report interval using the modulo operation %.
# - If the remainder is 0, it means the current hour matches the reporting interval.
#   (HOUR: Current hour (24-hour format), used to check report intervals.)
# - Reports are only generated at the hour's start (when minutes are 00).
#   (MINUTE: The minute at the start of the job ensures reports are only generated at the beginning of the hour.)
# - The script interpret $HOUR (and $MINUTE) as decimal (base-10) by using the 10# prefix. 
# - If --force-report is used, the report will be generated immediately, regardless of the current time.
#
##################################################

# Uncomment the following shell options to expand aliases and source the current ~/.bashrc file if not running as cron
shopt -s expand_aliases
source ~/.bashrc

# Set default command-line values
REPORT_INTERVAL_HOURS=1
FORCE_REPORT=false

# Define variables for logging and output file management
DATE=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
LOG_PATH="RsTableLogs/"
mkdir -p "$LOG_PATH" # Ensure the log directory exists
LOG_PREFIX="RedShift_Table_Size_"
OUT_FILE=${LOG_PATH}${LOG_PREFIX}$DATE # Combine to create the output file name

# S3 paths and destination table for storing and processing data
TABLE_DEST="maintenance.table_sizes"
S3_PATH="s3://sp-ca-bc-gov-131565110619-12-microservices/client/redshift_table_size/"
S3_DEST="s3://sp-ca-bc-gov-131565110619-12-microservices/processed/good/client/redshift_table_size/"

# Variables used for reporting
REPORT_LOG_PATH="ReportLogs/"
mkdir -p "$REPORT_LOG_PATH" # Ensure the report log directory exists
REPORT_LOG_PREFIX="Report_"
REPORT_DATE=$(date -u +"%Y-%m-%d")
REPORT_LOG_FILE=${REPORT_LOG_PATH}${REPORT_LOG_PREFIX}$REPORT_DATE
CURRENT_TIME=$(date +"%Y-%m-%d %H:%M:%S")
MINUTE=$(date +"%M")
HOUR=$(date +"%H")

# Function to display help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --limit-rows=N      Limit results written to Redshift to N rows."
    echo "  --report-interval=H  Set the interval to report in every H hours."
    echo "  --force-report       Force to create a report without considering the report interval."
    echo "  -h, --help          Show this help message."
}

# Process command-line arguments
for arg in "$@"; 
do
  case $arg in
    --limit-rows=*)
      LIMIT_ROWS="${arg#*=}"
      ;;
    --report-interval=*)
      REPORT_INTERVAL_HOURS="${arg#*=}"
      ;;
    --force-report)
      FORCE_REPORT=true
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Warning: Unrecognized argument: $arg" >&2
      ;;
  esac
done

# Validate REPORT_INTERVAL_HOURS
if ! [[ "$REPORT_INTERVAL_HOURS" =~ ^[1-9][0-9]*$ ]]; then
    echo "error: --report-interval must be a positive integer." >&2
    exit 1
fi

# Validate LIMIT_ROWS (if set)
if [[ -n "$LIMIT_ROWS" ]] && ! [[ "$LIMIT_ROWS" =~ ^[1-9][0-9]*$ ]]; then
    echo "error: --limit-rows must be a positive integer." >&2
    exit 1
fi

# Construct the SQL query based on LIMIT_ROWS
if [[ -z "$LIMIT_ROWS" ]]; then
    # No limit set, return full list of tables
    read -r -d '' sql <<EOF
	SELECT convert_timezone('America/Vancouver', getdate()) as date, schema, "table", tbl_rows, size, estimated_visible_rows, tbl_rows-estimated_visible_rows AS tombstoned_rows
	FROM SVV_TABLE_INFOl
	ORDER BY size DESC
EOF
else
    # Limit the rows returned to the number specified in LIMIT_ROWS
    read -r -d '' sql <<EOF
    SELECT convert_timezone('America/Vancouver', getdate()) as date, schema, "table", tbl_rows, size, estimated_visible_rows, tbl_rows-estimated_visible_rows AS tombstoned_rows
    FROM SVV_TABLE_INFO
    ORDER BY size DESC
    LIMIT $LIMIT_ROWS
EOF
fi

# Execute the query using the adminuser_rs alias and redirect output to file
adminuser_rs -tqc "$sql" >> $OUT_FILE

# Clean the file before s3 upload
sed -r -i 's/[\t ]//g;/^$/d' $OUT_FILE

# Copy output to s3
aws s3 --quiet cp "$OUT_FILE" $S3_PATH

# Build table_size table
read -r -d '' rs_copy <<EOF
        COPY $TABLE_DEST
        FROM '$S3_PATH'
        CREDENTIALS
        'aws_access_key_id=$AWS_ACCESS_KEY_ID;aws_secret_access_key=$AWS_SECRET_ACCESS_KEY'
        escape
	ignoreblanklines
        trimblanks
        delimiter '|';
EOF

# Initiate copy to RedShift
printf "($CURRENT_TIME) " >> "$REPORT_LOG_FILE" 2>&1
adminuser_rs -tqc "$rs_copy" >> "$REPORT_LOG_FILE" 2>&1

# Move log file to processed
aws s3 mv $S3_PATH $S3_DEST --quiet --recursive

# Remove log files +7 days old
find $LOG_PATH -mindepth 1 -mtime +7 -delete

# Check the report interval and echo the log report
if [ "$FORCE_REPORT" = true ] || ([ $((10#$HOUR % REPORT_INTERVAL_HOURS)) -eq 0 ] && [ $((10#$MINUTE)) -eq 0 ]); then
    if [ -s $REPORT_LOG_FILE ]; then
        # echo the log content to send the report to MAILTO recipients
        echo -e "Log report for Redshift table sizes:\n"
        echo "$(tac $REPORT_LOG_FILE)"
    else
        echo "Log file is empty at $CURRENT_TIME, nothing to report."
    fi
fi

# Delete log files older than 1 week
find $REPORT_LOG_PATH -mindepth 1 -mtime +7 -delete;
