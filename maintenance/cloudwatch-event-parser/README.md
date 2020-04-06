# Cloudwatch Event Parser

This project contains source code and supporting files for a serverless 
application to fomat incoming json object and publish to a SNS topic.

## Why

AWS Config sends detailed information about the configuration changes and
notifications to Amazon CloudWatch Events. Rules can be defined in CloudWatch
to filter the events and send to downstreams such as SNS. However, the 
filtered events is not properly formatted, making it less readable when received
by SNS subscribers. This application adds the json formatting
function to the event processing pipeline.

## Components
The project is built using [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html). 
It includes  following files and folders

- json_formatter - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- template.yaml - A template that defines the application's AWS resources.
- samconfig.toml - sam deploy defaults

## Deploy the application

### Prerequisites

* [Python 3.7](https://www.python.org/downloads/)
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

### Build and Deploy
To build and deploy your application for the first time, run the following in your shell:

```
sam build
sam deploy --guided --profile <your-aws-cli-profile>
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Parameter targetSNSArnParameter**: The SNS topic Arn to publish parsed event to. If leaving to default *changeMe*, the function essentially will do nothing.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

## Useage
This Lambda function is designed to be used in a CloudWatch event rule. Just 
set the rule target to this Lambda function.

## Use the SAM CLI to build and test locally

Build your application 

```bash
cloudwatch-event-parser$ sam build
```

The SAM CLI installs dependencies defined in `json_formatter/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```
cloudwatch-event-parser$ sam local invoke JsonFormatterFunction --event events/event.json
```
Note: local invoke may not yield desired outcome due to inadequate permission 
context support of SAM

### Step-through debugging with VS Code
To enable step-through debugging, 
 1. Open [app.code-workspace](./app.code-workspace) in VS Code
 2. uncomment following 3 lines in [json_formatter/app.py](./json_formatter/app.py#L7)

    ```
    # import ptvsd
    # ptvsd.enable_attach(address=('0.0.0.0', 5890), redirect_output=True)
    # ptvsd.wait_for_attach()
    ```
 3. Set a breakpoint in json_formatter/app.py
 4. Run

    ```
    sam build
    sam local invoke -e events/event.json -d 5890 JsonFormatterFunction
    ```
    The last cmd will hung waiting for a debugger to be attached.
 5. Hit `F5` to start debugging

## Cleanup

```
aws cloudformation delete-stack --stack-name GovBC-GDX-cloudwatch-event-parser --profile <your-aws-cli-profile>
```

## Project Status

This project is ongoing.

## Getting Help

For any questions regarding this project, please contact the GDX Analytics Team.

## Contributors

The GDX Analytics Team will be the main contributors to this project currently. They will maintain the code as well.

## License

Copyright 2015 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.