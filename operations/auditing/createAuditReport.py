###################################################################
# Script Name   : createAuditReport.py
#
# Description   : script to generate audit report given a website domain
#

import os
import sys
import psycopg2
import httplib2
import json
import argparse
import getpass
import pandas as pd
from sqlalchemy import create_engine

# parse cmd arguments
parser = argparse.ArgumentParser(
    description='Generate auditing report for a given site host.')
parser.add_argument('siteHost', help='site host such as my-site.gov.bc.ca')
parser.add_argument('lookerClientId', help='your looker client id')
parser.add_argument('-s',
                    '--lookerClientSecret',
                    help='your looker client secret')
parser.add_argument('-H',
                    '--pgHost',
                    help='Redshift host overriding env var PGHOST')
parser.add_argument('-u',
                    '--pgUser',
                    help='Redshift user name overriding env var PGUSER')
parser.add_argument('-p',
                    '--pgPassword',
                    help='Redshift user password overriding env var'
                    ' PGPASSWORD')
parser.add_argument('-l',
                    '--lookerUrlPrefix',
                    help='Looker url prefix such as https://looker.local:19999'
                    '/api/3.1 overriding env var lookerUrlPrefix')
parser.add_argument('-f',
                    '--file',
                    help='Write results to a csv file at the specified path')

args = parser.parse_args()

# set var from cmd args or envvars
lookerClientId = args.lookerClientId
pgHost = args.pgHost or os.getenv('PGHOST')
pgUser = args.pgUser or os.getenv('PGUSER')
pgPassword = args.pgPassword or os.getenv('PGPASSWORD')
lookerUrlPrefix = args.lookerUrlPrefix or os.getenv('lookerUrlPrefix')
lookerClientSecret = args.lookerClientSecret
file = args.file

# prompt user to supply missing mandatory information
if pgHost is None:
    pgHost = input('Enter Redshift host name: ')
if pgUser is None:
    pgUser = input('Enter Redshift user name: ')
if pgPassword is None:
    pgPassword = getpass.getpass('Enter Redshift user password: ')
if lookerUrlPrefix is None:
    lookerUrlPrefix = input('Enter Looker Url prefix: ')
if lookerClientSecret is None:
    lookerClientSecret = getpass.getpass('Enter your looker client secret: ')

# database connection string
connection_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    pgUser,
    pgPassword,
    pgHost,
    '5439',
    'snowplow'
)
engine = create_engine(connection_string)

# create empty dict for api user data
lookerUserIdNameMap = {}

qryString = """
select
    convert_timezone('America/Vancouver', starttime),
    looker_user_id,
    trim(querytxt) as sqlquery
from
    admin.V_STL_QUERY_HISTORY
where
    sqlquery ilike '-- Looker Query Context%%page_urlhost%%'
    -- exclude known admin users
    and looker_user_id not in ('13','128','8','513','35','746','742','6','16')
    and (
        sqlquery ilike '%%page_urlhost)) = ''{0}''%%'
        or
        sqlquery ilike '%%page_urlhost = ''{0}''%%'
        or
        position('page_urlhost LIKE ''%%''' in sqlquery) > 0
        )
order by
    starttime desc;
    """.format(args.siteHost)  # nosec

# execute the query and store in a dataframe
dfQuery = pd.read_sql(qryString, engine)

# grab the unique user ids from the query
queryUserIdList = dfQuery['looker_user_id'].unique()
for id in queryUserIdList:
    lookerUserIdNameMap[id] = {}

# api login to looker
h = httplib2.Http(
    ca_certs=os.path.dirname(os.path.realpath(__file__)) + '/ca.crt')
resp, content = h.request(
    lookerUrlPrefix + '/login',
    "POST",
    body='client_id=' + lookerClientId + '&client_secret=' +
    lookerClientSecret,
    headers={'content-type': 'application/'
        'x-www-form-urlencoded'})
jsonRes = json.loads(content)
accessToken = jsonRes['access_token']
userSrchStr = lookerUrlPrefix+'/users/search?id=' + \
    ','.join(lookerUserIdNameMap.keys())

# api call for looker users
resp, content = h.request(
    userSrchStr,
    "GET",
    headers={'authorization': 'token ' + accessToken})
users = json.loads(content)

# add looker user data to dict if user id in query
for usr in users:
    lookerUserIdNameMap[str(
        usr['id'])]["displayName"] = usr['display_name']
    if usr['credentials_embed'] is not None and len(
            usr['credentials_embed']) > 0:
        lookerUserIdNameMap[str(
            usr['id'])]["embedUserId"] = \
            usr['credentials_embed'][0]['external_user_id']
        
# convert name map dict to dataframe
dfLookerUserIdNameMap = pd.DataFrame.from_dict(lookerUserIdNameMap, orient='index')
dfLookerUserIdNameMap = dfLookerUserIdNameMap.reset_index()
dfLookerUserIdNameMap = dfLookerUserIdNameMap.rename(columns={"index": "looker_user_id"})

# merge query results with name map
dfMerged = pd.merge(dfQuery, dfLookerUserIdNameMap, on='looker_user_id')

# cleaning up the results
dfMerged['displayName'] = dfMerged['displayName'].apply(lambda x: str(x).replace('"', '""'))
dfMerged['embedUserId'] = dfMerged['embedUserId'].apply(lambda x: str(x).replace('"', '""'))
dfMerged['sqlquery'] = dfMerged['sqlquery'].apply(lambda x: str(x).strip())
dfMerged = dfMerged.rename(columns={"convert_timezone": "Date & Time",
                                    "looker_user_id": "Looker User Id",
                                    "displayName": "User Display Name",
                                    "embedUserId": "User Embed Id",
                                    "sqlquery": "Query Text"})

# setting column datatypes
dfMerged['Date & Time'] = dfMerged['Date & Time'].astype('datetime64[ns]')
dfMerged['Looker User Id'] = dfMerged['Looker User Id'].astype('int')
dfMerged['User Display Name'] = dfMerged['User Display Name'].astype('str')
dfMerged['User Embed Id'] = dfMerged['User Embed Id'].astype('str')
dfMerged['Query Text'] = dfMerged['Query Text'].astype('str')

# reorder columns
dfMerged = dfMerged.iloc[:,[0,1,3,4,2]]

# print results to console# if output is not set print results to console
if file is None:
    print(dfMerged.to_csv(index=False, quoting=2))
else:
    dfMerged.to_csv(path_or_buf=file, index=False, quoting=2)