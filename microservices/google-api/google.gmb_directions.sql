DROP TABLE IF EXISTS google.gmb_directions;
CREATE TABLE IF NOT EXISTS google.gmb_directions (
    days_aggregated   INTEGER,
    location_label    VARCHAR(255)    ENCODE ZSTD,
    location_locale   VARCHAR(255)    ENCODE ZSTD,
    location_name   VARCHAR(255)    ENCODE ZSTD,
    location_postal_code    VARCHAR(10)   ENCODE ZSTD,
    location_time_zone    VARCHAR(255)    ENCODE ZSTD,
    rank_on_query   INTEGER,
    region_count    INTEGER,
    region_label    VARCHAR(255)    ENCODE ZSTD,
    region_latitude   DECIMAL(17,14),
    region_longitude    DECIMAL(17,14),
    utc_query_date    DATE
);
ALTER TABLE google.gmb_directions OWNER TO microservice;
GRANT SELECT ON TABLE google.gmb_directions TO LOOKER;
