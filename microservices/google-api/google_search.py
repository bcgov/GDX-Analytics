"""Google Search Console API Loader Script"""
###################################################################
# Script Name   : google_search.py
#
#
# Description   : A script to access the Google Search Console
#               : api, download analytcs info and dump to a CSV in S3
#               : The resulting file is loaded to Redshift and then
#               : available to Looker through the project google_api.
#               : Calls span 30 days or less, and calls begin from
#               : the day after the latest data loaded into Redshift,
#               : or 16 months ago, or on the date specified in the
#               : file referenced by the GOOGLE_MICROSERVICE_CONFIG
#               : environment variable. The config JSONschema is
#               : defined in the google-api README.md file.
#
# Requirements  : Install python libraries: httplib2, oauth2client
#               : google-api-python-client
#               :
#               : You will need API credensials set up. If you don't have
#               : a project yet, follow these instructions. Otherwise,
#               : place your credentials.json file in the location defined
#               : below.
#               :
#               : ------------------
#               : To set up the Google end of things, following this:
#   : https://developers.google.com/api-client-library/python/start/get_started
#               : the instructions are:
#               :
#               :
#               : Set up a Google account linked to an IDIR service account
#               : Create a new project at
#               : https://console.developers.google.com/projectcreate
#               :
#               : Enable the API via "+ Enable APIs and Services" by choosing:
#               :      "Google Search Console API"
#               :
#               : Click "Create Credentials" selecting:
#               :   Click on the small text to select that you want to create
#               :   a "client id". You will have to configure a consent screen.
#               :   You must provide an Application name, and
#               :   under "Scopes for Google APIs" add the scopes:
#               :   "../auth/webmasters" and "../auth/webmasters.readonly".
#               :
#               :   After you save, you will have to pick an application type.
#               :   Choose Other, and provide a name for this OAuth client ID.
#               :
#               :   Download the JSON file and place it in your directory as
#               :   "credentials.json" as described by the variable below
#               :
#               :   When you first run it, it will ask you do do an OAUTH
#               :   validation, which will create a file "credentials.dat",
#               :   saving that auhtorization.


import re
from datetime import date, datetime, timedelta
from time import sleep
import json
import argparse
import sys       # to read command line parameters
import os.path   # file handling
import io        # file and stream handling
import logging
import boto3     # For Amazon S3 IO
import httplib2
from oauth2client.client import HttpAccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as GoogleHttpError
import psycopg2  # For Amazon Redshift IO
import lib.logs as log


# Ctrl+C
def signal_handler(signal, frame):
    logger.debug('Ctrl+C pressed!')
    sys.exit(0)


logger = logging.getLogger(__name__)
log.setup()


def last_loaded(s):
    """Check for a sites last loaded date in Redshift"""
    # Load the Redshift connection
    con = psycopg2.connect(conn_string)
    cursor = con.cursor()
    # query the latest date for any search data on this site loaded to redshift
    q = f"SELECT MAX(DATE) FROM {dbtable} WHERE site = '{s}'"
    cursor.execute(q)
    # get the last loaded date
    lld = (cursor.fetchall())[0][0]
    # close the redshift connection
    cursor.close()
    con.commit()
    con.close()
    return lld


# the latest available Google API data is two less than the query date (today)
latest_date = date.today() - timedelta(days=2)

# Command line arguments
parser = argparse.ArgumentParser(
    parents=[tools.argparser],
    description='GDX Analytics ETL utility for Google search.')
parser.add_argument('-o', '--cred', help='OAuth Credentials JSON file.')
parser.add_argument('-a', '--auth', help='Stored authorization dat file.')
parser.add_argument('-c', '--conf', help='Microservice configuration file.')
flags = parser.parse_args()
flags.noauth_local_webserver = True

CLIENT_SECRET = flags.cred
AUTHORIZATION = flags.auth
CONFIG = flags.conf

# calling the Google API. If credentials.dat is not yet generated
# then brower based Google Account validation will be required
API_NAME = 'searchconsole'
API_VERSION = 'v1'
DISCOVERY_URI = ('https://www.googleapis.com/'
                 'discovery/v1/apis/webmasters/v3/rest')

