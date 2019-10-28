--set default schema to admin
set search_path to admin;

select getdate();

--create STL_QUERY_HISTORY if not exists
create table IF NOT EXISTS STL_QUERY_HISTORY (like STL_QUERY including defaults);

--create or replace v_stl_query_history 
create or replace view v_stl_query_history as
SELECT *, regexp_substr(querytxt,'"user_id":(\\d+)',1,1,'e') AS looker_user_id 
FROM stl_query_history;

--delete data older than 7 months
delete STL_QUERY_HISTORY
  where starttime < dateadd(month, -7, CURRENT_DATE);

--insert yesterday's data
insert into STL_QUERY_HISTORY (
  select * from stl_query 
  where
    querytxt ilike '-- Looker Query Context%' 
    and starttime >= dateadd(day, -1, CURRENT_DATE)
    and starttime < current_date
);

select getdate();

