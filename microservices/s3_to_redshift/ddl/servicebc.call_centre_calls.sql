CREATE TABLE IF NOT EXISTS servicebc.call_centre_calls (
  "ID" INTEGER ENCODE ZSTD NOT NULL PRIMARY KEY,
  "Datekey" DATE ENCODE ZSTD,
  "TimeKey" INTEGER ENCODE ZSTD,
  "UWFAgentID" INTEGER ENCODE ZSTD,
  "Instance" VARCHAR(20) ENCODE ZSTD,
  "ContactReason" VARCHAR(50) ENCODE ZSTD,
  "ContactReasonDetail" VARCHAR(50) ENCODE ZSTD,
  "WrapTime" FLOAT ENCODE ZSTD,
  "ActiveTime" FLOAT ENCODE ZSTD,
  "PresentingTime" FLOAT ENCODE ZSTD,
  "SuspendTime" FLOAT ENCODE ZSTD,
  "SuspendCount" INTEGER ENCODE ZSTD,
  "TSFFlag" INTEGER ENCODE ZSTD
);

GRANT SELECT ON servicebc.call_centre_calls TO "looker";
GRANT SELECT ON servicebc.call_centre_calls TO "datamodeling";
