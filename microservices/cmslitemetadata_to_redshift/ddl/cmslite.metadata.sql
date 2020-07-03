CREATE SCHEMA IF NOT EXISTS cmslite;

-- LOOKUP TABLE FOR VALUES

-- SY: dbtables_dictionaries

CREATE TABLE IF NOT EXISTS cmslite.content_types (
    "id"      BIGINT		ENCODE LZO	NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD	NOT NULL
)  
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS cmslite.mbcterms_subject_categories (
    "id"      BIGINT		ENCODE LZO	NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD	NOT NULL
)  
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS cmslite.dcterms_subjects (
    "id"      BIGINT		ENCODE LZO	NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD	NOT NULL
)  
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS cmslite.dcterms_languages (
    "id"      BIGINT		ENCODE LZO	NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD	NOT NULL
)  
DISTSTYLE EVEN;

-- SY: Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.security_classifications (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
); */

-- SY: Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.security_labels (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
); */

CREATE TABLE IF NOT EXISTS cmslite.audiences (
    "id"      BIGINT		ENCODE LZO	NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD	NOT NULL
)  
DISTSTYLE EVEN;

-- SY: Added this table to reflect cmslite_gdx.json
CREATE TABLE IF NOT EXISTS cmslite.creators (
    "id"      BIGINT		ENCODE LZO	NOT NULL,
    "value"   VARCHAR(255)  ENCODE ZSTD	NOT NULL
)  
DISTSTYLE EVEN;

-- LOOKUP TABLES (MANY-TO-MANY)

-- SY: dbtables_metadata

CREATE TABLE IF NOT EXISTS cmslite.metadata_content_types (
    "node_id"   VARCHAR(255)    ENCODE LZO		NOT NULL,
    "id"        BIGINT          ENCODE DELTA	NOT NULL
)  
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS cmslite.metadata_subject_categories (
    "node_id"   VARCHAR(255)    ENCODE LZO		NOT NULL,
    "id"        BIGINT          ENCODE DELTA	NOT NULL
)  
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS cmslite.metadata_subjects (
    "node_id"   VARCHAR(255)    ENCODE LZO		NOT NULL,
    "id"        BIGINT          ENCODE DELTA	NOT NULL
)  
DISTSTYLE EVEN;

CREATE TABLE IF NOT EXISTS cmslite.metadata_languages (
     "node_id"   VARCHAR(255)    ENCODE LZO		NOT NULL,
    "id"        BIGINT          ENCODE DELTA	NOT NULL
)  
DISTSTYLE EVEN;

-- SY: Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.metadata_security_classifications (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
); */

-- SY: Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.metadata_security_labels (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
); */

CREATE TABLE IF NOT EXISTS cmslite.metadata_audiences (
    "node_id"   VARCHAR(255)    ENCODE LZO		NOT NULL,
    "id"        BIGINT          ENCODE DELTA	NOT NULL
)  
DISTSTYLE EVEN;

-- SY: Added this table to reflect cmslite_gdx.json
CREATE TABLE IF NOT EXISTS cmslite.metadata_creators (
    "node_id"   VARCHAR(255)    ENCODE LZO		NOT NULL,
    "id"        BIGINT          ENCODE DELTA	NOT NULL
)  
DISTSTYLE EVEN;

-- METADATA TABLE FOR NODE_ID RECORDS
-- NODE_ID should be primary key, however RedShift doesn't seem to enforce this.

-- SY: Old table
/* CREATE TABLE IF NOT EXISTS cmslite.metadata (
    "node_id"           VARCHAR(255)     NOT NULL,
    "keywords"          VARCHAR(1000)   ,
    "description"       VARCHAR(1000)   ,
    "page_type"         VARCHAR(255)    ,
    "synonyms"          VARCHAR(1000)   ,
    "dcterms_creator"   VARCHAR(255)    ,
    "publication_date"  DATE            ,
    "modified_date"     TIMESTAMP       ,
    "created_date"      TIMESTAMP       ,
    "updated_date"      TIMESTAMP       ,
    "published_date"    TIMESTAMP       
); */

