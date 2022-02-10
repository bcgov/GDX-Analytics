CREATE TABLE IF NOT EXISTS test.atomic_sept_poc_parquet (
    root_tstamp TIMESTAMPTZ ENCODE ZSTD,
    page_view_id VARCHAR(36) ENCODE ZSTD NOT NULL,
    root_id CHAR(36) ENCODE LZO,
    page_urlhost VARCHAR(255) ENCODE ZSTD,
    page_url VARCHAR(4096) ENCODE ZSTD,
    domain_sessionid CHAR(128) ENCODE ZSTD,
    PRIMARY KEY(root_id)
    SORTKEY(root_tstamp)
)
