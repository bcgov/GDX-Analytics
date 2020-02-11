CREATE TABLE IF NOT EXISTS esb.se_pathways
(
  "id" VARCHAR(20) ENCODE ZSTD NOT NULL,
  "type" VARCHAR(255) ENCODE ZSTD,
  "pathway" VARCHAR(255) ENCODE ZSTD,
  "order" INT ENCODE ZSTD,
  "title" VARCHAR(255) ENCODE ZSTD
);

GRANT SELECT ON servicebc.call_centre TO "looker";
