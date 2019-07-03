## S3 to Redshift Microservice

These microservice scripts automate the migration of well formed `csv` data on S3 into Redshift. The `json` configuration files specify the expected form of data.

Logging for these services is output to stdout at the INFO level; and aggregated at the DEBUG level to the files named `./logs/<microservice_name>.log`.

## Project Status

Currently this project is still in development.

The `cmslitemetadata_to_redshift` diverged from `s3_to_redshift` to process data containing nested delimeters, requiring dictonary and lookup tables; but due to inherent overlap, these scripts are good candidates for consolidation.

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
