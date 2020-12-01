CREATE TABLE IF NOT EXISTS cmslite.user_group
( 
  "id" VARCHAR(255) ENCODE ZSTD NOT NULL,
  "user_id" VARCHAR(255)  ENCODE ZSTD,
  "email" VARCHAR(512) ENCODE ZSTD,
  "group_id" VARCHAR(255) ENCODE ZSTD,
  "group_name" VARCHAR(255) ENCODE ZSTD,
  "site_key" VARCHAR(64) ENCODE ZSTD,
  "is_group_mgr" BOOL ENCODE ZSTD
);

GRANT SELECT ON cmslite.user_group TO "looker";