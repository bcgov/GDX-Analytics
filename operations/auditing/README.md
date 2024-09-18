# Site Query Auditing Report Generator
The script *createAuditReport.py* in this folder generates an auditing report about queries performed by Looker dashboard users, excluding administrators, against a given web site in the format of CSV containing following columns:

* Date & Time
* Looker User Id
* User Display Name
* User Embed Id
* Query Text

## Prerequisites
* The process [Copy Looker SQL query Logs](../../maintenance/copySqlQuery) is in place
* The machine running the script must have
  * Python 3.8
  * [pipenv](https://github.com/pypa/pipenv)
  * access to Redshift
  * access to Looker API endpoint
* You need to have
  * Redshift login credentials
  * Looker API4 keys

## Setup
Download the git repo to host machine, change *`pwd`* to repo root folder, and run

```
$ cd audting
$ pipenv install
```
Optionally, set following environment variables if you don't want to supply the information in every invocation.

* PGHOST - Redshift host
* PGUSER - Redshift user name
* PGPASSWORD - Redshift user password
* lookerUrlPrefix - Looker url prefix such as https://looker.local:19999/api/4.0

## Usage

```
$ pipenv run python createAuditReport.py -h
usage: createAuditReport.py [-h] [-s LOOKERCLIENTSECRET] [-H PGHOST] [-u PGUSER] [-p PGPASSWORD] [-l LOOKERURLPREFIX] [-f FILE] siteHost lookerClientId

Generate auditing report for a given site host.

positional arguments:
  siteHost              site host such as my-site.gov.bc.ca
  lookerClientId        your looker client id

optional arguments:
  -h, --help            show this help message and exit
  -s LOOKERCLIENTSECRET, --lookerClientSecret LOOKERCLIENTSECRET
                        your looker client secret
  -H PGHOST, --pgHost PGHOST
                        Redshift host overriding env var PGHOST
  -u PGUSER, --pgUser PGUSER
                        Redshift user name overriding env var PGUSER
  -p PGPASSWORD, --pgPassword PGPASSWORD
                        Redshift user password overriding env var PGPASSWORD
  -l LOOKERURLPREFIX, --lookerUrlPrefix LOOKERURLPREFIX
                        Looker url prefix such as https://looker.local:19999/api/3.1 overriding env var lookerUrlPrefix
  -f FILE, --file FILE  Write results to a csv file at the specified path
```
If any required information is neither supplied in env var nor cmd arg, you will be prompted to enter it.

Examples

```
$ pipenv run python createAuditReport.py foo.com myLookerClientId -s myLookerClientSecret -f report.csv
Enter your looker client secret:
```
Generate report for site *foo.com* into file *report.csv* if PGHOST, PGUSER, PGPASSWORD and lookerUrlPrefix have been supplied via environment variables.
```
$ pipenv run python createAuditReport.py -H redshift.host -u reshift_user -p reshift_user_password -l https://looker.local:19999/api/4.0 -s myLookerClientSecret www.foo.com myLookerClientId -f report.csv
```
Generate report for site *foo.com* into file *report.csv*, supplying all required information via command arguments.

## Getting Help

These scripts are intented for internal use. Please contact the GDX Analytics Team for more information.

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
See the License for the specific language governing permissions and limitations under the License.
