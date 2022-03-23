import requests
import os
import json
import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth

api_secret_access_key=os.environ['API_SECRET_ACCESS_KEY']

api_id='jdo0epycg8'
region='ca-central-1'
api_stage='default'
endpoint=f'https://{api_id}.execute-api.{region}.amazonaws.com/{api_stage}/'
params="dashboard_id=120&embed_domain=localhost:8888&urlhost=www2.gov.bc.ca"
headers={"x-api-key": api_secret_access_key}

response = requests.get(endpoint,
                        params=params,
                        headers=headers)

if 'body' in json.loads(response.content.decode('utf-8')):
    print(json.loads(response.content.decode('utf-8'))['body'])
else:
    print(response.content.decode('utf-8'))
