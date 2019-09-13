#!/usr/bin/env bash
##################################################
#
# get the size of tables in schema "derived" 
# as well as total size of all tables
# into a row with table name "_TOTAL_"
#
##################################################

sql="select getdate() as date, \"table\",size FROM SVV_TABLE_INFO where schema='derived'
union
select getdate(), '_TOTAL_', sum(size) FROM SVV_TABLE_INFO where schema='derived'
order by size desc"
adminuser_rs -tqc "$sql"