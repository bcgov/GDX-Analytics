import json
import boto3
import os

# local invoke debug only
# comment out following 3 lines when build for deploying
# import ptvsd
# ptvsd.enable_attach(address=('0.0.0.0', 5890), redirect_output=True)
# ptvsd.wait_for_attach()


def lambda_handler(event, context):
    targetSnsArn = os.getenv('TARGET_SNS_ARN')
    print(f'env TARGET_SNS_ARN={targetSnsArn}')  # noqa: E999
    if targetSnsArn == 'changeMe' or targetSnsArn is None:
        return
    client = boto3.client('sns')
    client.publish(
        TargetArn=targetSnsArn,
        Message=json.dumps({'default': json.dumps(event, indent=2)}),
        MessageStructure='json'
    )
