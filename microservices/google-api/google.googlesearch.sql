DROP TABLE IF EXISTS google.googlesearch;
CREATE TABLE IF NOT EXISTS google.googlesearch (
    site        VARCHAR(255)    ENCODE ZSTD,
    date        DATE            ENCODE AZ64,
    query       VARCHAR(2048)   ENCODE ZSTD,
    country     VARCHAR(255)    ENCODE ZSTD,
    device      VARCHAR(255)    ENCODE ZSTD,
    page        VARCHAR(2047)   ENCODE ZSTD,
    position    FLOAT           ENCODE ZSTD,
    clicks      INTEGER         ENCODE ZSTD,
    ctr         FLOAT           ENCODE ZSTD,
    impressions INTEGER         ENCODE ZSTD
);
ALTER TABLE google.googlesearch OWNER TO microservice;
GRANT SELECT ON TABLE google.googlesearch TO LOOKER; 
