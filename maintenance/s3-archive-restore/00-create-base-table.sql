CREATE TABLE IF NOT EXISTS gdx_analytics.restored_atomic_ca_bc_gov (
    root_tstamp         TIMESTAMP       ENCODE RAW,
    page_view_id        VARCHAR(36)     ENCODE ZSTD,
    root_id             CHAR(36)        ENCODE LZO,
    page_urlhost        VARCHAR(255)    ENCODE ZSTD,
    page_url            VARCHAR(4096)   ENCODE ZSTD,
    domain_sessionid    CHAR(128)       ENCODE ZSTD,
    PRIMARY KEY(root_id)
)
-- Set diststyle to key to avoid
DISTSTYLE KEY
-- Optimize join to events table
DISTKEY (root_id)
SORTKEY (root_tstamp);
