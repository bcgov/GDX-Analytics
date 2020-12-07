CREATE TABLE IF NOT EXISTS test.cms_group
( 
  "id" VARCHAR(255) ENCODE ZSTD NOT NULL,
  "name" VARCHAR(255) ENCODE ZSTD,
  "active" BOOL ENCODE ZSTD,
  "site_key" VARCHAR(64) ENCODE ZSTD
);

GRANT SELECT ON test.cms_group TO "looker";