CREATE TABLE IF NOT EXISTS servicebc.call_centre_escalation (
  "ID" INTEGER NOT NULL PRIMARY KEY ENCODE ZSTD,
  "Group" VARCHAR(16) ENCODE ZSTD,
  "AreaOfIncidentOrRequest" VARCHAR(50) ENCODE ZSTD,
  "ReceivedDateKey" DATE ENCODE ZSTD,
  "ReceivedTimeKey" INTEGER ENCODE ZSTD,
  "CompletedDateKey" DATE ENCODE ZSTD,
  "BusinessDaysAged" INTEGER ENCODE ZSTD,
  "ResolvedWithinReportingMonth" BOOLEAN ENCODE ZSTD
);

GRANT SELECT ON servicebc.call_centre_escalation TO "looker";
GRANT SELECT ON servicebc.call_centre_escalation TO "datamodeling";
