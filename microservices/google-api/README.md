# Google API microservices

This directory contains scripts, configs, and DDL files describing the Google API calling microservices implemented on the GDX-Analytics platform.

### Google Search Console API Loader Microservice

The `google_search.py` script automates the loading of Google Search data into S3 (as `.csv`) and Redshift (the `google.googlesearch` schema as defined by `google.googlesearch.sql`) via the Google Search Console API.

The Google Search Console API documentation is here: https://developers.google.com/webmaster-tools/search-console-api-original. The latest data available from the Google Search API is from two days ago (relative to "_now_"). The Search Console API provides programmatic access to most of the functionality of Google Search Console.

The Google Search Console is here: https://search.google.com/search-console. This console helps to visually identify which Properties you have verified owner access to and allows manual querying of slightly more recent data than the API provides programmatic access to (you can see data from 1 day ago, instead of from 2 days ago).

To illustrate: on a Friday, the Search Console web interface would show search data on your property from a maximum range of search data from 18 months ago up until Thursday. However, the Search Console API would only be able to collect a maximum range of search data from 18 months ago up until Wednesday.

The accompanying `google_search.json` configuration file specifies:
 * the S3 bucket where the responses to API queries will be loaded into for storage;
 * the database table where the files stored into S3 will later be loaded to;
 * the Site URLs per property as defined in Search Console, such as "http://www.example.com/" (for a URL-prefix property) or "sc-domain:example.com" (for a Domain property); and
 * optional query start dates per property.

As mentioned, property types may be either _URL-prefixed_ or _Domain properties_. Domain properties delivery search query results for all subdomains and pages contained in that domain. URL-prefixed properties will only return search query results for pages prefixed with that URL. At the Domain property level, data aggregation performed at Google's end may have less detail than the equivalent URL-prefixed data, and as a result, you may observe data discrepancies when comparing one to the other.

We adjust for this difference by preferentially loading data from the URL-prefixed property instead of the Domain property (where both exist) into a persistent derived table generated at the end of the `google_search.py` script.

The microservice will begin loading Google Search data from the date specified in the configuration as `"start_date_default"`. If that is unspecified in the configuration, the script will attempt to load data from 18 months ago relative to the date when the script is run. If more recent data already exists in Redshift; it will load data from _the day after_ the most recent date that has already been loaded into Redshift up to a latest date of two-days ago (relative to the date on which the script is being run).

When run, the script collects property data in batches of 30 days at a time before posting a data file into the S3 bucket specified in the config. If querying recent data, the file will contain 30 days or fewer. For instance: If you set this job up as a cron task, the data file for a given property will typically contain only one day worth of data.

Log files are appended at the debug level into file called `google_search.log` under a `logs/` folder which must be created manually. Info level logs are output to stdout. In the log file, events are logged with the format showing the log level, the function name, the timestamp with milliseconds, and the message: `INFO:__main__:2010-10-10 10:00:00,000:<log message here>`.

#### Configuration

##### Credentials

'credentials.dat' and 'credentials.json' are required to query data through the API.

'credentials.dat' will be generated the first time this script runs after authenticating (you will be instructed on how to authenticate when this runs).

'credentials.json' must be generated according to the instructions at https://developers.google.com/webmaster-tools/search-console-api-original/v3/how-tos/authorizing#APIKey. You must first have a project created at https://console.cloud.google.com/ and associate that project to use the "Google Search Console API".

##### Environment Variables

The Google Search API loader microservice requires the following environment variables be set to run correctly.

- `GOOGLE_MICROSERVICE_CONFIG`: the path to the json configuration file, e.g.: `\path\to\google_search.json`;
- `pgpass`: the database password for the microservice user;
- `AWS_ACCESS_KEY_ID`: the AWS access key for the account authorized to perform COPY commands from S3 to Redshift; and,
- `AWS_SECRET_ACCESS_KEY`: the AWS secret access key for the account authorized to perform COPY commands from S3 to Redshift.

##### Configuration File

The JSON configuration is loaded as an environmental variable defined as `GOOGLE_MICROSERVICE_CONFIG`. It follows this structure:

- `"bucket"`: a string to define the S3 bucket where CSV Google Search API query responses are stored.
- `"dbtable"`: a string to define the Redshift table where the S3 stored CSV files are inserted to to after their creation.
- `"sites"`: a JSON array containing objects defining a `"name"` and an optional `"start_date_default"`.
  - `"name"`: the property URL-prefixed or Domain to query the Google Search API on.
  - `"start_date_default"`: an _optional_ key identifying where to begin queries from as a YYYY-MM-DD string. If excluded, the default behaviour is to look back to the earliest date that the Google Search API exposes, which is 16 months (scripted as 480 days).

```
{
    "bucket": string,
    "dbtable": "google.googlesearch",
    "sites":[
        {
        "name":"https://www2.gov.bc.ca/"
        },
        {
        "name":"sc-domain:gov.bc.ca",
        "start_date_default":"2020-01-01"
        }
    ]
}
```

### Google My Business API Loader microservice

The `google_mybusiness.py` script pulling the Google My Business API data for locations according to the accounts specified in `google_mybusiness.json`. The metrics from each location are consecutively recorded as `.csv` files in S3 and then copied to Redshift.

