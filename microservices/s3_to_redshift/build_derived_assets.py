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
from lib.redshift import RedShift
from datetime import datetime
from tzlocal import get_localzone
from pytz import timezone
import lib.logs as log

# Set local timezone and get time
local_tz = get_localzone()
yvr_tz = timezone('America/Vancouver')
yvr_dt_start = (yvr_tz
                .normalize(datetime.now(local_tz)
                           .astimezone(yvr_tz)))

logger = logging.getLogger(__name__)
log.setup()
logging.getLogger("RedShift").setLevel(logging.WARNING)


# Provides exit code and logs message
def clean_exit(code, message):
    """Exits with a logger message and code"""
    logger.debug('Exiting with code %s : %s', str(code), message)
    sys.exit(code)


if not os.path.exists('logs'):
    os.makedirs('logs')

# check that configuration file was passed as argument
if len(sys.argv) != 2:
    print('Usage: python build_derived_assets.py config.json')
    clean_exit(1, 'Bad command use.')
configfile = sys.argv[1]
# confirm that the file exists
if os.path.isfile(configfile) is False:
    print("Invalid file name {}".format(configfile))
    clean_exit(1, 'Invalid file name.')
# open the confifile for reading
with open(configfile) as f:
    data = json.load(f)


def report(data):
    '''reports out the data from the main program loop'''
    # if no objects were processed; do not print a report
    if data["objects"] == 0:
        return
    print(f'report {__file__}:')
    print(f'\nObjects to process: {data["objects"]}')
    print(f'Objects that failed to process: {data["failed"]}')
    print(f'Objects loaded to Redshift: {data["loaded"]}')
    print(
        "\nList of objects successfully fully ingested from S3, processed, "
        "loaded to S3 ('good'), and copied to Redshift:")
    if data['good_list']:
        for i, meta in enumerate(data['good_list']):
            print(f"{i}: {meta.key}")
    else:
        print('None')
    print('\nList of objects that failed to process:')
    if data['bad_list']:
        for i, meta in enumerate(data['bad_list']):
            print(f"{i}: {meta.key}")
    else:
        print('None')
    print('\nList of objects that were not processed due to early exit:')
    if data['incomplete_list']:
        for i, meta in enumerate(data['incomplete_list']):
            print(f"{i}: {meta.key}")
    else:
        print("None")

    # get times from system and convert to Americas/Vancouver for printing
    yvr_dt_end = (yvr_tz
                  .normalize(datetime.now(local_tz)
                             .astimezone(yvr_tz)))
    print(
        '\nMicroservice started at: '
        f'{yvr_dt_start.strftime("%Y-%m-%d %H:%M:%S%z (%Z)")}, '
        f'ended at: {yvr_dt_end.strftime("%Y-%m-%d %H:%M:%S%z (%Z)")}, '
        f'elapsing: {yvr_dt_end - yvr_dt_start}.')


schema_name = data['schema_name']
asset_host = data['asset_host']
asset_source = data['asset_source']
asset_scheme_and_authority = data['asset_scheme_and_authority']
dbtable = data['dbtable']


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
    INSERT INTO asset_downloads_derived (
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
                REGEXP_SUBSTR(assets.referrer, '[^/]+\\\.[^/:]+')
                <> '{asset_host}'
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
        CASE WHEN assets.user_agent_http_request_header LIKE '%Mobile%'
            THEN TRUE
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
        -- Redshift requires the two extra escaping slashes for the
        -- backslash in the regex for referrer_urlhost.
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
            THEN SUBSTRING (referrer,
                            POSITION ('?' IN referrer) +1)
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
        -- Asset files not in the getmedia folder for workbc must
        -- be filtered out
        WHERE '{asset_scheme_and_authority}' NOT IN (
            'https://www.workbc.ca',
            'http://apps.britishcolumbia.ca/',
            'https://www.britishcolumbia.ca',
            'https://www.hellobc.com.cn',
            'https://www.britishcolumbia.jp',
            'https://www.britishcolumbia.kr')
        OR (request_string LIKE '%getmedia%'
            AND asset_url LIKE 'https://www.workbc.ca%')
        OR (request_string LIKE '%getmedia%'
            AND asset_source LIKE 'TIBC')
        OR (request_string LIKE '%TradeBCPortal/media%'
            AND asset_source LIKE 'TIBC')
    );
    COMMIT;
'''.format(schema_name=schema_name,
           asset_host=asset_host,
           asset_source=asset_source,
           asset_scheme_and_authority=asset_scheme_and_authority)

# Reporting variables
report_stats = {
    'objects': 1,
    'failed': 0,
    'loaded': 0,
    'good_list': [],
    'bad_list': [],
    'incomplete_list': []
}


# Execute the transaction against Redshift using local lib redshift module
table_name = dbtable
spdb = RedShift.snowplow(table_name)
if spdb.query(query):
    report_stats['loaded'] += 1
    report_stats['good_list'].append(table_name)
else:
    report_stats['failed'] += 1
    report_stats['bad'] += 1
    report_stats['bad_list'].append(table_name)
    report_stats['incomplete_list'].remove(table_name)
    clean_exit(1, f'Query failed to load {table_name}, '
               'no further processing.')
spdb.close_connection()

report(report_stats)
clean_exit(0, 'Finished all processing cleanly.')
