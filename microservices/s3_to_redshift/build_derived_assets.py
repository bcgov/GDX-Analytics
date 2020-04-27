###################################################################
# Script Name   : build_derived_assets.py
#
# Description   : Creates asset_downloads_derived, which is a
#               : persistent derived table (PDT)
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the pgpass user microservice
#
#               : export pguser=<<database_username>>
#               : export pgpass=<<database_password>>
#
#
# Usage         : python build_derived_assets.py
#
#               : This microservice can be run after asset_data_to_redshift.py
#               : has run using the *_assets.json config file and updated the
#               : {{schema}}.asset_downloads table.
#

import os
import logging
import sys
import json  # to read json config files
import psycopg2

# Logging has two handlers: INFO to stdout and DEBUG to a file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
handler = logging.FileHandler(os.path.join('logs', log_filename),
                              "a", encoding=None, delay="true")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# check that configuration file was passed as argument
if len(sys.argv) != 2:
    print('Usage: python build_derived_assets.py config.json')
    sys.exit(1)
configfile = sys.argv[1]
# confirm that the file exists
if os.path.isfile(configfile) is False:
    print("Invalid file name {}".format(configfile))
    sys.exit(1)
# open the confifile for reading
with open(configfile) as f:
    data = json.load(f)

schema_name = data['schema_name']
asset_host = data['asset_host']
asset_source = data['asset_source']
asset_scheme_and_authority = data['asset_scheme_and_authority']


conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=os.environ['pguser'],
           password=os.environ['pgpass'])

