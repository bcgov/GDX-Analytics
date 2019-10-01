DROP TABLE IF EXISTS google.locations;
CREATE TABLE IF NOT EXISTS google.locations (
  actions_driving_directions   INTEGER,
  actions_phone   INTEGER,
  actions_website   INTEGER,
  local_post_views_search   INTEGER,
  photos_count_customers   INTEGER,
  photos_count_merchant   INTEGER,
  photos_views_customers   INTEGER,
  photos_views_merchant   INTEGER,
  queries_direct   INTEGER,
  queries_indirect   INTEGER,
  views_maps   INTEGER,
  views_search   INTEGER,
  location_id   VARCHAR(255)    ENCODE ZSTD,
  location   VARCHAR(255)    ENCODE ZSTD,
  client   VARCHAR(255)    ENCODE ZSTD,
  date   DATE
);
ALTER TABLE google.locations OWNER TO microservice;
GRANT SELECT ON TABLE google.locations TO LOOKER;
