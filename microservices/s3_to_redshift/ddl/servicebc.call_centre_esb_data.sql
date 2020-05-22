CREATE TABLE IF NOT EXISTS servicebc.call_centre_esb_data (
  "ID" DECIMAL(13,0) NOT NULL PRIMARY KEY ENCODE ZSTD,
  "SkillGroup" VARCHAR(50) ENCODE ZSTD,
  "ContactReason" VARCHAR(50) ENCODE ZSTD,
  "ContactReasonDetail" VARCHAR(50) ENCODE ZSTD,
  "DateKey" DATE ENCODE ZSTD,
  "Interval" VARCHAR(5) ENCODE ZSTD,
  "AnsweredWithinServiceLevel" BOOLEAN ENCODE ZSTD,
  "CallPutOnHold" INTEGER ENCODE ZSTD,
  "HandleTime" FLOAT ENCODE ZSTD,
  "WaitTime" FLOAT ENCODE ZSTD,
  "WrapTime" FLOAT ENCODE ZSTD,
  "TalkTime" FLOAT ENCODE ZSTD,
  "HoldTime" FLOAT ENCODE ZSTD,
  "IncomingPhoneNumber" VARCHAR(20) ENCODE ZSTD
);

GRANT SELECT ON servicebc.call_centre_esb_data TO "looker";
GRANT SELECT ON servicebc.call_centre_esb_data TO "datamodeling";
