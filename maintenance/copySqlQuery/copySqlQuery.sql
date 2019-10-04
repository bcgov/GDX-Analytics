--set default schema to admin
set search_path to admin;

select getdate();

--create STL_QUERY_HISTORY if not exists
create table IF NOT EXISTS STL_QUERY_HISTORY (like STL_QUERY including defaults);

--delete data older than 6 months
delete STL_QUERY_HISTORY
  where starttime < dateadd(month, -6, CURRENT_DATE);

--insert yesterday's data
insert into STL_QUERY_HISTORY (
  select * from stl_query 
  where
    querytxt ilike '-- Looker Query Context%' 
    and starttime >= dateadd(day, -1, CURRENT_DATE)
    and starttime < current_date
);

select getdate();

