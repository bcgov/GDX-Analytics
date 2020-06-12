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
        "configurationItem", {}).get("resourceType") or event.get(
            "detail", {}).get("configurationItemSummary", {}).get(
                "resourceType")
    resourceName = event.get("detail", {}).get(
        "configurationItem", {}).get("resourceName") or event.get(
            "detail", {}).get(
        "configurationItemSummary", {}).get("resourceId")
    changeType = event.get("detail", {}).get(
        "configurationItemDiff", {}).get("changeType") or event.get(
            "detail", {}).get("configurationItemSummary", {}).get("changeType")
    changeTypeMap = {'UPDATE': 'updated',
                     'CREATE': 'created', 'DELETE': 'deleted'}
    changeTypeStr = changeTypeMap.get(changeType, changeType)
    detailTypeMap = {'Config Configuration Item Change': {
        'subject': f'AWS Config Item Change: {resourceType} {changeTypeStr}'
        if resourceType is not None and changeTypeStr is not None else
        'AWS Config Item Change',
        'summary': f'{resourceType} {resourceName} has been {changeTypeStr}.'
        + '\nSuggested action: none, unless the change is unauthorized.'
        if resourceType is not None and changeTypeStr is not None
        and resourceName is not None else None}}
    publishArgs = {'TargetArn': targetSnsArn, 'MessageStructure': 'json'}
    evtDetailType = event.get('detail-type')
    detailTypeEntry = detailTypeMap.get(evtDetailType, {})
    subject = detailTypeEntry.get('subject', evtDetailType)
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
