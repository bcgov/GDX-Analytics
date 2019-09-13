# S3 to Redshift Microservice

This folder contains scripts and configuration files (within the [config.d](./config.d/) folder) that enable the the S3-to-Redshift microservice implemented on the GDX-Analytics platform.

## `s3_to_redshift.py`

The S3 to Redshift microservice requires a `json` configuration file passed as a second command line argument to run. The configuration file format is described in more detail below. Usage is like:

```
python s3_to_redshift.py configfile.json
```

### Overview

This script reads an input `csv` file one at a time from a list of one or more files. The data contained in the input file is read into memory as a [Pandas dataframe](https://pandas.pydata.org/pandas-docs/stable/reference/frame.html) which is manipulated according to options set in the config file. The final dataframe is written out to S3 as `<bucket_name>/batch/<path-to-file>/<object_summary.key>.csv`, where:
- the bucket is specified from the configuration file,
- the path to file matches the path to the input file (conventionally, we use `/client/service_name/<object_summary.key>.csv`), and
- the object summary key can be thought of as the filename (S3 stores data as objects, not files).

Next, a Redshift transaction attempts to `COPY` that file into Redshift as a single `COMMIT` event (this is done in order to fail gracefully with rollback if the transaction cannot be completed successfully).

Finally, if the transaction failed then the input is copied from `<bucket_name>/client/<path-to-file>/<object_summary.key>.csv` to the "`bad`" folder at `<bucket_name>/processed/bad/<path-to-file>/<object_summary.key>.csv`. Otherwise the successful transaction will result in the input file being copied to the "`good`" folder: `<bucket_name>/processed/good/<path-to-file>/<object_summary.key>.csv`.

### Configuration

The JSON configuration is loaded as a second argument when running the `s3_to_redshift.py` script. It follows this structure:

- `"bucket"`: the label defining the S3 bucket that the microservice will reference.
- `"source"`: the top level S3 prefix for source objects after the bucket label, as in: `<bucket>/<source>/<client>/<doc>`.
- `"destination"`: the top level S3 prefix for processed objects to be stored, as in: `<bucket>/<destination>/<client>/<doc>`.
- `"directory"`: the S3 prefix to follow source or destination and before the `<doc>` objects.
- `"doc"`: a regex pattern representing the final object after all directory prefixes, as in: `<bucket>/<source>/<client>/<doc>`.
- `"dbschema"`: An optional String defaulting to `'microservice'` _(currently unused by `s3_to_redshift.py`)_.
- `"dbtable"`: The table to `COPY` the processed data into _with the schema_, as in: `<schema>.<table>`.
- `"column_count"`: The number of columns the processed dataframe should contain.
- `"columns"`: A list containing the column names of the input file.
- `"column_string_limit"`: A dictionary where keys are names of string type column to truncate, and values are integers indicating the length to truncate to.  
- `"dtype_dic_strings"`: A dictionary where keys are the names of columns in the input data, and the keys are strings defining the datatype of that column.
- `"delim"`: specify the character that deliminates data in the input `csv`.
- `"truncate"`: boolean (`true` or `false`) that determines if the Redshift table will be truncated before inserting data, or instead if the table will be extended with the inserted data.
- `"dateformat"` a list of dictionaries containing keys: `field` and `format`
  - `"field"`: a column name containing datetime format data.
  - `"format"`: strftime to parse time. See [strftime documentation](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) for more information on choices.

The structure of the config file should resemble the following:

```
{
  "bucket": String,
  "source": String,
  "destination": String,
  "directory": String,
  "doc": String,
  "dbschema": String,
  "dbtable": String,
  "columns": [String],
  "column_count": Integer,
  "columns_metadata": [String],
  "columns_lookup": [String],
  "dbtables_dictionaries": [String],
  "dbtables_metadata": [String],
  "replace": [
    {
      "field": String,
      "old": String,
      "new": String
    }
  ],
  "column_string_limit":{
    "<column_name_1>": Integer
  }
  "dateformat": [
    {
      "field": String,
      "format": String
    }
  ],
  "dtype_dic_strings": [String],
  "delim": String,
  "nested_delim": String,
  "truncate": boolean
}
```

## Project Status

As new data sources become available, new configuration files will be prepared to support the consumption of those data sources. This project is ongoing.

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
