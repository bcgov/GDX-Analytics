#!/usr/bin/env bash
##################################################
# Cehck for old files in the directory and load them to s3
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
##################################################

# uncomment the following shell options to expand aliases and source the current ~/.bashrc file if not running as cron
shopt -s expand_aliases
source ~/.bashrc

LOG_PATH="RsTableLogs/"
S3_PATH="s3://sp-ca-bc-gov-131565110619-12-microservices/client/redshift_table_size/"
S3_DEST="s3://sp-ca-bc-gov-131565110619-12-microservices/processed/good/client/redshift_table_size/"

# Copy output to  s3
aws s3 cp $LOG_PATH $S3_PATH --recursive

# Build table_size table
read -r -d '' rs_copy <<EOF
        COPY maintenance.table_sizes
        FROM '$S3_PATH'
        CREDENTIALS
        'aws_access_key_id=$AWS_ACCESS_KEY_ID;aws_secret_access_key=$AWS_SECRET_ACCESS_KEY'
        escape
        ignoreblanklines
        trimblanks
        delimiter '|';
EOF


# Initiate copy to RedShift
adminuser_rs -tqc "$rs_copy"

# Move log file to processed
aws s3 mv $S3_PATH $S3_DEST --quiet --recursive
