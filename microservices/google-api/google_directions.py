###################################################################
# Script Name   : google_directions.py
#
#
# Description   : A script to access the Google Locations/My Business
#               : api, download driving insights for locations in a location
#               : group, then dump the output per location into an S3 Bucket
#               : where that file is then loaded to Redshift.
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
#               : Click 'Create Credentials' selecting:
#               :   Click on the small text to select that you want to create
#               :   a 'client id'. You will have to configure a consent screen.
#               :   You must provide an Application name, and
#               :   under 'Scopes for Google APIs' add the scopes:
#               :   '../auth/business.manage'.
#               :
#               :   After you save, you will have to pick an application type.
#               :   Choose Other, and provide a name for this OAuth client ID.
#               :
#               :   Download the JSON file and place it in your working
#               :   directory as 'credentials_mybusiness.json'
#               :
#               :   When you first run it, it will ask you do do an OAUTH
#               :   validation, which will create a file 'mybusiness.dat',
#               :   saving that auhtorization.
#               :
# Usage         : e.g.:
#               : $ python google_directions.py -o credentials_mybusiness.json\
#               :   -a mybusiness.dat -c google_directions.json
#
#               : the flags specified in the usage example above are:
#               : -o <OAuth Credentials JSON file>
#               : -a <Stored authorization dat file>
#               : -c <Microservice configuration file>
#               :
# References    :
# https://developers.google.com/my-business/reference/rest/v4/accounts.locations/reportInsights

import os
import sys
import json
import boto3
from botocore.exceptions import ClientError
import logging
import psycopg2
import argparse
import httplib2
import pandas as pd
from pandas import json_normalize
import googleapiclient.errors
from io import StringIO
import datetime
from googleapiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
import lib.logs as log


# Ctrl+C
def signal_handler(signal, frame):
    logger.debug('Ctrl+C pressed!')
    sys.exit(0)


# Set up logging
logger = logging.getLogger(__name__)
log.setup()


# Command line arguments
parser = argparse.ArgumentParser(
    parents=[tools.argparser],
    description='GDX Analytics ETL utility for Google My Business insights.')
parser.add_argument('-o', '--cred', help='OAuth Credentials JSON file.')
parser.add_argument('-a', '--auth', help='Stored authorization dat file')
parser.add_argument('-c', '--conf', help='Microservice configuration file.',)
parser.add_argument('-d', '--debug', help='Run in debug mode.',
                    action='store_true')
flags = parser.parse_args()

CLIENT_SECRET = flags.cred
AUTHORIZATION = flags.auth
CONFIG = flags.conf


# Parse the CONFIG file as a json object and load its elements as variables
with open(CONFIG) as f:
    config = json.load(f)

config_bucket = config['bucket']
config_dbtable = config['dbtable']
config_destination = config['destination']
config_locationGroups = config['locationGroups']
config_prefix = config['prefix']

# set up the Redshift connection
dbname = 'snowplow'
host = 'redshift.analytics.gov.bc.ca'
port = '5439'
user = os.environ['pguser']
password = os.environ['pgpass']
conn_string = (f"dbname='{dbname}' host='{host}' port='{port}' "
               f"user='{user}' password={password}")

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

# set the query date as now in UTC
query_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

# Setup OAuth 2.0 flow for the Google My Business API
API_NAME = 'mybusiness'
API_VERSION = 'v4'
DISCOVERY_URI = 'https://developers.google.com/my-business/samples/\
{api}_google_rest_{apiVersion}.json'


# Google API Access requires a browser-based authentication step to create
# the stored authorization .dat file. Forcign noauth_local_webserver to True
# allows for authentication from an environment without a browser, such as EC2.
flags.noauth_local_webserver = True


# Initialize the OAuth2 authorization flow.
# The string urn:ietf:wg:oauth:2.0:oob is for non-web-based applications.
# The prompt='consent' Retrieves the refresh token.
flow_scope = 'https://www.googleapis.com/auth/business.manage'
flow = flow_from_clientsecrets(CLIENT_SECRET, scope=flow_scope,
                               redirect_uri='urn:ietf:wg:oauth:2.0:oob',
                               prompt='consent')


# Specify the storage path for the .dat authentication file
storage = Storage(AUTHORIZATION)
credentials = storage.get()

# Refresh the access token if it expired
if credentials is not None and credentials.access_token_expired:
    try:
        h = httplib2.Http()
        credentials.refresh(h)
    except Exception:
        pass

# Acquire credentials in a command-line application
if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)

# Apply credential headers to all requests made by an httplib2.Http instance
http = credentials.authorize(httplib2.Http())

# Build the service object
service = build(
    API_NAME, API_VERSION, http=http, discoveryServiceUrl=DISCOVERY_URI)
# site_list_response = service.sites().list().execute()

# set up the S3 resource
client = boto3.client('s3')
resource = boto3.resource('s3')


