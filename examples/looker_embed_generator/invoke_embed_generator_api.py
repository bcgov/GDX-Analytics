import requests
import os
import json
import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth

aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']

api_id='jdo0epycg8'
region='ca-central-1'
api_stage='default'
endpoint=f'https://{api_id}.execute-api.{region}.amazonaws.com/{api_stage}/'
headers={"params":"dashboard_id=120&urlhost=www2.gov.bc.ca"}

session = boto3.Session(aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        )
credentials = session.get_credentials()

auth = AWSRequestsAuth(aws_access_key=credentials.access_key,
                       aws_secret_access_key=credentials.secret_key,
                       aws_host=f'{api_id}.execute-api.{region}.amazonaws.com',
                       aws_region=region,
                       aws_service='execute-api')

response = requests.get(endpoint,
                        auth=auth, 
                        headers=headers)

print(json.loads(response.content.decode('utf-8'))['body'])

