CREATE TABLE IF NOT EXISTS cmslite.cms_group
( 
  "id" VARCHAR(255) ENCODE ZSTD NOT NULL,
  "name" VARCHAR(255) ENCODE ZSTD,
  "active" BOOL ENCODE ZSTD,
  "site_key" VARCHAR(64) ENCODE ZSTD
);

GRANT SELECT ON cmslite.cms_group TO "looker";