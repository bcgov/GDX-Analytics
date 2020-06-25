CREATE SCHEMA IF NOT EXISTS cmslite;

-- LOOKUP TABLE FOR VALUES

CREATE TABLE IF NOT EXISTS cmslite.content_types (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
);

CREATE TABLE IF NOT EXISTS cmslite.mbcterms_subject_categories (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
);

CREATE TABLE IF NOT EXISTS cmslite.dcterms_subjects (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
);

CREATE TABLE IF NOT EXISTS cmslite.dcterms_languages (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
);

--- Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.security_classifications (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
); */

--- Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.security_labels (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
); */

CREATE TABLE IF NOT EXISTS cmslite.audiences (
    "id"      BIGINT          NOT NULL,
    "value"   VARCHAR(255)     NOT NULL
);

-- LOOKUP TABLES (MANY-TO-MANY)

CREATE TABLE IF NOT EXISTS cmslite.metadata_content_types (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
);

CREATE TABLE IF NOT EXISTS cmslite.metadata_subject_categories (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
);

CREATE TABLE IF NOT EXISTS cmslite.metadata_subjects (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
);

CREATE TABLE IF NOT EXISTS cmslite.metadata_languages (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
);

--- Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.metadata_security_classifications (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
); */

--- Table no longer in cmslite schema
/* CREATE TABLE IF NOT EXISTS cmslite.metadata_security_labels (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
); */

CREATE TABLE IF NOT EXISTS cmslite.metadata_audiences (
    "node_id"   VARCHAR(255)    NOT NULL,
    "id"        BIGINT          NOT NULL
);

-- METADATA TABLE FOR NODE_ID RECORDS
-- NODE_ID should be primary key, however RedShift doesn't seem to enforce this.

-- Old table
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

-- New table
-- Not sure if node_id needs NOT NULL but kept it as it was in the old table above
CREATE TABLE IF NOT EXISTS cmslite.metadata (
	"node_id"						VARCHAR(255)	NOT NULL,
	"inherited_security_group"		VARCHAR(1023),
	"defined_security_groups"		VARCHAR(1023),
	"security_label"				VARCHAR(255),
	"security_classification"		VARCHAR(255),
	"exclude_from_search_engines"	VARCHAR(10),
	"hide_from_navigation"			VARCHAR(10),
	"exclude_from_ia" 				VARCHAR(10),
	"node_level" 					VARCHAR(10),
	"modified_by" 					VARCHAR(255),
	"created_by" 					VARCHAR(255),
	"published_by" 					VARCHAR(255),
	"page_status" 					VARCHAR(255),
	"language_code"					VARCHAR(256),
	"language_name"					VARCHAR(256),
	"site_id"						VARCHAR(255),
	"sitekey"						VARCHAR(255),
	"eng_nav_title"					VARCHAR(2047),
	"nav_title"						VARCHAR(2047),
	"title"							VARCHAR(2047),
	"dcterms_creator"				VARCHAR(4095),
	"synonyms"						VARCHAR(1023),
	"page_type"						VARCHAR(255),
	"description"					VARCHAR(1023),
	"keywords"						VARCHAR(1023),
	"hr_url"						VARCHAR(2047),
	"ancestor_nodes"				VARCHAR(4095),
	"parent_node_id"				VARCHAR(255),
	"publication_date"				TIMESTAMP,
	"moved_date"					TIMESTAMP,
	"locked_date"					TIMESTAMP,
	"published_date"				TIMESTAMP,
	"updated_date"					TIMESTAMP,
	"created_date"					TIMESTAMP,
	"modified_date"					TIMESTAMP
};
