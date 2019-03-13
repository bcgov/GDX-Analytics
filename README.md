## GDX Analytics

This is for the Government of British Columbia’s instance of Snowplow tracking. Snowplow is a Cloud-native web, mobile and event analytics, running on AWS (RedShift).

## Features

Identifies and tracks the way your users engage with your website or application.

## Project Status

Currently this project is still in development.

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

## Getting Help

Please Contact the GDX Service desk for any analytics service help, for inquiries about starting a new analytics account for Government please contact The GDX Analytics team.

## Contributors

The GDX analytics team will be the main contributors to this project currently. They will also maintain the code as well. 

## License


    Copyright 2015 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
