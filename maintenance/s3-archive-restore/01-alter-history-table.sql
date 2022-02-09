ALTER TABLE test.atomic_sept_30_poc_parquet
ADD domain_sessionid CHAR(128);
ALTER TABLE test.atomic_sept_30_poc_parquet
ADD page_urlhost VARCHAR(255);
ALTER TABLE test.atomic_sept_30_poc_parquet
ADD page_url VARCHAR(4096);
