# Copy Looker SQL query Logs
## What
Scripts in this folder is intended to be run by a nightly cron job. The scripts copy yesterday's SQL queries executed by Looker user from RedShift *stl_query* table to proprietary *admin.stl_query_history* table.

## Why
 *stl_query* retains approximately two to five days of log history, depending on log usage and available disk space. Auditing requirements imposed by clients require 6 months of log history, *stl_query* is thus insufficient. The scripts and 
 *admin.stl_query_history* table are designed to address the retention shortfall.

## How
To schedule the cronjob, put this folder under, say, *~/scripts* and add following line to crontab 

```
0 1 * * * source ~/.bashrc && . ~/scripts/copySqlQuery/copySqlQuery.sh > ~/scripts/copySqlQuery/lastRunOutput
```

The above crontab line runs the script daily at 1am and logs the output to file *~/scripts/copySqlQuery/lastRunOutput*