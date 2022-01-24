# Looker API Query Performance Timer

This Looker API Query Performance Timer script, `looker_api_connect.py` will output the runtime results of running a given input query (based on a Looker Explore slug) a given number of times.

It runs by invoking the Looker API, which requires API Keys to access which must be set in the `config/looker.ini` file.

The script takes positional command line arguments to set the Explore slug and the number of times you want to run the query.

The output on the command line will report the duration of each query as a list and the _min_, _max_, and _average_ query runtimes of those queries. It will optionally output a csv file with the headers:

`explore_slug, invokation_timestamp, query_runtime`

## Installation

Use Pipenv to handle dependencies and run the script:
```
pipenv install
```
## Configuration

The user must provide API client and secret keys in the `config/looker.ini` file.

Every authorized Looker user can create their own values for __"Client ID"__ and __"Client Secret__" for use with the Looker API. To find these values:

 1. navigate to the Looker [Users Admin panel](https://analytics.gov.bc.ca/admin/users),
 2. search for your user;
 3. click the "_Edit_" button to open your user configuration screen;
 4. click on "_Edit Keys_" button under the "__Api3__" section;
 5. if "No API3 keys found", click the "_New API3 Key_" button to generate a new Client ID and Client Secret pair;
    - you may optionally delete and recreate key Client ID and Client Secret pairs, or create multiple key pairs for different uses. Keep in mind deleting these pairs will require updating the `looker.ini` file, and deleted keys will no longer work if being used elsewhere.
 6. record the values for your Client ID and Client Secret.

Update config/looker.ini replace the values for Client ID and Client Secret recorded in the previous steps:

```
# API 3 client 
client_id="<client_id>"  ## Replace <client_id> with your Client ID
# API 3 
client_secret="<client_secret>"  ## Replace <client_secret> with your client secret
```

> These are secret values unique to your user, and should not be shared. After changing `looker.ini`, do not add that change to a git commit record. The Client ID and Client Secret pairs can be deleted and new ones recreated from the Looker interface if required.

## Running `looker_api_connect.py`

The `looker_api_connect.py` script requires positional arguments:
 - <arg1> accepts a Looker Explore slug, which it will use to determine the Query ID to run.
 - <arg2> accepts an integer, which is the number of times you want to run the query (the script will take the minimum of this value and 100)
 - __TODO__: instructions for CSV file creation

When invoking `looker_api_connect.py`, use Pipenv run.

### Example:

```
pipenv run python looker_api_connect.py <arg1> <arg2>
```
