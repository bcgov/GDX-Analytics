# Measure Tile Performance

This Measure Tile Performance script, `measure_tile_performance.py` will output the runtime results of running a given input query (based on a Looker Explore slug) a given number of times.

It runs by invoking the Looker API, which requires API Keys to access which must be set in the `looker.ini` file.

The script takes positional command line arguments to set the Explore slug and the number of times you want to run the query.

The output on the command line will report the duration of each query as a list and the _min_, _max_, and _average_ query runtimes of those queries. It will optionally output a csv file with the headers:

```
SlugID, Timestamp, RunTime
```

Format:
 - `SlugID`: The slugID that was provided as the first argument when running the script (see "Running" section below).
 - `Timestamp`: The ISO 8601 Looker system time timestamp converted from UTC into the America/Vancouver timezome, such as: `2022-01-25T13:39:16-08:00`.
 - `RunTime`: The query run duration in seconds.

There will be a time delay of 5 mins between each query to save looker from clogging.


## Configuration of Looker.ini
The user must copy `looker.ini.dist` file to thier local home directory and rename it to `looker.ini`. This step is added to prevent looker.ini being committed to source control. 

The user must provide API client and secret keys in the `looker.ini` file.

Every authorized Looker user can create their own values for __"Client ID"__ and __"Client Secret__" for use with the Looker API. To find these values:

 1. navigate to the Looker [Users Admin panel](https://analytics.gov.bc.ca/admin/users),
 2. search for your user;
 3. click the "_Edit_" button to open your user configuration screen;
 4. click on "_Edit Keys_" button under the "__Api3__" section;
 5. if "No API3 keys found", click the "_New API3 Key_" button to generate a new Client ID and Client Secret pair;
    - you may optionally delete and recreate key Client ID and Client Secret pairs, or create multiple key pairs for different uses. Keep in mind deleting these pairs will require updating the `looker.ini` file, and deleted keys will no longer work if being used elsewhere.
 6. record the values for your Client ID and Client Secret.

Update `looker.ini` replace the values for Client ID and Client Secret recorded in the previous steps:

```
# API 3 client 
## Replace <client_id> with your Client ID
client_id="<client_id>"
# API 3 
## Replace <client_secret> with your client secret
client_secret="<client_secret>"
```

> These are secret values unique to your user, and should not be shared. After changing `looker.ini`, do not add that change to a git commit record. The Client ID and Client Secret pairs can be deleted and new ones recreated from the Looker interface if required.

## Installation

Use Pipenv to handle dependencies and run the script:

```
pipenv install
```


## Running `measure_tile_performance.py`

The `measure_tile_performance.py` script requires positional arguments:
 - `<arg1>` accepts a Looker Explore slug, which it will use to determine the Query ID to run. You can use the Looker explore page to build a query and then choose the 'Share' option to show the share url for the query. "Share" option can be found by clicking on the gear icon on top right section of an explore. Share urls generally look something like 'https://analytics.gov.bc.ca/x/UnBMGQaMNRhiTy2nhbcXdl'. The trailing 'UnBMGQaMNRhiTy2nhbcXdl' is the share slug.
 - `<arg2>` accepts an integer, which is the number of times you want to run the query (the script will take the value between 1 and 100)

 Optional arguments:
 - `-f` or `--file`: flag to write output to a csv file. It will create a csv file with the name `<slug>_<datetime>.csv` when `<slug>` is slug id of query you are running and `<datetime>` is the local system timestamp of when script was run as `YYYYMMDDTHHMMSS` (ISO 8601 format).

When invoking `measure_tile_performance.py`, use Pipenv run.

### Example with a csv file:
```
pipenv run python measure_tile_performance.py <arg1> <arg2> -f

pipenv run python measure_tile_performance.py MWPGYXQO8rj4ha3PWQAM7d 2 -f
```

### Example without a csv file:

```
pipenv run python measure_tile_performance.py <arg1> <arg2>

pipenv run python measure_tile_performance.py MWPGYXQO8rj4ha3PWQAM7d 4
```
