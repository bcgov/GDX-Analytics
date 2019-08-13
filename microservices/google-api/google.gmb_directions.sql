DROP TABLE IF EXISTS google.gmb_directions;
CREATE TABLE IF NOT EXISTS google.gmb_directions (
    days_aggregated   INTEGER,
    client_shortname   VARCHAR(255)    ENCODE ZSTD,
    location_label    VARCHAR(255)    ENCODE ZSTD,
    location_locality   VARCHAR(255)    ENCODE ZSTD,
    location_name   VARCHAR(255)    ENCODE ZSTD,
    location_postal_code    VARCHAR(10)   ENCODE ZSTD,
    location_time_zone    VARCHAR(255)    ENCODE ZSTD,
    region_label    VARCHAR(255)    ENCODE ZSTD,
    rank_on_query   INTEGER,
    region_count_seven_days    INTEGER,
    region_count_thirty_days    INTEGER,
    region_count_ninety_days    INTEGER,
    region_latitude   DECIMAL(17,14),
    region_longitude    DECIMAL(17,14),
    utc_query_date    DATE
);
ALTER TABLE google.gmb_directions OWNER TO microservice;
GRANT SELECT ON TABLE google.gmb_directions TO LOOKER;
