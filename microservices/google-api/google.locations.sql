DROP TABLE IF EXISTS google.locations_gdxdsd2333;
CREATE TABLE IF NOT EXISTS google.locations_gdxdsd2333 (
  date   DATE,
  client   VARCHAR(255)    ENCODE ZSTD,
  location   VARCHAR(255)    ENCODE ZSTD,
  location_id   VARCHAR(255)    ENCODE ZSTD,
  views_search   INTEGER,
  views_maps   INTEGER,
  queries_indirect   INTEGER,
  queries_direct   INTEGER,
  photos_views_merchant   INTEGER,
  photos_views_customers   INTEGER,
  photos_count_merchant   INTEGER,
  photos_count_customers   INTEGER,
  local_post_views_search   INTEGER,
  actions_website   INTEGER,
  actions_phone   INTEGER,
  actions_driving_directions   INTEGER
);
ALTER TABLE google.locations_gdxdsd2333 OWNER TO microservice;
GRANT SELECT ON TABLE google.locations_gdxdsd2333 TO LOOKER;
