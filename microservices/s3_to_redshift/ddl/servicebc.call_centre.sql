CREATE TABLE IF NOT EXISTS servicebc.call_centre
( 
  "id" VARCHAR(20) ENCODE ZSTD NOT NULL,
  "skillgroup" VARCHAR(30) ENCODE ZSTD,
  "contactreason" VARCHAR(50) ENCODE ZSTD,
  "contactreasondetail" VARCHAR(50) ENCODE ZSTD,
  "datekey" timestamp without time zone ENCODE ZSTD,
  "interval" VARCHAR(5) ENCODE ZSTD,
  "answeredwithinservicelevel" BOOL ENCODE ZSTD,
  "callputonhold" BOOL ENCODE ZSTD,
  "handletime" DOUBLE PRECISION ENCODE ZSTD,
  "waittime" DOUBLE PRECISION ENCODE ZSTD,
  "wraptime" DOUBLE PRECISION ENCODE ZSTD,
  "talktime" DOUBLE PRECISION ENCODE ZSTD,
  "holdtime" DOUBLE PRECISION ENCODE ZSTD,
  "incomingphonenumber" VARCHAR(20) ENCODE ZSTD
);

GRANT SELECT ON servicebc.call_centre TO "looker";
GRANT SELECT ON servicebc.call_centre TO "datamodeling";
