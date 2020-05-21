#!/usr/bin/env bash
##################################################
#
# get top 10 largest tables
#
##################################################

sql="select getdate() as date, schema, \"table\",size FROM SVV_TABLE_INFO order by size desc limit 10"
adminuser_rs -tqc "$sql"