# Check to see if the file has been processed already
def is_processed(key):
    filename = key[key.rfind('/')+1:]  # get the filename (after the last '/')
    goodfile = config_destination + "/good/" + key
    badfile = config_destination + "/bad/" + key
    try:
        client.head_object(Bucket=config_bucket, Key=goodfile)
    except ClientError:
        pass  # this object does not exist under the good destination path
    else:
        logger.debug("%s was processed as good already.", filename)
        return True
    try:
        client.head_object(Bucket=config_bucket, Key=badfile)
    except ClientError:
        pass  # this object does not exist under the bad destination path
    else:
        logger.debug("%s was processed as bad already.", filename)
        return True
    logger.debug("%s has not been processed.", filename)
    return False


# Location Check
# check that all locations defined in the configuration file are available
# to the authencitad account being used to access the MyBusiness API, and
# append those accounts information into a 'validated_locations' list.
validated_accounts = []
# Get the list of accounts that the Google account being used to access
# the My Business API has rights to read location insights from
# (ignoring the first one, since it is the 'self' reference account).
accounts = service.accounts().list().execute()['accounts'][1:]
# print json.dumps(accounts, indent=2)
for loc in config_locationGroups:
    # access the environment variable that sets the Account ID for this
    # Location Group, which is to be passed to the validated accounts list
    accountNumber = os.environ[f"{loc['clientShortname']}_accountid"]
    try:
        validated_accounts.append(
            next({
                'name': item['name'],
                'clientShortname': loc['clientShortname'],
                'aggregate_days': loc['aggregate_days'],
                'accountNumber': accountNumber}
                 for item
                 in accounts
                 if item['accountNumber'] == accountNumber))
    except StopIteration:
        logger.warning('No access to %s: %s. Skipping.',
                       loc['clientShortname'], accountNumber)
        continue

