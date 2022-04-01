
CREATE TABLE IF NOT EXISTS maintenance.table_sizes
(
        date TIMESTAMP WITHOUT TIME ZONE   ENCODE zstd
        ,"schema" VARCHAR(255)   ENCODE zstd
        ,"table" VARCHAR(255)   ENCODE zstd
        ,tbl_rows BIGINT   ENCODE zstd
        ,size INTEGER   ENCODE zstd
        ,estimated_visible_rows BIGINT   ENCODE az64
        ,tombstoned_rows BIGINT   ENCODE az64
)
DISTSTYLE AUTO
SORTKEY (date)
;
ALTER TABLE maintenance.table_sizes owner to microservice;