-- SY: New table
-- SY: Not sure if node_id needs NOT NULL but kept it as it was in the old table above
-- SY: sitekey in Looker but site_key in cmslite_gdx.json??
CREATE TABLE IF NOT EXISTS cmslite.metadata (
	"node_id"						VARCHAR(255)					ENCODE	LZO		NOT NULL,
	"parent_node_id"				VARCHAR(255)					ENCODE	ZSTD,	
	"ancestor_nodes"				VARCHAR(4095)					ENCODE	ZSTD,	
	"hr_url"						VARCHAR(2047)					ENCODE	ZSTD,	
	"keywords"						VARCHAR(1023)					ENCODE	ZSTD,	
	"description"					VARCHAR(1023)					ENCODE	ZSTD,	
	"page_type"						VARCHAR(255)					ENCODE	ZSTD,	
	"synonyms"						VARCHAR(1023)					ENCODE	ZSTD,	
	"dcterms_creator"				VARCHAR(4095)					ENCODE	ZSTD,	
	"modified_date"					TIMESTAMP WITHOUT TIME ZONE		ENCODE	LZO,	
	"created_date"					TIMESTAMP WITHOUT TIME ZONE		ENCODE	LZO,	
	"updated_date"					TIMESTAMP WITHOUT TIME ZONE		ENCODE	LZO,	
	"published_date"				TIMESTAMP WITHOUT TIME ZONE		ENCODE	LZO,	
	"title"							VARCHAR(2047)					ENCODE	ZSTD,	
	"nav_title"						VARCHAR(2047)					ENCODE	ZSTD,	
	"eng_nav_title"					VARCHAR(2047)					ENCODE	ZSTD,	
	"sitekey"						VARCHAR(255)					ENCODE	LZO,	
	"site_id"						VARCHAR(255)					ENCODE	LZO,	
	"language_name"					VARCHAR(256)					ENCODE	LZO,	
	"language_code"					VARCHAR(256)					ENCODE	LZO,	
	"page_status"					VARCHAR(255)					ENCODE	LZO,	
	"published_by"					VARCHAR(255)					ENCODE	LZO,	
	"created_by"					VARCHAR(255)					ENCODE	LZO,	
	"modified_by"					VARCHAR(255)					ENCODE	LZO,	
	"node_level"					VARCHAR(10)						ENCODE	LZO,	
	"locked_date"					TIMESTAMP WITHOUT TIME ZONE		ENCODE	AZ64,	
	"moved_date"					TIMESTAMP WITHOUT TIME ZONE		ENCODE	AZ64,	
	"exclude_from_ia"				VARCHAR(10)						ENCODE	LZO,	
	"hide_from_navigation"			VARCHAR(10)						ENCODE	LZO,	
	"exclude_from_search_engines"	VARCHAR(10)						ENCODE	LZO,	
	"security_classification"		VARCHAR(255)					ENCODE	LZO,	
	"security_label"				VARCHAR(255)					ENCODE	LZO,	
	"publication_date"				TIMESTAMP WITHOUT TIME ZONE		ENCODE	AZ64,	
	"defined_security_groups"		VARCHAR(1023)					ENCODE	LZO,	
	"inherited_security_group"		VARCHAR(1023)					ENCODE	LZO
}  
DISTSTYLE EVEN;

-- All tables owned by microservice
ALTER TABLE cmslite.content_types OWNER TO microservice;
ALTER TABLE cmslite.mbcterms_subject_categories OWNER TO microservice;
ALTER TABLE cmslite.dcterms_subjects OWNER TO microservice;
ALTER TABLE cmslite.dcterms_languages OWNER TO microservice;
ALTER TABLE cmslite.audiences OWNER TO microservice;
ALTER TABLE cmslite.creators OWNER TO microservice;
ALTER TABLE cmslite.metadata_content_types OWNER TO microservice;
ALTER TABLE cmslite.metadata_subject_categories OWNER TO microservice;
ALTER TABLE cmslite.metadata_subjects OWNER TO microservice;
ALTER TABLE cmslite.metadata_languages OWNER TO microservice;
ALTER TABLE cmslite.metadata_audiences OWNER TO microservice;
ALTER TABLE cmslite.metadata_creators OWNER TO microservice;
ALTER TABLE cmslite.metadata OWNER TO microservice;

-- Grant access to Looker to read the tables
GRANT USAGE ON SCHEMA cmslite TO looker;

GRANT SELECT ON cmslite.content_types TO looker;
GRANT SELECT ON cmslite.mbcterms_subject_categories TO looker;
GRANT SELECT ON cmslite.dcterms_subjects TO looker;
GRANT SELECT ON cmslite.dcterms_languages TO looker;
GRANT SELECT ON cmslite.audiences TO looker;
GRANT SELECT ON cmslite.creators TO looker;
GRANT SELECT ON cmslite.metadata_content_types TO looker;
GRANT SELECT ON cmslite.metadata_subject_categories TO looker;
GRANT SELECT ON cmslite.metadata_subjects TO looker;
GRANT SELECT ON cmslite.metadata_languages TO looker;
GRANT SELECT ON cmslite.metadata_audiences TO looker;
GRANT SELECT ON cmslite.metadata_creators TO looker;
GRANT SELECT ON cmslite.metadata TO looker;