flow_scope = 'https://www.googleapis.com/auth/webmasters.readonly'
flow = flow_from_clientsecrets(
    CLIENT_SECRET,
    scope=flow_scope,
    redirect_uri='urn:ietf:wg:oauth:2.0:oob')

flow.params['access_type'] = 'offline'
flow.params['approval_prompt'] = 'force'

storage = Storage(AUTHORIZATION)
credentials = storage.get()

if credentials is not None and credentials.access_token_expired:
    try:
        h = httplib2.Http()
        credentials.refresh(h)
    except HttpAccessTokenRefreshError:
        pass

if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)

http = credentials.authorize(httplib2.Http())

# disabling cache-discovery to suppress warnings on:
# ImportError: file_cache is unavailable when using oauth2client >= 4.0.0
# https://stackoverflow.com/questions/40154672/importerror-file-cache-is-unavailable-when-using-python-client-for-google-ser
service = build(API_NAME,
                API_VERSION,
                http=http,
                discoveryServiceUrl=DISCOVERY_URI,
                cache_discovery=False)

# Read configuration file from env parameter
with open(CONFIG) as f:
    config = json.load(f)

sites = config['sites']
bucket = config['bucket']
dbtable = config['dbtable']
config_source = config['source']
config_directory = config['directory']

# set up the S3 resource
client = boto3.client('s3', region_name='ca-central-1')
resource = boto3.resource('s3')

# set up the Redshift connection
dbname = 'snowplow'
host = 'redshift.analytics.gov.bc.ca'
port = '5439'
user = os.environ['pguser']
password = os.environ['pgpass']
conn_string = (f"dbname='{dbname}' host='{host}' port='{port}' "
               f"user='{user}' password={password}")

