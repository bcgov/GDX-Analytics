CREATE TABLE IF NOT EXISTS cmslite.asset_downloads
( 
  "ip" VARCHAR(255) ENCODE ZSTD NOT NULL,
  "date_timestamp" VARCHAR(255)  ENCODE ZSTD,
  "request_string" VARCHAR(4095) ENCODE ZSTD,
  "status_code" DOUBLE PRECISION ENCODE ZSTD,
  "return_size" DOUBLE PRECISION ENCODE ZSTD,
  "referrer" VARCHAR(4095) ENCODE ZSTD,
  "user_agent_http_request_header" VARCHAR(4095) ENCODE ZSTD,
  "request_response_time" VARCHAR(255)  ENCODE ZSTD,
  "os_family" VARCHAR(255) ENCODE ZSTD,
  "os_version" VARCHAR(255) ENCODE ZSTD,
  "browser_family" VARCHAR(255) ENCODE ZSTD,
  "browser_version" VARCHAR(255) ENCODE ZSTD,
  "referrer_source" VARCHAR(255) ENCODE ZSTD,
  "referrer_medium" VARCHAR(255) ENCODE ZSTD
);

GRANT SELECT ON cmslite.asset_downloads TO "looker";