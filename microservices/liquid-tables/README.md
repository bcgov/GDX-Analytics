# Liquid Tables Microservice

This folder contains a script that runs SQL queries against a Redshift database. The SQL files currently being used by this script are stored in the [sql](./sql/) folder. This microservice was built to provide the option for use by LookML [liquid variable](https://docs.looker.com/reference/liquid-variables) logic to select between different tables depending on a Dashboard users' filter choices. The intention is to deliver shorter query runtimes for default dashboard filters.

## `liquid-tables.py`

The S3 to Redshift microservice is invoked through pipenv and requires a `sql` file passed as a positional argument.

To confiure the pipenv, run:

```
pipenv install
```

to use, run a command like:

```
pipenv run python liquid-tables.py sql/<filename>.slq
```

#### Environment Variables

The liquid tables microservice invokes (../lib/redshift.py)[../lib/redshift.py], which requires the  database password for the microservice user set as the `pgpass` environment variable.

## Project Status

As new data requirements for optimization are identified, new sql files will be prepared to support those. This project is ongoing.

## Getting Help

For any questions regarding this project, please contact the GDX Analytics Team.

## Contributors

The GDX analytics team will be the main contributors to this project currently and will maintain the code.

## License

```
Copyright 2015 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
```