# each site in the config list of sites gets processed in this loop
for site_item in sites:
    # read the config for the site name and default start date if specified
    site_name = site_item["name"]

    # get the last loaded date.
    # may be None if this site has not previously been loaded into Redshift)
    last_loaded_date = last_loaded(site_name)

    # if the last load is 2 days old, there will be no new data in Google
    if last_loaded_date is not None and last_loaded_date >= latest_date:
        continue

    # determine default start
    start_date_default = site_item.get("start_date_default")
    # if no start date is specified in the config, set it to 16 months ago
    if start_date_default is None:
        start_date_default = date.today() - timedelta(days=480)
    # if a start date was specified, it has to be formatted into a date type
    else:
        start_date_default = datetime.strptime(
            start_date_default, '%Y-%m-%d').date()

    # Load 30 days at a time until the data in Redshift has
    # caught up to the most recently available data from Google
    while last_loaded_date is None or last_loaded_date < latest_date:

        # if there isn't data in Redshift for this site,
        # start at the start_date_default set earlier
        if last_loaded_date is None:
            start_dt = start_date_default
        # offset start_dt one day ahead of last Redshift-loaded data
        else:
            start_dt = last_loaded_date + timedelta(days=1)

        # if the start_dt is the latest date, there is no new data: skip site
        if start_dt == latest_date:
            break

        # end_dt will be the lesser of:
        # (up to) 1 month ahead of start_dt OR (up to) two days before now.
        end_dt = min(start_dt + timedelta(days=30), latest_date)

        # set the file name that will be written to S3
        site_clean = re.sub(r'^https?:\/\/', '', re.sub(r'\/$', '', site_name))
        outfile = f"googlesearch-{site_clean}-{start_dt}-{end_dt}.csv"
        outfile = f"googlesearch-{site_clean}-{start_dt}-{end_dt}.csv"
        object_key = f"{config_source}/{config_directory}/{outfile}"

        # site_list_response = service.sites().list().execute()

        # prepare stream
        stream = io.StringIO()

        # site is prepended to the response from the Google Search API
        outrow = (u"site|date|query|country|device|"
                  "page|position|clicks|ctr|impressions\n")
        stream.write(outrow)

        # Limit each query to 20000 rows. If there are more than 20000 rows
        # in a given day, it will split the query up.
        rowlimit = 20000
        index = 0

        def daterange(date1, date2):
            """yields a generator of all dates from date1 to date2"""
            for n in range(int((date2 - date1).days)+1):
                yield date1 + timedelta(n)

        search_analytics_response = ''

        # loops on each date from start date to the end date, inclusive
        for date_in_range in daterange(start_dt, end_dt):
            # A wait time of 250ms each query reduces chance of HTTP 429 error
            # "Rate Limit Exceeded", handled below
            wait_time = 0.25
            sleep(wait_time)

            index = 0
            while (index == 0 or ('rows' in search_analytics_response)):
                logger.debug('%s %s', str(date_in_range), index)

                # The request body for the Google Search API query
                bodyvar = {
                    "aggregationType": 'auto',
                    "startDate": str(date_in_range),
                    "endDate": str(date_in_range),
                    "dimensions": [
                        "date",
                        "query",
                        "country",
                        "device",
                        "page"
                        ],
                    "rowLimit": rowlimit,
                    "startRow": index * rowlimit
                    }

                # This query to the Google Search API may eventually yield an
                # HTTP response code of 429, "Rate Limit Exceeded".
                # The handling attempt below will increase the wait time on
                # each re-attempt up to 10 times.

                # As a scheduled job, ths microservice will restart after the
                # last successful load to Redshift.
                retry = 1
                while True:
                    try:
                        search_analytics_response = service.searchanalytics() \
                            .query(siteUrl=site_name, body=bodyvar).execute()
                    except GoogleHttpError:
                        if retry == 11:
                            logger.error(("Failing with HTTP error after 10 "
                                          "retries with query time easening."))
                            sys.exit()
                        wait_time = wait_time * 2
                        logger.warning(
                            "retrying site %s: %s with wait time %s",
                            site_name, retry, wait_time)
                        retry = retry + 1
                        sleep(wait_time)
                    else:
                        break

                index = index + 1

                if 'rows' in search_analytics_response:
                    for row in search_analytics_response['rows']:
                        outrow = site_name + "|"
                        for key in row['keys']:
                            # for now, we strip | from searches
                            key = re.sub(r'\|', '', key)
                            # for now, we strip \\ from searches
                            key = re.sub('\\\\', '', key)
                            outrow = outrow + key + "|"
                        outrow = \
                            outrow + str(row['position']) + "|" + \
                            re.sub(r'\.0', '', str(row['clicks'])) + "|" + \
                            str(row['ctr']) + "|" + \
                            re.sub(r'\.0', '', str(row['impressions'])) + "\n"
                        stream.write(outrow)

        # Write the stream to an outfile in the S3 bucket with naming
        # like "googlesearch-sitename-startdate-enddate.csv"
        resource.Bucket(bucket).put_object(Key=object_key,
                                           Body=stream.getvalue())
        logger.debug('PUT_OBJECT: %s:%s', outfile, bucket)
        object_summary = resource.ObjectSummary(bucket, object_key)
        logger.debug('OBJECT LOADED ON: %s, OBJECT SIZE: %s',
                     object_summary.last_modified, object_summary.size)

        # Prepare the Redshift query
        logquery = (
            f"COPY {dbtable} FROM 's3://{bucket}/{object_key}' CREDENTIALS "
            "'aws_access_key_id={AWS_ACCESS_KEY_ID};aws_secret_access_key="
            "{AWS_SECRET_ACCESS_KEY}' REGION AS 'ca-central-1' "
            "IGNOREHEADER AS 1 MAXERROR AS 0 "
            "DELIMITER '|' NULL AS '-' ESCAPE;")
        query = logquery.format(
            AWS_ACCESS_KEY_ID=os.environ['AWS_ACCESS_KEY_ID'],
            AWS_SECRET_ACCESS_KEY=os.environ['AWS_ACCESS_KEY_ID'])
        logger.debug(logquery)

        # Load into Redshift
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                # if the DB call fails, print error and place file in /bad
                except psycopg2.Error:
                    logger.exception(
                        "Loading failed: %s index %s on object key %s.",
                        site_name, str(index),
                        object_key.split('/')[-1])
                else:
                    logger.info(
                        "Loaded: %s index %d for %s on object key %s",
                        site_name, str(index),
                        object_key.split('/')[-1])
        # if we didn't add any new rows, set last_loaded_date to latest_date to
        # break the loop, otherwise, set it to the last loaded date
        if last_loaded_date == last_loaded(site_name):
            last_loaded_date = latest_date
        else:
            # refresh last_loaded with the most recent load date
            last_loaded_date = last_loaded(site_name)


