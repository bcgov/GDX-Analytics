#!/bin/bash
################
#
# Filename consists of version number that was passed as an argument and then appending today's timestamp to keep track of files.
# This script performs following steps in order.Use it to backup looker prod database.
# Step1 - Backup Looker's prod database from RDS to local tmp directory.
# Step2 - Upload that backup to store in AWS s3 bucket.
# Step3 - Remove it from tmp directory for cleaning purposes
#
#
#
# Usage : backup_looker_prod_database.sh arg1
#  Where arg1 is the version number of the current Looker Prod.
#  For example: if the Looker Prod version being backed up is 21.20.10 then,
#               pass that as arg1, as in:
#               backup_looker_prod_database.sh 21.20.10
#################


version=$1
name=${version}_$(date +%Y-%m-%d-%H-%M)

mysqldump --result-file=./temp/looker_prod_backup_v${name}.sql --set-gtid-purged=OFF --add-drop-database --databases looker
aws s3 cp ./temp/looker_prod_backup_v${name}.sql s3://ca-bc-gov-analytics-lookerdb-backup/looker-prod-database-backup/
rm ./temp/looker_prod_backup_v${name}.sql
