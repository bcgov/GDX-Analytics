# Google API microservices

This directory contains scripts, configs, and DDL files describing the Google API calling microservices implemented on the GDX-Analytics platform.

### Google Search API Loader Microservice

The `google_search.py` script automates the loading of Google Search API data into S3 (as `.csv`) and Redshift (the `google.googlesearch` schema as defined by `google.googlesearch.sql`).

The accompanying `google_search.json` configuration file specifies the bucket, schema, the sites to query the Google Search API for, and optional start dates on those sites.

The microservice will begin loading Google data from the date specified in the configuration as `"start_date_default"`. If that is unspecified, it will attempt to load data from 18 months ago relative to the script runtime. If more recent data already exists; it will load data from the day after the last date that has already been loaded into Redshift.

It currently runs in batches of a maximum of 30 days at a time until 2 days ago (the latest available data from the Google Search API).

#### Configuration

The JSON configuration is loaded as an environmental variable defined as `GOOGLE_MICROSERVICE_CONFIG`. It follows this structure:

- `"bucket"`: a string to define the S3 bucket where CSV Google Search API query responses are stored.
- `"dbtable"`: a string to define the Redshift table where the S3 stored CSV files are inserted to to after their creation.
- `"sites"`: a JSON array containing objects defining a `"name"` and an optional `"start_date_default"`.
  - `"name"`: the site URL to query the Google Search API on.
  - `"start_date_default"`: an _optional_ key identifying where to begin queries from as a YYYY-MM-DD string. If excluded, the default behaviour is to look back to the earliest date that the Google Search API exposes, which is 16 months (scripted as 480 days).

```
{
    "bucket": string,
    "dbtable": "google.googlesearch",
    "sites":[
        {
        "name":"https://www2.gov.bc.ca/"
        }
    ]
}
```

### Google My Business API Loader microservice

The `google_mybusiness.py` script pulling the Google My Business API data for locations according to the accounts specified in `google_mybusiness.json`. The metrics from each location are consecutively recorded as `.csv` files in S3 and then copied to Redshift.

Google makes location insights data available for a time range spanning 18 months ago to 2 days ago (as tests have determined to be a reliable "*to date*"). From the Google My Business API [BasicMetricsRequest reference guide](https://developers.google.com/my-business/reference/rest/v4/BasicMetricsRequest):
> The maximum range is 18 months from the request date. In some cases, the data may still be missing for days close to the request date. Missing data will be specified in the metricValues in the response.

The script iterates each location for the date range specified on the date range specified by config keys `start_date` and `end_date`. If no range is set (those key values are left as blank strings), then the script attempts to query for the full range of data availability.

#### Configuration

- `"bucket"`: a string to define the S3 bucket where CSV Google My Business API query responses are stored.
- `"dbtable"`: a string to define the Redshift table where the S3 stored CSV files are copied to to after their creation.
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

The `google_directions.py` script automates the loading of Google MyBusiness Driving Directions insights reports into S3 (as a `.csv` file), which it then loads to Redshift. When run, logs are appended to `logs/google_directions.log`. Create the logs directory before running if it does not already exist. The script requires a `JSON` config file as specifid in the "_Configuration_" section below. It also must be passed command line locations for Google Credentials files; a usage example is in the header comment in the script itself.

#### Table

The `google.gmb_directions` schema is defined by the [`google.gmb_directions.sql`](./`google.gmb_directions.sql) ddl  file.

#### Configuration

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
