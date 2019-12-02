# GDX Analytics Microservices

These microservice scripts automate the loading of data from a well formed `csv` file stored in S3 to Redshift. They use `json` configuration files to specify the expected form of input data and of other options pertaining to processing and output operations. Logging for these services is output to stdout at the INFO level; and aggregated at the DEBUG level to files named as: `./logs/<microservice_name>.log`.

## [S3 to Redshift Microservice](./s3_to_redshift)

The S3 to Redshift microservice will read the config `json` to determine the input data location, it's content and how to process that (including column data types, content replacements, datetime formats), and where to output the results (the Redshift table). Each processed file will land in a `<bucket>/processed/` folder in S3, which can be `/processed/good/` or `/processed/bad/` depending on the success or failure of processing the input file. The Redshift `COPY` command is performed as a single transaction which will not commit the changes unless they are successful in the transaction.

## [CMS Lite Metadata Microservice](./cmslitemetadata_to_redshift)

The CMS Lite Metadata microservice emerged from a specialized use case of the S3 to Redshift microservice which required additional logic to build Lookup tables and Dictionary tables, as indicated though input data columns containing nested delimiters. To do so, it processes a single input `csv` file containing metadata about pages in CMS Lite, to generate several batch CSV files as a batch process. It then runs the `COPY` command on all of these files as a single Redshift transaction. As with the S3 to Redshift Microservice, The `json` configuration files specify the expected form of input data and output options.

## [Google API Microservices](./google-api)

The Google API microservices are a collection of scripts to automate the loading of data collected through various Google APIs such as the [Google My Business API](https://developers.google.com/my-business/) for Location and Driving Direction insights; and the [Google Search Console API](https://developers.google.com/webmaster-tools/) for Search result analytics. Upon accessing the requested data, the Google API microservices build an output `csv` file containing that data, and stores it into S3. From there, the loading of data from S3 to Redshift follows very closely to the flow described in the S3 to Redshift microservice.

## [Secure File Transfer System microservice](./sfts)

The [`/sfts`](./sfts) folder contains the Secure File Transfer System microservice. This was configured first to support Performance Management and Reporting Program (PMRP) data exchange. This microservice is triggered to run after the successful transfer of PMRP date into Redshift. The microservice first generates an object in S3 from the output of a Redshift transaction modelling PMRP data with other GDX Analytics data, and then transfers that object from S3 to an upload location on BCGov's Secure File Transfer Service. The microservice is two scripts; one to generate the objets in S3 based on Redshift queries (`redshift_to_s3.py`) and one to transfer previously un-transferred files from S3 to SFTS (`s3_to_sfts.py`).

## Project Status

The microservices in this project are still under development.

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
