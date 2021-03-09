#!/usr/bin/env bash
##################################################
#
# Queries Redshift for the list of tables ordered by their size
#
# The results are returned without the column names printed out.
#
# The column order is:
# date, schema, table, size
#
# The date column is a timestamp in the America/Vancouver timezone
# The schema column is what schema the table is in
# the table columnn is the table name
# the size column is the size of the table, in 1 MB data blocks.
#
# An optional positive number positional argument limits the rows returned.
#
##################################################

# uncomment the following shell options to expand aliases and source the current ~/.bashrc file if not running as cron
shopt -s expand_aliases
source ~/.bashrc

DATE=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
LOG_PATH="RsTableLogs/"
LOG_PREFIX="RedShift_Table_Size_"
OUT_FILE=${LOG_PATH}${LOG_PREFIX}$DATE
S3_PATH="s3://sp-ca-bc-gov-131565110619-12-microservices/client/redshift_table_size/"
S3_DEST="s3://sp-ca-bc-gov-131565110619-12-microservices/processed/good/client/redshift_table_size/"

# For no positional arguments return the full list of tables
if [ $# -eq 0 ]
  then
    read -r -d '' sql <<EOF
	SELECT convert_timezone('America/Vancouver', getdate()) as date, schema, "table", tbl_rows, size
	FROM SVV_TABLE_INFO
	ORDER BY size DESC
EOF
else
    limit=$1
    # validate that the positional argument is a positive number
    re='^[0-9]+$'
    if ! [[ $limit =~ $re ]] ; then
        echo "error: Argument must be a number" >&2; exit 1
    else
    # limit the rows returned to the number provided as an argument
    read -r -d '' sql <<EOF
        SELECT convert_timezone('America/Vancouver', getdate()) as date, schema, "table", tbl_rows, size
        FROM SVV_TABLE_INFO
        ORDER BY size DESC
	LIMIT $limit
EOF
    fi
fi

# Execute the query using the adminuser_rs alias and redirect output to file
adminuser_rs -tqc "$sql" >> $OUT_FILE

# Clean the file before s3 upload
sed -i '/^[[:space:]]*$/d' $OUT_FILE

# Copy output to  s3
aws s3 --quiet cp "$OUT_FILE" $S3_PATH

# Build table_size table
read -r -d '' rs_copy <<EOF
	COPY maintenance.table_sizes
	FROM '$S3_PATH'
	CREDENTIALS
	'aws_access_key_id=$AWS_ACCESS_KEY_ID;aws_secret_access_key=$AWS_SECRET_ACCESS_KEY'
	delimiter '|';
EOF

# Initiate copy to RedShift
adminuser_rs -tqc "$rs_copy"

# Move log file to processed
aws s3 mv $S3_PATH $S3_DEST --quiet --recursive

