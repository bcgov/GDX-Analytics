import json
import boto3
import os

# local invoke debug only
# comment out following 4 lines when build for deploying
# import ptvsd
# print('Attach debugger to proceed...')
# ptvsd.enable_attach(address=('0.0.0.0', 5890), redirect_output=True)
# ptvsd.wait_for_attach()


def lambda_handler(event, context):
    targetSnsArn = os.getenv('TARGET_SNS_ARN')
    print(f'env TARGET_SNS_ARN={targetSnsArn}')  # noqa: E999
    if targetSnsArn == 'changeMe' or targetSnsArn is None:
        return
    resourceType = event.get("detail", {}).get(
        "configurationItem", {}).get("resourceType")
    resourceName = event.get("detail", {}).get(
        "configurationItem", {}).get("resourceName")
    changeType = event.get("detail", {}).get(
        "configurationItemDiff", {}).get("changeType")
    changeTypeMap = {'UPDATE': 'updated',
                     'CREATE': 'created', 'DELETE': 'deleted'}
    changeTypeStr = changeTypeMap.get(changeType, changeType)
    detailTypeMap = {'Config Configuration Item Change': {
        'subject': 'AWS Config Item Change',
        'summary': f'{resourceType} {resourceName} has been {changeTypeStr}.'}}
    publishArgs = {'TargetArn': targetSnsArn, 'MessageStructure': 'json'}
    detailTypeEntry = detailTypeMap.get(event.get('detail-type'), {})
    subject = detailTypeEntry.get('subject')
    if subject is not None:
        publishArgs['Subject'] = subject
    summary = detailTypeEntry.get('summary')
    eventStr = json.dumps(event, indent=2)
    msgString = eventStr
    if summary is not None:
        msgString = summary + '\n\n' + eventStr
    message = json.dumps({'default': msgString})
    publishArgs['Message'] = message
    client = boto3.client('sns')
    client.publish(**publishArgs)