query = r'''
    BEGIN;
    SET SEARCH_PATH TO '{schema_name}';
    DROP TABLE IF EXISTS asset_downloads_derived;
    CREATE TABLE asset_downloads_derived AS
    SELECT '{asset_scheme_and_authority}' ||
        SPLIT_PART(assets.request_string, ' ',2)
        AS asset_url,
    assets.date_timestamp::TIMESTAMP,
    assets.ip AS ip_address,
    assets.request_response_time,
    assets.referrer,
    assets.return_size,
    assets.status_code,
    -- strip down the asset_url by removing host, query, etc,
    -- then use a regex to get the filename from the remaining path.
    REGEXP_SUBSTR(
        REGEXP_REPLACE(
          SPLIT_PART(
            SPLIT_PART(
              SPLIT_PART(
                asset_url, '{asset_host}' , 2),
              '?', 1),
            '#', 1),
          '(.aspx)$'),
    '([^\/]+\.[A-Za-z0-9]+)$') AS asset_file,
    -- strip down the asset_url by removing host, query, etc, then use
    -- a regex to get the file extension from the remaining path.
    CASE
      WHEN SPLIT_PART(
        REGEXP_REPLACE(
          SPLIT_PART(
            SPLIT_PART(
              SPLIT_PART(
                asset_url, '%', 1),
              '?', 1),
            '#', 1),
          '(.aspx)$'),
        '{asset_host}', 2) LIKE '%.%'
      THEN REGEXP_SUBSTR(
        SPLIT_PART(
          REGEXP_REPLACE(
            SPLIT_PART(
              SPLIT_PART(
                SPLIT_PART(
                    asset_url, '%', 1),
                '?', 1),
              '#', 1),
            '(.aspx)$'),
          '{asset_host}', 2),
        '([^\.]+$)')
      ELSE NULL
    END AS asset_ext,
    assets.user_agent_http_request_header,
    assets.request_string,
    '{asset_host}' as asset_host,
    '{asset_source}' as asset_source,
    CASE
        WHEN assets.referrer is NULL THEN TRUE
        ELSE FALSE
        END AS direct_download,
    CASE
        WHEN
            REGEXP_SUBSTR(assets.referrer, '[^/]+\\\.[^/:]+') <> '{asset_host}'
        THEN TRUE
        ELSE FALSE
        END AS offsite_download,
    CASE
        WHEN assets.ip LIKE '184.69.13.%'
        OR assets.ip LIKE '184.71.25.%' THEN TRUE
        ELSE FALSE
        END AS is_efficiencybc_dev,
    CASE WHEN assets.ip LIKE '142.22.%'
        OR assets.ip LIKE '142.23.%'
        OR assets.ip LIKE '142.24.%'
        OR assets.ip LIKE '142.25.%'
        OR assets.ip LIKE '142.26.%'
        OR assets.ip LIKE '142.27.%'
        OR assets.ip LIKE '142.28.%'
        OR assets.ip LIKE '142.29.%'
        OR assets.ip LIKE '142.30.%'
        OR assets.ip LIKE '142.31.%'
        OR assets.ip LIKE '142.32.%'
        OR assets.ip LIKE '142.33.%'
        OR assets.ip LIKE '142.34.%'
        OR assets.ip LIKE '142.35.%'
        OR assets.ip LIKE '142.36.%'
        THEN TRUE
        ELSE FALSE
        END AS is_government,
    CASE WHEN assets.user_agent_http_request_header LIKE '%Mobile%' THEN TRUE
        ELSE FALSE
        END AS is_mobile,
    CASE
        WHEN assets.user_agent_http_request_header
            LIKE '%Mobile%' THEN 'Mobile'
        WHEN assets.user_agent_http_request_header
            LIKE '%Tablet%' THEN 'Tablet'
        WHEN assets.user_agent_http_request_header
            ILIKE '%neo-x%' THEN 'Digital media receiver'
        WHEN assets.user_agent_http_request_header ILIKE '%playstation%'
            OR  assets.user_agent_http_request_header ILIKE '%nintendo%'
            OR  assets.user_agent_http_request_header ILIKE '%xbox%'
            THEN 'Game Console'
        WHEN assets.user_agent_http_request_header LIKE '%Macintosh%'
            OR assets.user_agent_http_request_header LIKE '%Windows NT%'
            THEN 'Computer'
        ELSE 'Unknown'
        END AS device,
    assets.os_family,
    assets.os_version,
    assets.browser_family,
    assets.browser_version,
    -- Redshift requires the two extra escaping slashes for the backslash in
    -- the regex for referrer_urlhost.
    REGEXP_SUBSTR(assets.referrer, '[^/]+\\\.[^/:]+')
    AS referrer_urlhost_derived,
    assets.referrer_medium,
    SPLIT_PART(
        SPLIT_PART(
            REGEXP_SUBSTR(
                REGEXP_REPLACE(assets.referrer,'.*:\/\/'), '/.*'), '?', 1),
                '#', 1)
    AS referrer_urlpath,
    CASE
        WHEN POSITION ('?' IN referrer) > 0
        THEN SUBSTRING (referrer_urlpath,POSITION ('?' IN referrer_urlpath) +1)
        ELSE ''
        END AS referrer_urlquery,
    SPLIT_PART(assets.referrer, ':', 1) AS referrer_urlscheme,
    CASE
        WHEN referrer_urlhost_derived = 'www2.gov.bc.ca'
            AND referrer_urlpath = '/gov/search'
        THEN 'https://www2.gov.bc.ca/gov/search?' || referrer_urlquery
        WHEN referrer_urlhost_derived = 'www2.gov.bc.ca'
            AND referrer_urlpath = '/enSearch/sbcdetail'
        THEN 'https://www2.gov.bc.ca/enSearch/sbcdetail?' ||
            REGEXP_REPLACE(referrer_urlquery,'([^&]*&[^&]*)&.*','$1')
        WHEN referrer_urlpath IN (
            '/solutionexplorer/ES_Access',
            '/solutionexplorer/ES_Question',
            '/solutionexplorer/ES_Result',
            '/solutionexplorer/ES_Action')
            AND LEFT(referrer_urlquery, 3) = 'id='
        THEN referrer_urlscheme || '://' || referrer_urlhost_derived  ||
            referrer_urlpath ||'?' ||
            SPLIT_PART(referrer_urlquery,'&',1)
        ELSE referrer_urlscheme || '://' || referrer_urlhost_derived  ||
            REGEXP_REPLACE(
                referrer_urlpath,
                'index.(html|htm|aspx|php|cgi|shtml|shtm)$','')
        END AS page_referrer_display_url,
    LOWER(asset_url) AS asset_url_case_insensitive,
    REGEXP_REPLACE(asset_url, '\\?.*$') AS asset_url_nopar,
    LOWER(
        REGEXP_REPLACE(asset_url, '\\?.*$'))
    AS asset_url_nopar_case_insensitive,
    REGEXP_REPLACE(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                asset_url_nopar_case_insensitive,
                '/((index|default)\\.(htm|html|cgi|shtml|shtm))|(default\\.(asp|aspx))/{{0,}}$','/'),
            '//$','/'),
        '%20',' ')
    AS truncated_asset_url_nopar_case_insensitive
    FROM {schema_name}.asset_downloads AS assets
    -- Asset files not in the getmedia folder for workbc must be filtered out
    WHERE asset_url NOT LIKE 'https://www.workbc.ca%'
    OR (request_string LIKE '%getmedia%'
        AND asset_url LIKE 'https://www.workbc.ca%');
    ALTER TABLE asset_downloads_derived OWNER TO microservice;
    GRANT SELECT ON asset_downloads_derived TO looker;
    COMMIT;
'''.format(schema_name=schema_name,
           asset_host=asset_host,
           asset_source=asset_source,
           asset_scheme_and_authority=asset_scheme_and_authority)

with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        except psycopg2.Error:
            logger.exception(
                ('Error: failed to execute the transaction '
                 'to prepare the %s.asset_downloads_derived PDT'), schema_name)
        else:
            logger.info(
                ('Success: executed the transaction '
                 'to prepare the %s.asset_downloads_derived PDT'), schema_name)
