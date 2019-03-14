## GDX Analytics

This block represents an instance of Government of British Columbia’s Snowplow tracking. This includes pushing custom events to the Snowplow Tracker, and generation of cryptographically signed SSO embed URL pointing to a dashboard.

## Features

Snowplow is a Cloud-native web, mobile and event analytics that runs on AWS (RedShift) which identifies and tracks the way users engage with the website or application.

## Project Status

This project is currently in development mode. The GDX analytics team will contribute to the content of this project as a resource.

## Contents by Directory:

#### [examples/](./examples/)

- proof of concept examples of the code required to add Snowplow instrumentation client applications;
- embed generators in Java and Python demonstrating the generation of cryptographically signed SSO embed URL;
- The `s3-upload.sh` script, to upload files to S3 with standard Unix utilities, for example: to run as a cron job and load scheduled data dumps;
- Snowplow schema files.

#### [microservices/](./microservices/)

- microservices running on EC2 to perform automated data loads of well formed data into RedShift.

#### [web_trackers/](./web_trackers)

- examples of the Javascript tracker used to push custom events to Snowplow;

#### [testing/](./testing/)

- scripts automating the testing strategies of the WebTrends to Snowplow migration.

## Relavant Repositories

#### [GDX-Analytics-Looker-AWS-Cost-And-Usage/](https://github.com/bcgov/GDX-Analytics-Looker-AWS-Cost-And-Usage) 
Provides GDX Analyitics with reporting to track AWS usage, estimated charges, and line items by AWS product, usage type, and operation.
#### [GDX-Analytics-Looker-cfms_block/](https://github.com/bcgov/GDX-Analytics-Looker-cfms_block)
Represents an instance of the Government of British Columbia’s Service BC [LookerML](https://docs.looker.com/data-modeling/learning-lookml/what-is-lookml) project.
#### [GDX-Analytics-Looker-Redshift_Admin_By_AWS/](https://github.com/bcgov/GDX-Analytics-Looker-Redshift_Admin_By_AWS)
Provides a substitute for the AWS Console, helping users identify how tables are structured and if data flow is normal.
#### [GDX-Analytics-Looker-Snowplow-Web-Block/](https://github.com/bcgov/GDX-Analytics-Looker-Snowplow-Web-Block)
Represents an instance of the Government of British Columbia’s [LookerML](https://docs.looker.com/data-modeling/learning-lookml/what-is-lookml) project.
#### [GDX-Analytics-Looker-Webtrends-Testing-Block/](https://github.com/bcgov/GDX-Analytics-Looker-Webtrends-Testing-Block)
Represents the testing related to migration of Government of British Columbia’s data from WebTrends to Looker/Snowplow using [LookerML](https://docs.looker.com/data-modeling/learning-lookml/what-is-lookml).
#### [GDX-Analytics-OpenShift-Snowplow-Gateway-Service/](https://github.com/bcgov/GDX-Analytics-OpenShift-Snowplow-Gateway-Service)
A description will be added here soon.

## Getting Help

Please Contact the GDX Service desk at gcpe.servicedesk@gov.bc.ca for any analytics service help, for inquiries about starting a new analytics account for Government please contact The GDX Analytics team.

## Contributors

The GDX analytics team will be the main contributors to this project currently. They will maintain the code as well. 

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
