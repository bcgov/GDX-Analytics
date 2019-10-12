###################################################################
# Script Name   : call_analytics.py
#
# Description   : Sample Python script showing the structure of an
#               : example event, and the requirements to call the
#               : GDX Analytics OpenShift Snoplow Gateway service
#               : with that event data.
#
# Requirements  : You must pass the hostname as the first argument.
#               : A second argument for the port is required if calling
#               : a listener that is not on the BCGov OpenShift cluster.
#
# Usage         : configure the Example values to your preference,
#               : then call the script from the command line:
#               : $ python call_analytics.py <<hostname>> <<hostport>>
#               :
# Examples      : This usage will call the default localhost on port 8443:
#               : $ python call_analytics_openshift_gateway.py
#               : This usage will call caps.pathfinder.bcgov on 8443 with debug
#               : level logging:
#         $ python call_analytics_openshift_gateway.py caps.pathfinder.bcgov -d
#               : This usage will call localhost on port 443 using https
#            $ python call_analytics_openshift_gateway.py localhost 443 -s
#
# References    :
#     https://github.com/bcgov/GDX-Analytics-OpenShift-Snowplow-Gateway-Service

import http.client
import time
import json
import sys
import ssl
from socket import gaierror
import argparse
import signal  # Dealing with Ctrl+C
import logging

# Arguments parsing
parser = argparse.ArgumentParser(
    description='Unix like tail command for Elastisearch and Snowplow.')
parser.add_argument('hostname', nargs='?', help='CAPS Analytics host URL.',
                    default='localhost')
parser.add_argument('hostport', nargs='?', help='CAPS Analytics host port.',
                    default='8443')
parser.add_argument('-d', '--debug', help='Debug level logging.',
                    action="store_true")
parser.add_argument('-i', '--insecure', help='Transmit insecurely over HTTP',
                    action="store_true")
args = parser.parse_args()

# Create stream handler for logs at the INFO level
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s:[%(levelname)s]: %(message)s")
if args.debug:
    # Extend stream handler for logs at the DEBUG level
    logger.setLevel(logging.DEBUG)
    logger.debug("debug mode is on")
else:
    logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


# Ctrl+C
def signal_handler(signal, frame):
    logger.info('Ctrl+C pressed. Exiting.')
    sys.exit(0)


# Ctrl+C handler
signal.signal(signal.SIGINT, signal_handler)

# GDX Analytics as a Service address information
hostname = args.hostname
hostport = args.hostport


# make the POST call that contains the event data
def post_event(json_event):
    # Make the connection
    if args.insecure:
        conn = http.client.HTTPConnection(hostname)
    else:
        conn = http.client.HTTPSConnection(
            hostname, context=ssl._create_unverified_context())
    if hostport:
        conn.port = hostport

    # Prepare the headers
    headers = {'Content-type': 'application/json'}

    # Send a post request containing the event as JSON in the body
    try:
        conn.request('POST', '/post', json_event, headers)
    except gaierror:
        logger.exception(
            ("Failure getting address info. "
             "Your IP address may not be whitelisted to the listener."))
        sys.exit(1)

    # Recieve the response
    try:
        response = conn.getresponse()
    except http.client.ResponseNotReady:
        logger.exception("ResponseNotReady Exception")
        sys.exit(1)
    # Print the response
    logger.info('status: {} reason: {}'.format(
        response.status, response.reason))


# schema is a string to the iglu:ca.bc.gov schema for this event
# context is the list of contexts as dictionaries for this event
# data is a dictionary describing this events data
def event(schema, contexts, data):
    post_body = configuration
    post_body['dvce_created_tstamp'] = event_timestamp()
    post_body['event_data_json'] = {
        'contexts': contexts,
        'data': data,
        'schema': schema}
    return post_body


# time of event as an epoch timestamp in milliseconds
def event_timestamp():
    # time.time() returns the time in seconds with 6 decimal places
    return int(round(time.time() * 1000))


def get_citizen(client_id, service_count, quick_txn, schema):
    # Set up the citizen context.
    citizen = {
        'data': {
            'client_id': client_id,
            'service_count': service_count,
            'quick_txn': quick_txn},
        'schema': schema}
    return citizen


def get_office(office_id, office_type, schema):
    # Set up the office context.
    office = {
        'data': {
            'office_id': office_id,
            'office_type': office_type},
        'schema': schema}
    return office


def get_agent(agent_id, role, quick_txn, schema):
    # Set up the service context.
    agent = {
        'data': {
            'agent_id': agent_id,
            'role': role,
            'quick_txn': quick_txn},
        'schema': schema}
    return agent


# Prepare the event requirements
configuration = {
    'env': 'test',  # test or prod
    'namespace': 'GDX-OpenShift-Test',
    'app_id': 'GDX-OpenShift-Test'}

# Example values contexts
# citizen
citizen_schema = 'iglu:ca.bc.gov.cfmspoc/citizen/jsonschema/3-0-0'
client_id = 283732
service_count = 15
quick_txn = False
# office
office_schema = 'iglu:ca.bc.gov.cfmspoc/office/jsonschema/1-0-0'
office_id = 14
office_type = 'reception'
# agent
agent_schema = 'iglu:ca.bc.gov.cfmspoc/agent/jsonschema/2-0-0'
agent_id = 99
role = 'CSR'
quick_txn = False

citizen = get_citizen(
    client_id=client_id,
    service_count=service_count,
    quick_txn=quick_txn,
    schema=citizen_schema)

office = get_office(
    office_id=office_id,
    office_type=office_type,
    schema=office_schema)

agent = get_agent(
    agent_id=agent_id,
    role=role,
    quick_txn=quick_txn,
    schema=agent_schema)

contexts = [citizen, office, agent]

# Example schema and data for a 'finish' event
schema = 'iglu:ca.bc.gov.cfmspoc/finish/jsonschema/2-0-0'
data = {
    'inaccurate_time': False,
    'quantity': 66}

# create example event
example_event = event(schema, contexts, data)

# Create a JSON object from the event dictionary
json_event = json.dumps(example_event)

# POST the event to the Analytics service
post_event(json_event)
