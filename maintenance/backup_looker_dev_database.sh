#!/bin/bash
mysqldump looker_dev > ./tmp/backup-$(date +%Y-%m-%d).sql --set-gtid-purged=OFF
aws s3 cp ./tmp/backup-$(date +%Y-%m-%d).sql s3://ca-bc-gov-analytics-lookerdb-backup/looker-dev-database-backup/
rm ./tmp/backup-$(date +%Y-%m-%d).sql
