# Secure File Transfer System microservice

This folder contains scripts, configuration files (within the [config.d](./config.d/) folder), and SQL formatted DML files (within the [dml](./dml/) folder) that enable the the Secure File Transfer System (SFTS) microservice implemented on the GDX-Analytics platform.

## `redshift_to_s3.py`

The Redshift to S3 microservice requires:
 - a `json` configuration file passed as a second command line argument to run.
 - a `dml` SQL formatted query file to perform inside a nesting `UNLOAD` command.

The configuration file format is described in more detail below. Usage is like:

```
python redshift_to_s3.py config.json
```

## `s3_to_sfts.py`

The S3 to SFTS microservice requires:
 - a `json` configuration file passed as a second command line argument to run.
 - that the MOVEit XFer Client Tools exists in: `/home/microservice/MOVEit-Xfer/` and contains:
  - `jna.jar`
  - `xfer.jar`
  - `xfer.sh`

The configuration file format is described in more detail below. Usage is like:

```
python s3_to_sfts.py config.json
```

### Overview


### Configuration

#### Environment Variables

The S3 to Redshift microservice requires the following environment variables be set to run correctly.

- `sfts_user`: the SFTS username used with `sfts_pass` to access the SFTS database;
- `sfts_pass`: the SFTS password used with `sfts_user` to access the SFTS database;
- `AWS_ACCESS_KEY_ID`: the AWS access key for the account authorized to perform COPY commands from S3 to Redshift; and,
- `AWS_SECRET_ACCESS_KEY`: the AWS secret access key for the account authorized to perform COPY commands from S3 to Redshift.

#### Configuration File

Overlap of the variables used in both `redshift_to_s3.py` and `s3_to_sfts.py` means a single configuration file can support both scripts. Furthermore, a single configuration file is recommended to reduce introducing the possibility for errors.

The JSON configuration is required as a second argument when running the `s3_to_redshift.py` script.

The structure of the config file should resemble the following:

```
{
  "bucket": String,
  "directory": String,
  "source": String,
  "destination": String,
  "dbtable": String,
  "dml": String,
  "sfts_path": String
}
```

The keys in the config file are defined as:

- `"bucket"`: the label defining the S3 bucket that the microservice will reference.
- `"source"`: the top level S3 prefix for source objects after the bucket label, as in: `<bucket>/<source>/<client>/<doc>`.
- `"destination"`: the top level S3 prefix for processed objects to be stored, as in: `<bucket>/<destination>/<client>/<doc>`.
- `"directory"`: the S3 prefix to follow source or destination and before the `<doc>` objects.
- `"dbtable"`: The table to `COPY` the processed data into _with the schema_, as in: `<schema>.<table>`.
- `"dml"`: The filename under the `./dml`(./dml/) directory containing the SQL statement to run as an UNLOAD command.
- `"sfts_path"`: The folder path in SFTS where the objects retrieved from S3 will be uploaded to.

## Project Status

As new projects require loading modeled data into SFTS, new configuration files will be prepared to support the consumption of those data sources.

This project is ongoing.

## Getting Help

Please Contact the GDX Service desk for any analytics service help. For inquiries about automating generated file exchange with GDX-Analytics over the BCGov SFTS service, or for general inquiries about starting a new analytics account for Government, please contact The GDX Analytics team.

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
