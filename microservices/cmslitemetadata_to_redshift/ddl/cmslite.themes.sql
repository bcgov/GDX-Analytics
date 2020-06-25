CREATE TABLE IF NOT EXISTS cmslite.themes (
	"node_id"	VARCHAR(255),
	"title"		VARCHAR(2047),
	"hr_url"	VARCHAR(2047),
	"parent_node_id" VARCHAR(255),
	"parent_title"	VARCHAR(2047),
	"theme_id"	VARCHAR(255),
	"subtheme_id"	VARCHAR(255),
	"topic_id"	VARCHAR(255),
	"theme"		VARCHAR(2047),
	"subtheme"	VARCHAR(2047),
	"topic"		VARCHAR(2047)
);      
ALTER TABLE cmslite.themes OWNER TO microservice;
GRANT SELECT ON cmslite.themes TO looker;