Google makes location insights data available for a time range spanning 18 months ago to 2 days ago (as tests have determined to be a reliable "*to date*"). From the Google My Business API [BasicMetricsRequest reference guide](https://developers.google.com/my-business/reference/rest/v4/BasicMetricsRequest):
> The maximum range is 18 months from the request date. In some cases, the data may still be missing for days close to the request date. Missing data will be specified in the metricValues in the response.

The script iterates each location for the date range specified on the date range specified by config keys `start_date` and `end_date`. If no range is set (those key values are left as blank strings), then the script attempts to query for the full range of data availability.

Log files are appended at the debug level into file called `google_mybusiness.log` under a `logs/` folder which much be created manually. Info level logs are output to stdout. In the log file, events are logged with the format showing the log level, the function name, the timestamp with milliseconds, and the message: `INFO:__main__:2010-10-10 10:00:00,000:<log message here>`.

#### Configuration

##### Environment Variables

The Google Search API loader microservice requires the following environment variables be set to run correctly.

- `pgpass`: the database password for the microservice user;
- `AWS_ACCESS_KEY_ID`: the AWS access key for the account authorized to perform COPY commands from S3 to Redshift; and,
- `AWS_SECRET_ACCESS_KEY`: the AWS secret access key for the account authorized to perform COPY commands from S3 to Redshift.

##### Command Line Arguments

- `-o` or `--oauth`: the OAuth Credentials JSON file;
- `-a` or `--auth`: the stored authorization dat file;
- `-c` or `--conf`: the microservice configuration file;
- `-d` or `--debug`: runs the microservice in debug mode (currently unsupported).

##### Configuration File

The JSON configuration is required, following a `-c` or `--conf` flag when running the `google_mybusiness.py` script. It follows this structure:

- `"bucket"`: a string to define the S3 bucket where CSV Google My Business API query responses are stored.
- `"dbtable"`: a string to define the Redshift table where the S3 stored CSV files are copied to after their creation.
- `"metrics"`: an list containing the list of metrics to pull from Google My Business
- `"locations"`: an object that annotates account information from clients that have provided us access”
  - `"client_shortname"`: the client name to be recorded in the client column of the table for filtering. This shortname will also map the path where the `.csv` files loaded into AWS S3 as `'client/google_mybusiness_<client_shortname>/'`.
  - `"name"`: The account Name label
  - `"names_replacement"`: a list to replace matched values from the locations under this account as suggested by: `['find','replace']`. For example, in the case of Service BC, all locations are prefixed with "Service BC Centre". We replace this with nothing in order to get _just_ the unique names (the locations' community names).
  - `"id"`: the location group, used for validation when querying the API.
  - `"start_date"`: the query start date as `"YYYY-MM-DD"`, leave as `""` to get the oldest data possible (defaults to the longest the API accepts, 18 months ago)
  - `"end_date"`: the query end date as `"YYYY-MM-DD"`, leave as `""` to get the most recent data possible (defaults to the most recent that the API has been tested to provide, 2 days ago)


### Google My Business Driving Directions Loader Microservice

#### Script

The `google_directions.py` script automates the loading of Google MyBusiness Driving Directions insights reports into S3 (as a `.csv` file), which it then loads to Redshift. Create the logs directory before running if it does not already exist. The script requires a `JSON` config file as specifid in the "_Configuration_" section below. It also must be passed command line locations for Google Credentials files; a usage example is in the header comment in the script itself.

Log files are appended at the debug level into file called `google_directions.log` under a `logs/` folder which must be created manually. Info level logs are output to stdout. In the log file, events are logged with the format showing the log level, the function name, the timestamp with milliseconds, and the message: `INFO:__main__:2010-10-10 10:00:00,000:<log message here>`.

#### Table

The `google.gmb_directions` schema is defined by the [`google.gmb_directions.sql`](./`google.gmb_directions.sql) ddl  file.

#### Configuration

##### Environment Variables

The Google Search API loader microservice requires the following environment variables be set to run correctly.

- `pgpass`: the database password for the microservice user;
- `AWS_ACCESS_KEY_ID`: the AWS access key for the account authorized to perform COPY commands from S3 to Redshift; and,
- `AWS_SECRET_ACCESS_KEY`: the AWS secret access key for the account authorized to perform COPY commands from S3 to Redshift.

##### Command Line Arguments

- `-o` or `--oauth`: the OAuth Credentials JSON file;
- `-a` or `--auth`: the stored authorization dat file;
- `-c` or `--conf`: the microservice configuration file;
- `-d` or `--debug`: runs the microservice in debug mode (currently unsupported).

##### Configuration File

The configuration for this microservice is in the `google_directions.json` file.

The JSON configuration fields are as described below:

| Key label | Value type | Value Description |
|-|-|-|
| `bucket` | string | The bucket name to write to |
| `dbtable` | string | The table name in Redshift to insert on |
| `destination` | string | A top level path in the S3 bucket to deposit the files after processing (good or bad), and also to check for to determine if this microservice was already run today (in order to avoid inserting duplicate data) |
| `locationGroups[]` | object (`location`) | objects representing locations, described below. This is an object to in order to accommodate future expansion on this field as necessary. |

`location` has been structured as an object in order to allow easier future extensibility, if necessary. The fields currently set in `location` are described below:

| Key label | Value type | Value Description |
|-|-|-|
| `clientShortname` | string | An internal shortname for a client's location group. An environment variable must be set as: `<clientShortname>_accountid=<accountid>` in order to map the Location Group Account ID to this client shortname and pull the API data. The `clientShortname` is also used to set the object path on S3 as: `S3://<bucket>/client/google_mybusiness_<clientShortname>` |
| `aggregate_days[]` | string | A 1 to 3 item list that can include only unique values of `"SEVEN"`, `"THIRTY"` or `"NINETY"` |

## Project Status

As clients provide GDX Analytics with access to their Google Search of My Business profiles, they will be added to the configuration file to be handled by the microservice.

## Getting Help

Please Contact the GDX Service desk for any analytics service help. For inquiries about Google Search API integration or for inquiries about starting a new analytics account for Government, please contact The GDX Analytics team.

## Contributors

The GDX analytics team will be the main contributors to this project currently and will maintain the code.

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
