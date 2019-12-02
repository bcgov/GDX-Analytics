# Secure File Transfer System microservice

This folder contains scripts, configuration files (within the [config.d](./config.d/) folder), and SQL formatted DML files (within the [dml](./dml/) folder) that enable the the Secure File Transfer System (SFTS) microservice implemented on the GDX-Analytics platform.


## Overview

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

Store these in [config.d/](./config.d/).

Overlap of the variables used in both `redshift_to_s3.py` and `s3_to_sfts.py` means a single configuration file can support both scripts. Furthermore, a single configuration file is recommended to reduce introducing the possibility for errors.

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
  "sfts_path": String
}
```

The keys in the config file are defined as:

- `"bucket"`: the label defining the S3 bucket that the microservice will reference.
- `"source"`: the first prefix of source objects, as in: `s3://<bucket>/<source>/.../<object>`.
- `"directory"`: the last path prefix before the object itself: `s3://<bucket>/<source>/<directory>/<object>` or `s3://<bucket>/<destination>/<good|bad|batch>/<source>/<directory>/<object>`
- `"destination"`: the first prefix of processed objects, as in `s3://<bucket>/<destination>/<good|bad|batch>`.
- `"object_prefix"`: The final prefix of the object; treat this as a prefix on the filename itself.
- `"dml"`: The filename under the `./dml`(./dml/) directory in this repository that contains the SQL statement to run as an UNLOAD command.
- `"sfts_path"`: The folder path in SFTS where the objects retrieved from S3 will be uploaded to.

### DML File

Store these in [dml/](./dml/).

This is simply a Redshift `UNLOAD` compatible query. The Redshift documentation for `UNLOAD` specifies how the `'select-statement'` must appear.

Note that there are some particular issues that are likely to cause problems:
- you may not use single quotes; since `UNLOAD` itself wraps the select-statement with single quotes. If you require single quotes in your statement, use a pair of single quotes instead
- The `SELECT` query can't use a `LIMIT` clause in the outer `SELECT`. Instead, use a nested `LIMIT` clause.

For more information see the Amazon Redshift documentation for UNLOAD: https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html

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
