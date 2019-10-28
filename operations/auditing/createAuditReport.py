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

# parse cmd arguments
parser = argparse.ArgumentParser(
    description='Generate auditing report for a given site host.')
parser.add_argument('siteHost', help='site host such as my-site.gov.bc.ca')
parser.add_argument('lookerClientId', help='your looker client id')
parser.add_argument('-s', '--lookerClientSecret',
                    help='your looker client secret')
parser.add_argument(
    '-H', '--pgHost', help='Redshift host overriding env var PGHOST')
parser.add_argument(
    '-u', '--pgUser', help='Redshift user name overriding env var PGUSER')
parser.add_argument('-p', '--pgPassword',
                    help='Redshift user password overriding env var PGPASSWORD')
parser.add_argument('-l', '--lookerUrlPrefix',
                    help='Looker url prefix such as https://looker.local:19999/api/3.1 overriding env var lookerUrlPrefix')

args = parser.parse_args()

lookerClientId = args.lookerClientId
pgHost = args.pgHost or os.getenv('PGHOST')
pgUser = args.pgUser or os.getenv('PGUSER')
pgPassword = args.pgPassword or os.getenv('PGPASSWORD')
lookerUrlPrefix = args.lookerUrlPrefix or os.getenv('lookerUrlPrefix')
lookerClientSecret = args.lookerClientSecret

# prompt user to supply missing mandatory information
if pgHost is None:
  sys.stderr.write('Enter Redshift host name: ')
  pgHost = sys.stdin.readline().strip()
if pgUser is None:
  sys.stderr.write('Enter Redshift user name: ')
  pgUser = sys.stdin.readline().strip()
if pgPassword is None:
  sys.stderr.write('Enter Redshift user password: ')
  pgPassword = sys.stdin.readline().strip()
if lookerUrlPrefix is None:
  sys.stderr.write('Enter Looker Url prefix: ')
  lookerUrlPrefix = sys.stdin.readline().strip()
if lookerClientSecret is None:
  lookerClientSecret = getpass.getpass('Enter your looker client secret: ')

# database connection string
conn_string = "dbname='snowplow' host='" + pgHost + \
    "' port='5439' user='" + pgUser + "' password=" + pgPassword

# query database
lookerUserIdNameMap = {}
with psycopg2.connect(conn_string) as conn:
  with conn.cursor() as curs:
    qryString = """
select
    convert_timezone('America/Vancouver', starttime),
    looker_user_id,
    trim(querytxt) as sqlquery       
from
    admin.V_STL_QUERY_HISTORY       
where
    sqlquery ilike '-- Looker Query Context%page_urlhost%'               
    -- exclude known admin users
    and looker_user_id not in ('13','128','8','513','35','746','742','6','16') 
    and (
        sqlquery ilike '%page_urlhost)) = ''{0}''%'               
        or 
        sqlquery ilike '%page_urlhost = ''{0}''%'
        or 
        position('page_urlhost LIKE ''%''' in sqlquery) > 0
        )
order by
    starttime desc;
    """.format(args.siteHost)
    curs.execute(qryString)
    for rec in curs:
      lookerUserIdNameMap[rec[1]] = {}
    # query looker users
    h = httplib2.Http(ca_certs='./ca.crt')
    resp, content = h.request(lookerUrlPrefix+'/login', "POST", body='client_id=' +
                              lookerClientId + '&client_secret=' + lookerClientSecret,
                              headers={'content-type': 'application/x-www-form-urlencoded'})
    jsonRes = json.loads(content)
    accessToken = jsonRes['access_token']
    userSrchStr = lookerUrlPrefix+'/users/search?id=' + \
        ','.join(lookerUserIdNameMap.keys())
    resp, content = h.request(userSrchStr, "GET",
                              headers={'authorization': 'token ' + accessToken})
    users = json.loads(content)
    for usr in users:
      lookerUserIdNameMap[str(usr['id'])]["displayName"] = usr['display_name']
      if usr['credentials_embed'] is not None and len(usr['credentials_embed']) > 0:
        lookerUserIdNameMap[str(
            usr['id'])]["embedUserId"] = usr['credentials_embed'][0]['external_user_id']
    print('"Date & Time","Looker User Id","User Display Name","User Embed Id","Query Text"')
    curs.scroll(0, mode='absolute')
    for rec in curs:
      displayNm = lookerUserIdNameMap[rec[1]].get(
          "displayName", '').replace('"', '""')
      userEmbedId = lookerUserIdNameMap[rec[1]].get(
          "embedUserId", '').replace('"', '""')
      queryTxt = rec[2]
      if queryTxt is not None:
        queryTxt = queryTxt.replace('"', '""')
      print('{0},{1},"{2}","{3}","{4}"'.format(
          rec[0], rec[1], displayNm, userEmbedId, queryTxt))
