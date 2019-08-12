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
import logging
import psycopg2
import argparse
import httplib2
import pandas as pd
from pandas.io.json import json_normalize

import googleapiclient.errors

from io import BytesIO
import datetime
from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets


# Ctrl+C
def signal_handler(signal, frame):
    logger.debug('Ctrl+C pressed!')
    sys.exit(0)


# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler for logs at the INFO level
# This will be emailed when the cron task runs; formatted to give messages only
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# create file handler for logs at the INFO level
log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
handler = logging.FileHandler(os.path.join('logs', log_filename), 'a',
                              encoding=None, delay='true')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


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
config_locationGroups = config['locationGroups']

# set up the Redshift connection
conn_string = (
    "dbname='snowplow' "
    "host='snowplow-ca-bc-gov-main-redshi-resredshiftcluster-"
    "13nmjtt8tcok7.c8s7belbz4fo.ca-central-1.redshift.amazonaws.com"
    "' port='5439' user='{user}' password={password}"
    ).format(user=os.environ['pguser'], password=os.environ['pgpass'])

# the copy command will be formatted when the query is ready to be excecuted
copy_command = (
    "copy {table} FROM 's3://{bucket}/{object}' "
    "CREDENTIALS 'aws_access_key_id={key};aws_secret_access_key={secret}' "
    "IGNOREHEADER AS 1 MAXERROR AS 0 DELIMITER '|' NULL AS '-' ESCAPE;")

aws_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret = os.environ['AWS_SECRET_ACCESS_KEY']

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
    accountNumber = os.environ['{0}_accountid'.format(loc['clientShortname'])]
    try:
        validated_accounts.append(
            next({
                'name': item['name'],
                'clientShortname': loc['clientShortname'],
                'accountNumber': accountNumber}
                 for item
                 in accounts
                 if item['accountNumber'] == accountNumber))
    except StopIteration:
        logger.warning(
            'No access to {0}: {1}. Skipping.'
            .format(loc['clientShortname'], accountNumber))
        continue

# iterate over ever validated account
for account in validated_accounts:
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

    batched_location_names = [
        location_names_list[i * batch_size:(i + 1) * batch_size] for i in
        range((len(location_names_list) + batch_size - 1) // batch_size)]

    # Iterate over each list of locations, calling the API for each that batch
    # stitching the responses into a single list to process after the API calls
    stitched_responses = {'locationDrivingDirectionMetrics': []}
    for key, batch in enumerate(batched_location_names):
        logger.debug("Begin processing on locations batch {0} of {1}".format(
            key + 1, len(batched_location_names)))
        bodyvar = {
            'locationNames': batch,
            # https://developers.google.com/my-business/reference/rest/v4/accounts.locations/reportInsights#DrivingDirectionMetricsRequest
            'drivingDirectionsRequest': {
                'numDays': 'SEVEN',
                'languageCode': 'en-US'
                }
            }

        logger.debug(
            "Request JSON -- \n{0}".format(json.dumps(bodyvar, indent=2)))

        # Posts the API request
        try:
            response = \
                service.accounts().locations().\
                reportInsights(body=bodyvar, name=name).execute()
        except googleapiclient.errors.HttpError as e:
            logger.info("Request contains an invalid argument. Skipping.")
            continue

        stitched_responses['locationDrivingDirectionMetrics'] += \
            response['locationDrivingDirectionMetrics']

    # The stiched_responses now contains all location driving direction data
    # as a list of dictionaries keyed to 'locationDrivingDirectionMetrics'.
    # The next block will build a dataframe from this list for CSV ouput to S3
    file = open("LocationDrivingDirectionMetrics.json", "w+")
    json.dump(stitched_responses, file, indent=2)

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

    # output csv formatted dataframe to stream
    csv_stream = BytesIO()
    df.to_csv(csv_stream, sep='|', encoding='utf-8', index=False)

    # Set up the S3 path to write the csv buffer to
    object_key_path = 'client/google_mybusiness_{}/'.format(
        account['clientShortname'])

    outfile = 'gmb_directions_{0}_{1}.csv'.format(
        account['clientShortname'],
        query_date)
    object_key = object_key_path + outfile

    # set up the S3 resource
    client = boto3.client('s3')
    resource = boto3.resource('s3')

    # write csv to S3
    resource.Bucket(config_bucket).put_object(
        Key=object_key,
        Body=csv_stream.getvalue())
    logger.debug('PUT_OBJECT: {0}:{1}'.format(outfile, config_bucket))
    object_summary = resource.ObjectSummary(config_bucket, object_key)
    logger.debug('OBJECT LOADED ON: {0} \nOBJECT SIZE: {1}'
                 .format(object_summary.last_modified,
                         object_summary.size))

    # Prepare the Redshift COPY command.
    query = copy_command.format(
            table=config_dbtable,
            bucket=config_bucket,
            object=object_key,
            key=aws_key,
            secret=aws_secret)
    logquery = copy_command.format(
            table=config_dbtable,
            bucket=config_bucket,
            object=object_key,
            key='AWS_ACCESS_KEY_ID',
            secret='AWS_SECRET_ACCESS_KEY')
    logger.debug(logquery)

    # Connect to Redshift and execute the query.
    with psycopg2.connect(conn_string) as conn:
        with conn.cursor() as curs:
            try:
                curs.execute(query)
            except psycopg2.Error:
                logger.exception("".join((
                    "Loading driving directions for failed {0} with exception:"
                    .format(account['clientShortname']),
                    " Object key: {0}".format(object_key.split('/')[-1]))))
            else:
                logger.info("".join((
                    "Loaded {0} driving directions successfully."
                    .format(account['clientShortname']),
                    ' Object key: {0}'.format(object_key.split('/')[-1]))))
