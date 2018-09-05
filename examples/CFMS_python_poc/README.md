## GDX Analytics Python Example

This code is a proof of concept of Python code required to add Snowplow instrumentation using the initial CFMS proof of concept model. For more information on the Snowplow Python Tracker see https://github.com/snowplow/snowplow-python-tracker.

## Project Status

Currently this project is still in development.

## To install the Snowplow Python library

```
$ sudo pip install snowplow-tracker
```

## To Run

```
$ python sn.py
```

## Special files in this repository
The files in [schemas/ca.bc.gov.cfmspoc](../schemas/ca.bc.gov.cfmspoc) are the Snowplow schema files. See https://github.com/snowplow/iglu for more info.

## If you encounter an SSL certificate error
When connecting to Snowplow signed by a BC Government SSL certificate you may encounter this Python error:
```
WARNING:snowplow_tracker.emitters:[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)
```
This occurs on some systems where your Python environment is missing the root certificate used to sign our SSL certificate. It appears that the Certificate Authority (CA) for Entrust is missing. 

You can test this on the main HTTPS certificate using an interactive Python session by running: 
```
>>> import requests
>>> requests.get('https://www2.gov.bc.ca')
```

To work around this issue, download the CA from https://www.entrustdatacard.com/pages/root-certificates-download. 
Look for the "Entrust Root Certificate Authority—G2" and dowload the certificate from https://entrust.com/root-certificates/entrust_g2_ca.cer. 

To ensure that Python loads this CA, can set this environment variable:
```
# export REQUESTS_CA_BUNDLE=/path/to/entrust_g2_ca.cer
```

## Getting Help

Please Contact dan.pollock@gov.bc.ca for questions related to this work. 

## Contributors

The GDX analytics team will be the main contributors to this project currently. They will also maintain the code as well. 

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

