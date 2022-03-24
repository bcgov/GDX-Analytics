###################################################################
# Script Name   : invoke_looker_embed_generator_api.py
#
# Description   : Sample Python script to generate secure Looker
#               : embed URLs for embed dashboards. This script 
#               : will make an api call with the dashbaord_id,
#               : embed_domain, and urlhost as hardcoded variables.
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the embed user
#
#               : export API_SECRET_ACCESS_KEY=<<AWS Embed API Key>>
#
# Usage         : To run the example embed string api call:
#
#               : python3 invoke_embed_generator_api.py
#

import requests
import os
import json
from aws_requests_auth.aws_auth import AWSRequestsAuth

api_secret_access_key=os.environ['API_SECRET_ACCESS_KEY']

api_id='jdo0epycg8'
region='ca-central-1'
endpoint=f'https://api.analytics.gov.bc.ca/embed/'
params="dashboard_id=120&embed_domain=localhost:8888&urlhost=www2.gov.bc.ca"
headers={"x-api-key": api_secret_access_key}

response = requests.get(endpoint,
                        params=params,
                        headers=headers)

if 'body' in json.loads(response.content.decode('utf-8')):
    print(json.loads(response.content.decode('utf-8'))['body'])
else:
    print(response.content.decode('utf-8'))
