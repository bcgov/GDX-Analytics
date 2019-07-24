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
# Usage             : To query a list of Service BC, run:
#
#                   : python3 elasticsearch_queuelength.py --config
#                   :   domainlist.txt
#                   :   --username ES_USER --password ES_PASS
#                   :   --endpoint ES_ENDPOINT --index ES_INDEX
#
#                   : where 'domainlist.txt' is a text file containing the
#                   : newline separated list of Service BC field offices you
#                   : wish to query. You can optionally specify a start time
#                   : and an end time using flags:
#
#                   : python3 elasticsearch_pageviews.py -c domainlist.txt
#                   :   -u ES_USER -p ES_PASS -s 'now-60m' -e 'now'

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import logging
from argparse import ArgumentParser
import sys
import os
import signal

# Arguments parsing
parser = ArgumentParser(
  description='Counts page views for given domains using Elastisearch \
               and Snowplow.')
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
