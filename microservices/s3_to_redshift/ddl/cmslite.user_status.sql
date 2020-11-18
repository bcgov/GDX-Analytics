CREATE TABLE IF NOT EXISTS cmslite.user_status
(
  "id" VARCHAR(255) ENCODE ZSTD NOT NULL,
  "organization" VARCHAR(20)  ENCODE ZSTD,
  "user_id" VARCHAR(100) ENCODE ZSTD,
  "user_name" VARCHAR(512) ENCODE ZSTD,
  "email" VARCHAR(512) ENCODE ZSTD,
  "created_dt" TIMESTAMP ENCODE ZSTD,
  "status" VARCHAR(32) ENCODE ZSTD
);

GRANT SELECT ON cmslite.user_status TO "looker";