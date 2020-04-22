CREATE TABLE IF NOT EXISTS workbc.asset_downloads_derived
( 
  "asset_path" VARCHAR(4117) ENCODE ZSTD NOT NULL,
  "date_timestamp" timestamp without time zone ENCODE ZSTD,
  "ip_address" VARCHAR(255) ENCODE ZSTD NOT NULL,
  "proxy" VARCHAR(255) ENCODE ZSTD,
  "referrer" VARCHAR(4095) ENCODE ZSTD,
  "referrer_urlhost_derived" VARCHAR(255) ENCODE ZSTD,
  "referrer_medium" VARCHAR(255) ENCODE ZSTD,
  "return_size" DOUBLE PRECISION ENCODE ZSTD,
  "status_code" VARCHAR(255) ENCODE ZSTD,
  "user_agent_http_request_header" VARCHAR(4095) ENCODE ZSTD,
  "is_efficiencybc_dev" BOOL ENCODE ZSTD,
  "is_government" BOOL ENCODE ZSTD,
  "is_mobile" BOOL ENCODE ZSTD,
  "device" VARCHAR(255) ENCODE ZSTD,
  "os_family" VARCHAR(255) ENCODE ZSTD,
  "os_version" VARCHAR(255) ENCODE ZSTD,
  "browser_family" VARCHAR(255) ENCODE ZSTD,
  "browser_version" VARCHAR(255) ENCODE ZSTD
);

GRANT SELECT ON workbc.asset_downloads_derived TO "looker";
