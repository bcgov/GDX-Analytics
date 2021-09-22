#!/bin/bash
################
#
#Filename consists of version number that was passed as an argument and then appending today's date to keep track of files.
#This script performs following steps in order.Use it to backup looker dev database.
#Step1 -Backup Looker's dev database from RDS to local tmp directory.
#Step2 -Upload that backup to store in AWS s3 bucket.
#Step3 -Remove it from tmp directory for cleaning purposes
#
#
#
#Usage :backup_looker_dev_database.sh arg1
#Where arg1 = Current looker dev version
#For example if looker dev version is 21.20.10 then command would be backup_looker_dev_database.sh 21.20.10
#################


version=$1

mysqldump looker_dev > ./tmp/looker_dev_backup_v${version}_$(date +%Y-%m-%d).sql --set-gtid-purged=OFF
aws s3 cp ./tmp/looker_dev_backup_v${version}_$(date +%Y-%m-%d).sql s3://ca-bc-gov-analytics-lookerdb-backup/looker-dev-database-backup/
rm ./tmp/looker_dev_backup_v${version}_$(date +%Y-%m-%d).sql