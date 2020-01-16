# Secure File Transfer System microservice

This folder contains scripts, configuration files (within the [config.d](./config.d/) folder), and SQL formatted DML files (within the [dml](./dml/) folder) that enable the the Secure File Transfer System (SFTS) microservice implemented on the GDX-Analytics platform.


## Overview

Two scripts exist to separate their functions into smaller, potentially independently operating services. Used together in sequence, they perform the overall function of copying data from Redshift to SFTS. S3 and EC2 are required as intermediary services (EC2 to execute the scripts and store and modify temporary files, and S3 to store objects unloaded from Redshift). The "first" script in this process is `redshift_to_s3.py`, and the "second" script is `s3_to_sfts.py`. A example below demonstrates the sequential use of the scripts to perform the overall service ([skip to Usage Example section](#usage-example)).

### `redshift_to_s3.py`

The Redshift to S3 microservice requires:

 - a `json` configuration file passed as a second command line argument to run.

 - a `dml` SQL formatted query file to perform inside a nesting `UNLOAD` command.

- The following environment variables must be set:

  - `$pguser`

    the user with query access to the Redshift database.

  - `$pgpass`

    the password for the `$pguser`.

The configuration file format is described in more detail below. Usage is like:

```
python redshift_to_s3.py -c config.d/config.json
```

### `s3_to_sfts.py`

The S3 to SFTS microservice requires:

 - A Java runtime environment that can be invoked with the command line `java`

 - a `json` configuration file passed as a second command line argument to run.

 - The following environment variables must be set:

  - `$xfer_path`

    the path to the folder containing the MOVEit XFer Client Tools. The XFer Client Tools can be downloaded from the link labelled "Client Tools Zip (EZ, Freely, Xfer)" at  https://community.ipswitch.com/s/article/Direct-Download-Links-for-Transfer-and-Automation-2018).

    For example:
    ```
    export xfer_path=/path/to/xfer/jar/files/
    ```
    the folder _must_ contain `jna.jar` and `xfer.jar`

  - `$sfts_user`

    the service account user configured for access to the Secure File Transfer system, and with write access to SFTS path defined by the value for `sfts_path` in the json configuration file.

    ```
    export sfts_user=username  ## do not include an IDIR/ prefix in the username
    ```

  - `$sfts_pass`

    the password associated with the `$sfts_user` service account.

The configuration file format is described in more detail below. Usage is like:

```
python s3_to_sfts.py -c config.d/config.json
```

## Configuration

### Environment Variables

The S3 to Redshift microservice requires the following environment variables be set to run correctly.

- `sfts_user`: the SFTS username used with `sfts_pass` to access the SFTS database;
- `sfts_pass`: the SFTS password used with `sfts_user` to access the SFTS database;
- `AWS_ACCESS_KEY_ID`: the AWS access key for the account authorized to perform COPY commands from S3 to Redshift; and,
- `AWS_SECRET_ACCESS_KEY`: the AWS secret access key for the account authorized to perform COPY commands from S3 to Redshift.

### Configuration File

Store configuration files in in [config.d/](./config.d/).

A single well formed configuration file is sufficient to pass all required values to either script (`redshift_to_s3` and `s3_to_sfts`). While some parameters are used exclusively by one script or the other, enough parameters are shared between both scripts that a single configuration file is recommended. This will reduce the likelihood of input errors, reduce maintenance burden, and encapsulates into a single configuration the overall function for which these two scripts executed in sequence were originally intended for.

The JSON configuration is required as a second argument when running the `s3_to_redshift.py` script.

The structure of the config file should resemble the following:

```
{
  "bucket": String,
  "source": String,
  "directory": String,
  "destination": String,
  "object_prefix": String,
  "dml": String,
  "header": Boolean,
  "sfts_path": String,
  "extension": String
}
```

The keys in the config file are defined as follows. All parameters are required in order to use one configuration file for both scripts (which is recommended for service encapsulation and ease of maintenance):

- `"bucket"`: the label defining the S3 bucket that the microservice will reference.
- `"source"`: the first prefix of source objects, as in: `"s3://<bucket>/<source>/.../<object>"`.
- `"directory"`: the last path prefix before the object itself: `"s3://<bucket>/<source>/<directory>/<object>"` or `"s3://<bucket>/<destination>/<good|bad|batch>/<source>/<directory>/<object>"`
- `"destination"`: the first prefix of processed objects, as in `"s3://<bucket>/<destination>/<good|bad|batch>"`.
- `"object_prefix"`: The final prefix of the object; treat this as a prefix on the filename itself.
- `"dml"`: The filename under the [`./dml`](./dml/) directory in this repository that contains the SQL statement to run as an UNLOAD command.
- `"header"`: Setting this to true will write a first row of column header values; setting as false will omit that row.
- `"sfts_path"`: The folder path in SFTS where the objects retrieved from S3 will be uploaded to.
- `"extension"`: A postfix to the file name. As an extension, it must include the "`.`" character before the extension type, such as: `".csv"`. If no extension is needed then the value should be an empty string, like `""`.

### DML File

Store these in [dml/](./dml/).

This is simply a Redshift `UNLOAD` compatible query. The Redshift documentation for `UNLOAD` specifies how the `'select-statement'` must appear.

Note that there are some particular issues that are likely to cause problems:
- you may not use single quotes; since `UNLOAD` itself wraps the select-statement with single quotes. If you require single quotes in your statement, use a pair of single quotes instead
- The `SELECT` query can't use a `LIMIT` clause in the outer `SELECT`. Instead, use a nested `LIMIT` clause.

For more information see the Amazon Redshift documentation for UNLOAD: https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html

## Usage example
This example supposes that a client desires an "Example" service to transfer content from Redshift to SFTS as a comma delimited file.

The configuration file for this example service is created as: [`config.d/example.json`](./config.d/example.json); and the DML file that stores the SQL statement selecting the data they wish to copy from Redshift is created as: [`dml/example.sql`](./dml/example.sql).

The example service may be run once as follows:

```
## step 1
$ python redshift_to_s3.py -c config.d/example.json

## step 2
$ python s3_to_sfts.py -c config.d/example.json
```

The first step created an object in S3 which stores delimited content emitted from Redshift, based on the results of the configured `"dml"` value: [`"example.sql"`](./dml/example.json).

The second step transferred that file (and any other files matching the configured `"object_prefix"` value if they had not already been transferred) from S3 to the BC Government SFTS endpoint. The second script may also modify the filename before transfer by appending the value of the configured `"extension"` parameter.

## Project Status

As new projects require loading modeled data into SFTS, new configuration files will be prepared to support the consumption of those data sources.

This project is ongoing.

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
