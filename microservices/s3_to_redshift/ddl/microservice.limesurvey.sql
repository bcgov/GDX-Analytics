CREATE TABLE IF NOT EXISTS microservice.limesurvey
( 
  "date" TIMESTAMP ENCODE ZSTD,
  "sid" BIGINT ENCODE ZSTD,
  "active" BOOLEAN ENCODE ZSTD,	
  "expires" TIMESTAMP ENCODE ZSTD,
  "startdate" TIMESTAMP ENCODE ZSTD,
  "datecreated" TIMESTAMP ENCODE ZSTD,
  "survey_total" BIGINT ENCODE ZSTD,
  "survey_completed" BIGINT ENCODE ZSTD,
  "survey_uncompleted" BIGINT ENCODE ZSTD,
  "survey_first_complete_date" TIMESTAMP ENCODE ZSTD,
  "survey_last_complete_date" TIMESTAMP ENCODE ZSTD
);

GRANT SELECT ON microservice.limesurvey TO "looker";
