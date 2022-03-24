# Measure Tile Performance

This Measure Tile Performance script, `measure_tile_performance.py` will output the runtime results of running a given input query (based on a Looker Explore slug) a given number of times.

It runs by invoking the Looker API, which requires Base URL, API Keys and other config settings which are set as environment variables. The script is setup to not pull any cached query results and run a fresh query with each run.

The script takes positional command line arguments to set the Explore slug and the number of times you want to run the query.

The standard output to the command line will report the duration of each query as a list. The _min_, _max_, _average_, and _standard deviation_ of the query runtimes is also reported. It will optionally output a csv file with the headers:

```
SlugID, Timestamp, RunTime
```

Format:
 - `SlugID`: The slugID that was provided as the first argument when running the script (see "Running" section below).
 - `Timestamp`: The ISO 8601 Looker system time timestamp converted from UTC into the America/Vancouver timezome, such as: `2022-01-25T13:39:16-08:00`.
 - `RunTime`: The query runtime duration in seconds.

User can put a time delay(seconds) between each query to save looker from clogging. User can change set time delay by using `<arg3>` as explained below. If it is not set then there is no delay between queries.

## Configuration of environment variables if running locally

These variables are already set in EC2 and following instructions are to setup these variables in case you want to run this script locally.

Every authorized Looker user can create their own values for __"Client ID"__ and __"Client Secret"__ for use with the Looker API. To find these values:

 1. navigate to the Looker [Users Admin panel](https://analytics.gov.bc.ca/admin/users);
 2. search for your user;
 3. click the "_Edit_" button to open your user configuration screen;
 4. click on "_Edit Keys_" button under the "__Api3__" section;
 5. if "No API3 keys found", click the "_New API3 Key_" button to generate a new Client ID and Client Secret pair;
    - you may optionally delete and recreate key Client ID and Client Secret pairs, or create multiple key pairs for different uses. Keep in mind deleting these pairs will require updating the environment variables, and deleted keys will no longer work if being used elsewhere.
 6. record the values for your Client ID and Client Secret.

Update environment variables locally to replace the values for Client ID and Client Secret recorded in the previous steps:

```
[...]
export LOOKERSDK_CLIENT_ID=__"Client ID"__
export LOOKERSDK_CLIENT_SECRET=__"Client Secret"__
export LOOKERSDK_BASE_URL="https://analytics.gov.bc.ca:19999"
export LOOKERSDK_VERIFY_SSL=True
export LOOKERSDK_TIMEOUT=600
[...]
```

## Installation

Install using Pipenv to get the dependencies specified in the `Pipfile.lock`:

```
pipenv install --ignore-pipfile
```

## Running `measure_tile_performance.py`

The `measure_tile_performance.py` script requires positional arguments:
 - `<arg1>` accepts a Looker Explore slug, which it will use to determine the Query ID to run. You can use the Looker explore page to build a query and then to find the Slug, click on the URL in the browser window. The part between "qid=" and "&origin" is the slug that you need for next steps. Copy these slugs in your documentation table.

For example the **hmbjQaHfeDbrtAsoCCBofP** part of this link is slug.

https://analytics.gov.bc.ca/explore/snowplow_web_block/page_views?qid=hmbjQaHfeDbrtAsoCCBofP&origin_space=37&toggle=vis 

Slug for above explore = hmbjQaHfeDbrtAsoCCBofP
 - `<arg2>` accepts an integer, which is the number of times you want to run the query (the script will take the value between 1 and 100)

 Optional arguments: 
 - `<arg3>` accepts an integer, which is number of seconds you want to delay between each query run. If nothing is specified then default value is 0s. Skip this argument if you are running this script in non-businesss hours using cron.

 - `-f` or `--file`: flag to write output to a csv file. It will create a csv file with the name `<slug>_<datetime>.csv` when `<slug>` is slug id of query you are running and `<datetime>` is the local system timestamp of when script was run as `YYYYMMDDTHHMMSS` (ISO 8601 format).

When executing `measure_tile_performance.py`, use `pipenv run` to invoke the pipenv installed python environment.

### Example with the SleepTimer and csv file:
```
pipenv run python measure_tile_performance.py <arg1> <arg2> <arg3> -f
```
The following example is using slug `TPvGJfrWSmqCAw7w8GnQ3w` which will run the query 2 times with delay of 10s between each query and create a csv file.

```
pipenv run python measure_tile_performance.py TPvGJfrWSmqCAw7w8GnQ3w 2 10 -f
```

### Example without SleepTimer and without csv file:

```
pipenv run python measure_tile_performance.py <arg1> <arg2>
```
The following example is using slug `TPvGJfrWSmqCAw7w8GnQ3w`, run the query 2 times with delay of default 300s between each query because `<arg3>` is not set and will not create a csv file because `-f` is not used.

```
pipenv run python measure_tile_performance.py TPvGJfrWSmqCAw7w8GnQ3w 2 
```
## Running using Cron

Use this procedure https://apps.itsm.gov.bc.ca/confluence/display/ANALYTICS/Measure+Looker+Tile+Performance to run this script via cron.