# # This query will INSERT data that is the result of a JOIN into
# # cmslite.google_pdt, a persistent dereived table which facilitating the LookML
# query = """
# -- perform this as a transaction.
# -- Either the whole query completes, or it leaves the old table intact
# BEGIN;
# DROP TABLE IF EXISTS cmslite.google_pdt_scratch;
# DROP TABLE IF EXISTS cmslite.google_pdt_old;
#
# CREATE TABLE IF NOT EXISTS cmslite.google_pdt_scratch (
#         "site"          VARCHAR(255),
#         "date"          date,
#         "query"         VARCHAR(2048),
#         "country"       VARCHAR(255),
#         "device"        VARCHAR(255),
#         "page"          VARCHAR(2047),
#         "position"      FLOAT,
#         "clicks"        DECIMAL,
#         "ctr"           FLOAT,
#         "impressions"   DECIMAL,
#         "node_id"       VARCHAR(255),
#         "page_urlhost"  VARCHAR(255),
#         "title"         VARCHAR(2047),
#         "theme_id"      VARCHAR(255),
#         "subtheme_id"   VARCHAR(255),
#         "topic_id"      VARCHAR(255),
#         "theme"         VARCHAR(2047),
#         "subtheme"      VARCHAR(2047),
#         "topic"         VARCHAR(2047)
# );
# ALTER TABLE cmslite.google_pdt_scratch OWNER TO microservice;
# GRANT SELECT ON cmslite.google_pdt_scratch TO looker;
#
# INSERT INTO cmslite.google_pdt_scratch
#       SELECT gs.*,
#           COALESCE(node_id,'') AS node_id,
#           SPLIT_PART(page, '/',3) as page_urlhost,
#           title,
#           theme_id, subtheme_id, topic_id, theme, subtheme, topic
#       FROM google.googlesearch AS gs
#       -- fix for misreporting of redirected front page URL in Google search
#       LEFT JOIN cmslite.themes AS themes ON
#         CASE WHEN page = 'https://www2.gov.bc.ca/'
#             THEN 'https://www2.gov.bc.ca/gov/content/home'
#             ELSE page
#             END = themes.hr_url
#         WHERE site NOT IN ('sc-domain:gov.bc.ca', 'sc-domain:engage.gov.bc.ca')
#             OR site = 'sc-domain:gov.bc.ca' AND page_urlhost NOT IN (
#                 'healthgateway.gov.bc.ca',
#                 'engage.gov.bc.ca',
#                 'feedback.engage.gov.bc.ca',
#                 'www2.gov.bc.ca',
#                 'www.engage.gov.bc.ca',
#                 'curriculum.gov.bc.ca',
#                 'studentsuccess.gov.bc.ca',
#                 'news.gov.bc.ca',
#                 'bcforhighschool.gov.bc.ca')
#             OR site = 'sc-domain:engage.gov.bc.ca';
#
# ALTER TABLE cmslite.google_pdt RENAME TO google_pdt_old;
# ALTER TABLE cmslite.google_pdt_scratch RENAME TO google_pdt;
# DROP TABLE cmslite.google_pdt_old;
# COMMIT;
# """
#
# # Execute the query and log the outcome
# logger.debug(query)
# with psycopg2.connect(conn_string) as conn:
#     with conn.cursor() as curs:
#         try:
#             curs.execute(query)
#         except psycopg2.Error:
#             logger.exception("Google Search PDT loading failed")
#         else:
#             logger.info("Google Search PDT loaded successfully")
