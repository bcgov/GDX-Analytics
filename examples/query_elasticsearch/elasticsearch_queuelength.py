###################################################################
# Script Name       : elasticsearch_queuelength.py
#
# Description       : Queries elasticsearch and calculates the current
#                     number of citizens in line for a given Service BC
#                     fierld office
#
#                     Configuration file should contain line separated list of
#                     Service BC offices to query from Elasticsearch, index and
#                     endpoint specified.
#
#                     In order to query by office location (eg: Kelowna,
#                     Kamloops), it is necessary to include a JSON export
#                     of office names and id's. This json export can be
#                     created in the looker explore, here:
#                     https://analytics.gov.bc.ca/
#                       explore/cfms_poc/cfms_poc?toggle=fil&qid=DWe1cjJI5lYB084l8fjZ1M
#
#                     Name the json export into a file called serviceBCOfficeList.json
#                     and place it in the same directory as this script.
#
# Requirements      : Install the following python packages to allow
#                     querying the elasticsearch endpoint, credentials, and
#                     index for regular use:
#
#                   : elasticsearch-dsl>=6.0.0,<7.0.0
#                   : elasticsearch>=6.0.0,<7.0.0
#
# Recommendations   : It's recommended to set environment variables for
#                     the elastic search endpoint.
#
#                   : export ES_USER='<<ElasticSearch_Username>>'
#                   : export ES_PASS='<<ElasticSearch_Password>>'
#                   : export ES_ENDPOINT='<<ElasticSearch_Endpoint>>'
#                   : export ES_INDEX='<<ElasticSearch_Index>>'
#
# Usage             : To query a list of Service BC offices, run:
#
#                   : python3 elasticsearch_queuelength.py --config
#                   :   officelist.txt
#                   :   --username ES_USER --password ES_PASS
#                   :   --endpoint ES_ENDPOINT --index ES_INDEX
#
#                   : where 'officelist.txt' is a text file containing the
#                   : newline separated list of Service BC field offices you
#                   : wish to query.


from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import logging
from argparse import ArgumentParser
import json
import sys
import os
import signal

# Arguments parsing
parser = ArgumentParser(
  description='Counts queue length  for given Service BC field offices\
               using Elastisearch and Snowplow.')
parser.add_argument('-c', '--config', help='Config file listing the Service \
                    BC field offies of interest.', required=True)
parser.add_argument('-u', '--username', help='Username.', required=True)
parser.add_argument('-p', '--password', help='Password.', required=True)
parser.add_argument('-d', '--debug', help='Debug', action="store_true")
parser.add_argument('-i', '--index', help='Index', required=True)
parser.add_argument('-ep', '--endpoint', help='Endpoint', required=True)
args = parser.parse_args()


# Ctrl+C
def signal_handler(signal, frame):
    logger.debug('Ctrl+C pressed!')
    sys.exit(0)


# Ctrl+C handler
signal.signal(signal.SIGINT, signal_handler)

# Create stream handler for logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s:[%(levelname)s]: %(message)s")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Validate config file
config = args.config
if os.path.isfile(config):
    with open(config) as f:
        offices = tuple(line.rstrip() for line in f)
else:
    logger.error("a config file listing Sewrvice BC field offices by line is required. \
                 Use --config <file_path>")

# Assign credentials and collector information
http_user = args.username
http_pass = args.password
endpoint = args.endpoint
index = args.index

client = Elasticsearch(endpoint, http_auth=(http_user, http_pass))
logger.debug('Elastic search object: ', client)

with open('serviceBCOfficeList.json') as json_file:
    serviceCenters = json.load(json_file)

for office in offices:
    office_id = ''
    for serviceCenter in serviceCenters:
        if serviceCenter["cfms_poc.office_name"] == office:
            office_id = serviceCenter['cfms_poc.office_id']

    # Query for number of addcitizen events. Note: The derived timestamp looks
    # weird but 'now/d+7h' is rounding down to the start of the day in UTC
    # which is 1700 which is 17h00 local on the previous day, so I am adding
    # 5 hours to get midnight.
    params = Q('term', app_id='TheQ') & \
        Q('term', event_name='addcitizen') & \
        Q('term', **{'contexts_ca_bc_gov_cfmspoc_office_1.office_id':
                     office_id}) & \
        Q('range', derived_tstamp={'gte': 'now/d+7h'}) & \
        Q('range', derived_tstamp={'lt': 'now'})
    try:
        s = Search(using=client, index=index).filter(params)
    except Exception as e:
        logger.debug(e)
    addCitizenCount = s.count()

    # Query for number of customerleft events
    params = Q('term', app_id='TheQ') & \
        Q('term', event_name='customerleft') & \
        Q('term', **{'contexts_ca_bc_gov_cfmspoc_office_1.office_id':
                     office_id}) & \
        Q('range', derived_tstamp={'gte': 'now/d+7h'}) & \
        Q('range', derived_tstamp={'lt': 'now'})
    try:
        s = Search(using=client, index=index).filter(params)
    except Exception as e:
        logger.debug(e)
    customerLeft = s.count()

    # Query for number of finish events
    params = Q('term', app_id='TheQ') & \
        Q('term', event_name='finish') & \
        Q('term', **{'contexts_ca_bc_gov_cfmspoc_office_1.office_id':
                     office_id}) & \
        Q('range', derived_tstamp={'gte': 'now/d+7h'}) & \
        Q('range', derived_tstamp={'lt': 'now'})
    try:
        s = Search(using=client, index=index).filter(params)
    except Exception as e:
        logger.debug(e)
    finish = s.count()

    # Calculate the total number of citizens in the queue for
    # the current office
    queueSize = addCitizenCount - (customerLeft + finish)

    logger.info(office + ' queue size successfully queried')
    print ('Office: ', office, ' Total queue size: ', queueSize)
