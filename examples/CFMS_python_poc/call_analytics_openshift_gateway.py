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
#               : For example:
#               : $ python call_analytics.py caps.pathfinder.bcgov
#               : $ python call_analytics.py localhost 8080
#
# References    : https://github.com/bcgov/GDX-Analytics-OpenShift-Snowplow-Gateway-Service

import http.client
import time
import json
import sys
import ssl
from socket import gaierror

# GDX Analytics as a Service address information
# Prod: caps.pathfinder.gov.bc.ca
# Test: test-caps.pathfinder.gov.bc.ca
# Dev:  dev-caps.pathfinder.gov.bc.ca
hostname = sys.argv[1]
bcgov_hosts = ['caps.pathfinder.bcgov',
               'test-caps.pathfinder.bcgov',
               'dev-caps.pathfinder.bcgov']
hostport = False

# hostport is only used if the listener app is running on 0.0.0.0.
# do not specify a hostport if you a connecting to one of the bcgov_hosts
if hostname not in bcgov_hosts:
    if len(sys.argv) == 3:
        hostport = sys.argv[2]


# make the POST call that contains the event data
def post_event(json_event):
    # Make the connection
    conn = http.client.HTTPSConnection(
        hostname, context=ssl._create_unverified_context())
    if hostport:
        conn.port = hostport

    # Prepare the headers
    headers = {'Content-type': 'application/json'}

    # Send a post request containing the event as JSON in the body
    try:
        conn.request('POST', '/post', json_event, headers)
    except gaierror as e:
        print("Failure getting address info. \nYour IP address may not be whitelisted to the listener.")
        sys.exit(1)


    # Recieve the response
    try:
        response = conn.getresponse()
    except http.client.ResponseNotReady as e:
        print("ResponseNotReady Exception")
        sys.exit(1)
    # Print the response
    print(response.status, response.reason)

# schema is a string to the iglu:ca.bc.gov schema for this event
# context is the list of contexts as dictionaries for this event
# data is a dictionary describing this events data
def event(schema, contexts, data):
    post_body = configuration
    post_body['dvce_created_tstamp'] = event_timestamp()
    post_body['event_data_json'] = {
        'contexts':contexts,
        'data':data,
        'schema':schema
    }
    return post_body

# time of event as an epoch timestamp in milliseconds
def event_timestamp():
    # time.time() returns the time in seconds with 6 decimal places of precision
    return int(round(time.time() * 1000))

def get_citizen(client_id,service_count,quick_txn,schema):
    # Set up the citizen context.
    citizen = {
        'data':
        {
            'client_id': client_id,
            'service_count': service_count,
            'quick_txn': quick_txn
        },
        'schema':schema
    }
    return citizen

def get_office(office_id,office_type,schema):
    # Set up the office context.
    office = {
        'data':
        {
            'office_id': office_id,
            'office_type': office_type
        },
        'schema':schema
    }
    return office

def get_agent(agent_id,role,quick_txn,schema):
    # Set up the service context.
    agent = {
        'data':
        {
            'agent_id': agent_id,
            'role': role,
            'quick_txn': quick_txn
        },
        'schema':schema
    }
    return agent

# Prepare the event requirements
configuration = {
    'env':'test', # test or prod
    'namespace':'GDX-OpenShift-Test',
    'app_id':'GDX-OpenShift-Test'
}

# Example values contexts
## citizen
citizen_schema='iglu:ca.bc.gov.cfmspoc/citizen/jsonschema/3-0-0'
client_id=283732
service_count=15
quick_txn=False
## office
office_schema='iglu:ca.bc.gov.cfmspoc/office/jsonschema/1-0-0'
office_id=14
office_type='reception'
## agent
agent_schema='iglu:ca.bc.gov.cfmspoc/agent/jsonschema/2-0-0'
agent_id=99
role='CSR'
quick_txn=False

citizen = get_citizen(
    client_id=client_id,
    service_count=service_count,
    quick_txn=quick_txn,
    schema=citizen_schema
)

office = get_office(
    office_id=office_id,
    office_type=office_type,
    schema=office_schema
)

agent = get_agent(
    agent_id=agent_id,
    role=role,
    quick_txn=quick_txn,
    schema=agent_schema
)

contexts = [citizen,office,agent]

# Example schema and data for a 'finish' event
schema = 'iglu:ca.bc.gov.cfmspoc/finish/jsonschema/2-0-0'
data = {
    'inaccurate_time': False,
    'quantity': 66
}

# create example event
example_event = event(schema,contexts,data)

# Create a JSON object from the event dictionary
json_event = json.dumps(example_event)

# POST the event to the Analytics service
post_event(json_event)
