CREATE TABLE IF NOT EXISTS servicebc.call_centre_csat (
  "ID" VARCHAR(20) ENCODE ZSTD NOT NULL PRIMARY KEY,
  "DateKey" INTEGER ENCODE ZSTD,
  "TimeKey" INTEGER ENCODE ZSTD,
  "SkillGroupChannel" VARCHAR(30) ENCODE ZSTD,
  "AltSkillGroupChannel" VARCHAR(30) ENCODE ZSTD,
  "ANI" VARCHAR(50) ENCODE ZSTD,
  "PeripheralCallType" INTEGER ENCODE ZSTD,
  "Transfered" BOOLEAN ENCODE ZSTD,
  "DigitsDialed" VARCHAR(30) ENCODE ZSTD,
  "SurveyChannel" VARCHAR(30) ENCODE ZSTD,
  "S1CSAT" NUMERIC(20,1) ENCODE ZSTD,
  "S2CSAT" NUMERIC(20,1) ENCODE ZSTD,
  "S3CSAT" NUMERIC(20,1) ENCODE ZSTD,
  "S4CSAT" NUMERIC(20,1) ENCODE ZSTD,
  "S5CSAT" NUMERIC(20,1) ENCODE ZSTD
);


GRANT SELECT ON servicebc.call_centre_csat TO "looker";
GRANT SELECT ON servicebc.call_centre_csat TO "datamodeling";
