CREATE SCHEMA IF NOT EXISTS  cmslite;

CREATE TABLE IF NOT EXISTS  test.microservice_log (
    "starttime" TIMESTAMP WITHOUT TIME ZONE ENCODE LZO,
    "endtime"   TIMESTAMP WITHOUT TIME ZONE ENCODE LZO
)
DISTSTYLE AUTO;

-- DICTIONARY TABLES

CREATE TABLE IF NOT EXISTS  test.content_types (
    "id"      BIGINT        ENCODE LZO  NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.mbcterms_subject_categories (
    "id"      BIGINT        ENCODE LZO NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.dcterms_subjects (
    "id"      BIGINT        ENCODE LZO NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.dcterms_languages (
    "id"      BIGINT        ENCODE LZO NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.audiences (
    "id"      BIGINT        ENCODE LZO NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.creators (
    "id"      BIGINT        ENCODE LZO NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD NOT NULL
)
DISTSTYLE EVEN;

-- LOOKUP TABLES

CREATE TABLE IF NOT EXISTS  test.metadata_content_types (
    "node_id"   VARCHAR(255)    ENCODE LZO  NOT NULL,
    "id"        BIGINT          ENCODE DELTA NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.metadata_subject_categories (
    "node_id"   VARCHAR(255)    ENCODE LZO  NOT NULL,
    "id"        BIGINT          ENCODE DELTA NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.metadata_subjects (
    "node_id"   VARCHAR(255)    ENCODE LZO  NOT NULL,
    "id"        BIGINT          ENCODE DELTA NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.metadata_languages (
     "node_id"   VARCHAR(255)    ENCODE LZO  NOT NULL,
    "id"        BIGINT          ENCODE DELTA NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.metadata_audiences (
    "node_id"   VARCHAR(255)    ENCODE LZO  NOT NULL,
    "id"        BIGINT          ENCODE DELTA NOT NULL
)
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS  test.metadata_creators (
    "node_id"   VARCHAR(255)    ENCODE LZO  NOT NULL,
    "id"        BIGINT          ENCODE DELTA NOT NULL
)
DISTSTYLE EVEN;

-- METADATA TABLE FOR NODE_ID RECORDS

CREATE TABLE IF NOT EXISTS  test.metadata (
 "node_id"                      VARCHAR(255)                ENCODE LZO NOT NULL,
 "parent_node_id"               VARCHAR(255)                ENCODE ZSTD,
 "ancestor_nodes"               VARCHAR(4095)               ENCODE ZSTD,
 "hr_url"                       VARCHAR(2047)               ENCODE ZSTD,
 "keywords"                     VARCHAR(2048)               ENCODE ZSTD,
 "description"                  VARCHAR(1023)               ENCODE ZSTD,
 "page_type"                    VARCHAR(255)                ENCODE ZSTD,
 "synonyms"                     VARCHAR(1023)               ENCODE ZSTD,
 "dcterms_creator"              VARCHAR(4095)               ENCODE ZSTD,
 "modified_date"                TIMESTAMP WITHOUT TIME ZONE ENCODE LZO,
 "created_date"                 TIMESTAMP WITHOUT TIME ZONE ENCODE LZO,
 "updated_date"                 TIMESTAMP WITHOUT TIME ZONE ENCODE LZO,
 "published_date"               TIMESTAMP WITHOUT TIME ZONE ENCODE LZO,
 "title"                        VARCHAR(2047)               ENCODE ZSTD,
 "nav_title"                    VARCHAR(2047)               ENCODE ZSTD,
 "eng_nav_title"                VARCHAR(2047)               ENCODE ZSTD,
 "sitekey"                      VARCHAR(255)                ENCODE LZO,
 "site_id"                      VARCHAR(255)                ENCODE LZO,
 "language_name"                VARCHAR(256)                ENCODE LZO,
 "language_code"                VARCHAR(256)                ENCODE LZO,
 "page_status"                  VARCHAR(255)                ENCODE LZO,
 "published_by"                 VARCHAR(255)                ENCODE LZO,
 "created_by"                   VARCHAR(255)                ENCODE LZO,
 "modified_by"                  VARCHAR(255)                ENCODE LZO,
 "node_level"                   VARCHAR(10)                 ENCODE LZO,
 "locked_date"                  TIMESTAMP WITHOUT TIME ZONE ENCODE AZ64,
 "moved_date"                   TIMESTAMP WITHOUT TIME ZONE ENCODE AZ64,
 "exclude_from_ia"              VARCHAR(10)                 ENCODE LZO,
 "hide_from_navigation"         VARCHAR(10)                 ENCODE LZO,
 "exclude_from_search_engines"  VARCHAR(10)                 ENCODE LZO,
 "security_classification"      VARCHAR(255)                ENCODE LZO,
 "security_label"               VARCHAR(255)                ENCODE LZO,
 "publication_date"             TIMESTAMP WITHOUT TIME ZONE ENCODE AZ64,
 "defined_security_groups"      VARCHAR(2047)               ENCODE LZO,
 "inherited_security_group"     VARCHAR(1023)               ENCODE LZO
)
DISTSTYLE EVEN;

-- Grant access to microservice
GRANT ALL ON SCHEMA  test TO microservice;

-- All tables owned by microservice
ALTER TABLE  test.content_types OWNER TO microservice;
ALTER TABLE  test.mbcterms_subject_categories OWNER TO microservice;
ALTER TABLE  test.dcterms_subjects OWNER TO microservice;
ALTER TABLE  test.dcterms_languages OWNER TO microservice;
ALTER TABLE  test.audiences OWNER TO microservice;
ALTER TABLE  test.creators OWNER TO microservice;
ALTER TABLE  test.metadata_content_types OWNER TO microservice;
ALTER TABLE  test.metadata_subject_categories OWNER TO microservice;
ALTER TABLE  test.metadata_subjects OWNER TO microservice;
ALTER TABLE  test.metadata_languages OWNER TO microservice;
ALTER TABLE  test.metadata_audiences OWNER TO microservice;
ALTER TABLE  test.metadata_creators OWNER TO microservice;
ALTER TABLE  test.metadata OWNER TO microservice;
ALTER TABLE  test.microservice_log OWNER TO microservice;

-- Grant access to Looker to read the tables
GRANT USAGE ON SCHEMA  test TO looker;

GRANT SELECT ON  test.content_types TO looker;
GRANT SELECT ON  test.mbcterms_subject_categories TO looker;
GRANT SELECT ON  test.dcterms_subjects TO looker;
GRANT SELECT ON  test.dcterms_languages TO looker;
GRANT SELECT ON  test.audiences TO looker;
GRANT SELECT ON  test.creators TO looker;
GRANT SELECT ON  test.metadata_content_types TO looker;
GRANT SELECT ON  test.metadata_subject_categories TO looker;
GRANT SELECT ON  test.metadata_subjects TO looker;
GRANT SELECT ON  test.metadata_languages TO looker;
GRANT SELECT ON  test.metadata_audiences TO looker;
GRANT SELECT ON  test.metadata_creators TO looker;
GRANT SELECT ON  test.metadata TO looker;
GRANT SELECT ON  test.microservice_log TO looker;