# iterate over ever validated account
for account in validated_accounts:
    # check the aggregate_days validity
    if 1 <= len(account["aggregate_days"]) <= 3:
        for i in account["aggregate_days"]:
            if not any(i == s for s in ["SEVEN", "THIRTY", "NINETY"]):
                logger.error(
                    "%s is an invalid aggregate option. Skipping %s.",
                    i, account['clientShortname'])
                continue
    else:
        logger.error(
            "aggregate_days on %s is invalid due to size. Skipping.",
            account['clientShortname'])
        continue

    # Set up the S3 path to write the csv buffer to
    object_key_path = f"client/{config_prefix}_{account['clientShortname']}/"

    outfile = f"gmb_directions_{account['clientShortname']}_{query_date}.csv"
    object_key = object_key_path + outfile

    if is_processed(object_key):
        logger.warning(
            ("The file: %s has already been generated "
             "and processed by this script today."), object_key)
        continue

    goodfile = f"{config_destination}/good/{object_key}"
    badfile = f"{config_destination}/bad/{object_key}"

    # Create a dataframe with dates as rows and columns according to the table
    df = pd.DataFrame()
    name = account['name']
    locations = service.accounts().locations().list(parent=name).execute()

    # Google's MyBusiness API supports querying for 10 locations at a time, so
    # here we batch locations into a list-of-lists of size batch_size (max=10).
    batch_size = 10
    location_names_list = [i['name'] for i in locations['locations']]

    # construct the label lookup and apply formatting if any
    label_lookup = {
        i['name']: {
            'locationName': i['locationName'],
            'locality': i['address']['locality'],
            'postalCode': i['address']['postalCode']
            } for i in locations['locations']}

    # batched_location_names is a list of lists
    # each list within batched_location_names contains up to 10 location names
    # each list of 10 will added pre API request, which can support responsese
    # of up to 10 locations at a time. The purpose of this is to reduce calls.
    batched_location_names = [
        location_names_list[i * batch_size:(i + 1) * batch_size] for i in
        range((len(location_names_list) + batch_size - 1) // batch_size)]

    # Iterate over each list of locations, calling the API for each that batch
    # stitching the responses into a single list to process after the API calls
    stitched_responses = {'locationDrivingDirectionMetrics': []}
    for key, batch in enumerate(batched_location_names):
        logger.debug("Begin processing on locations batch %s of %s",
                     str(key + 1), len(batched_location_names))
        for days in account['aggregate_days']:
            logger.debug("Begin processing on %s day aggregate", days)
            bodyvar = {
                'locationNames': batch,
                # https://developers.google.com/my-business/reference/rest/v4/accounts.locations/reportInsights#DrivingDirectionMetricsRequest
                'drivingDirectionsRequest': {
                    'numDays': f'{days}',
                    'languageCode': 'en-US'
                    }
                }

            logger.debug("Request JSON -- \n%s", json.dumps(bodyvar, indent=2))

            # Posts the API request
            try:
                response = \
                    service.accounts().locations().\
                    reportInsights(body=bodyvar, name=name).execute()
            except googleapiclient.errors.HttpError:
                logger.exception(
                    "Request contains an invalid argument. Skipping.")
                continue

            # stitch all responses responses for later iterative processing
            stitched_responses['locationDrivingDirectionMetrics'] += \
                response['locationDrivingDirectionMetrics']

    # The stiched_responses now contains all location driving direction data
    # as a list of dictionaries keyed to 'locationDrivingDirectionMetrics'.
    # The next block will build a dataframe from this list for CSV ouput to S3

    # Write out a file containing the stiched response from the queries above
    # file = open("LocationDrivingDirectionMetrics.json", "w+")
    # json.dump(stitched_responses, file, indent=2)

    # location_region_rows will collect elements from the API response
    # JSON into a list of dicts, to normalize into a DataFrame later
    location_region_rows = []
    location_directions = stitched_responses['locationDrivingDirectionMetrics']
    for location in location_directions:
        # The case where no driving directions were queried over this time
        # these records will be omitted, since there is nothing to report
        if 'topDirectionSources' not in location:
            continue

        # iterate over the top 10 driving direction requests for this location
        # the order of these is desending by number of requests
        source = location['topDirectionSources'][0]
        regions = source['regionCounts']
        for order, region in enumerate(regions):
            row = {
                'utc_query_date': query_date,
                'client_shortname': account['clientShortname'],
                'location_label':
                    label_lookup[location['locationName']]['locationName'],
                'location_locality':
                    label_lookup[location['locationName']]['locality'],
                'location_postal_code':
                    label_lookup[location['locationName']]['postalCode'],
                'location_name': location['locationName'],
                'days_aggregated': source['dayCount'],
                'rank_on_query': order + 1,  # rank is from 1 to 10
                'region_count': region['count'],
                'region_latitude': region['latlng']['latitude'],
                'region_longitude': region['latlng']['longitude'],
                'region_label': region['label'],
                'location_time_zone': location['timeZone']
                }
            location_region_rows.append(row)

    # normalizing the list of dicts to a dataframe
    df = json_normalize(location_region_rows)

    # build three columns: region_count_seven_days, region_count_thirty_days
    # and region_count_ninety_days to replace region_count column.
    new_cols = {
        'region_count_seven_days': 7,
        'region_count_thirty_days': 30,
        'region_count_ninety_days': 90
        }
    for key, value in new_cols.items():
        def alert(c):
            if c['days_aggregated'] == value:
                return c['region_count']
            else:
                return 0

        df[key] = df.apply(alert, axis=1)

    df.drop(columns='region_count', inplace=True)

    # output csv formatted dataframe to stream
    csv_stream = StringIO()
    # set order of columns for S3 file in order to facilitate table COPY
    column_names = [
        "client_shortname", "days_aggregated", "location_label",
        "location_locality", "location_name", "location_postal_code",
        "location_time_zone", "rank_on_query", "region_label",
        "region_latitude", "region_longitude", "utc_query_date",
        "region_count_seven_days", "region_count_ninety_days",
        "region_count_thirty_days"]
    df = df.reindex(columns=column_names)
    df.to_csv(csv_stream, sep='|', encoding='utf-8', index=False)

    # write csv to S3
    resource.Bucket(config_bucket).put_object(
        Key=object_key,
        Body=csv_stream.getvalue())
    logger.debug('S3 PUT_OBJECT: %s:%s', outfile, config_bucket)
    object_summary = resource.ObjectSummary(config_bucket, object_key)
    logger.debug('S3 OBJECT LOADED ON: %s OBJECT SIZE: %s',
                 object_summary.last_modified, object_summary.size)

    logquery = (
        f"COPY {config_dbtable} ("
        "client_shortname,"
        "days_aggregated,"
        "location_label,"
        "location_locality,"
        "location_name,"
        "location_postal_code,"
        "location_time_zone,"
        "rank_on_query,"
        "region_label,"
        "region_latitude,"
        "region_longitude,"
        "utc_query_date,"
        "region_count_seven_days,"
        "region_count_ninety_days,"
        "region_count_thirty_days"
        f") FROM 's3://{config_bucket}/{object_key}' CREDENTIALS '"
        "aws_access_key_id={AWS_ACCESS_KEY_ID};"
        "aws_secret_access_key={AWS_SECRET_ACCESS_KEY}' "
        "IGNOREHEADER AS 1 MAXERROR AS 0 DELIMITER '|' NULL AS '-' ESCAPE;")
    query = logquery.format(
            AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID,
            AWS_SECRET_ACCESS_KEY=AWS_SECRET_ACCESS_KEY)
    logger.debug(logquery)

    # Connect to Redshift and execute the query.
    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as curs:
            try:
                curs.execute(query)
            except psycopg2.Error:
                logger.exception(
                    ("Loading driving directions for failed %s "
                     "on Object key: %s"),
                    account['clientShortname'],object_key.split('/')[-1])
                outfile = badfile
            else:
                logger.info(
                    ("Loaded %s driving directions successfully. "
                     "Object key %s."),
                    account['clientShortname'], object_key.split('/')[-1])
                outfile = goodfile

    # copy the processed file to the outfile destination path
    try:
        client.copy_object(
            Bucket="sp-ca-bc-gov-131565110619-12-microservices",
            CopySource="sp-ca-bc-gov-131565110619-12-microservices/"
            + object_summary.key, Key=outfile)
    except boto3.exceptions.ClientError:
        logger.exception("S3 copy %s to %s location failed.",
                         object_summary.key, outfile=outfile)
