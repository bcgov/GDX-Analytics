## GDX Analytics Looker Embed Generator

These Java and Python examples demonstrate the generation of cryptographically signed SSO embed URL pointing to a dashboard or view exposed through the Looker embed user. The Looker Embed Secret key is required to generate these with the appropriate signature and nonce.

This includes two examples:
* [looker_embed_generator.java](looker_embed_generator.java) implements the example in Java
* [looker_embed_generator.py](looker_embed_generator.py) implements the example in Python27

## Project Status

Currently this project is still in development.

## To Run

These are command line applications. `LOOKERKEY` must be set for this session.

### Running the Java version

Requirements:
The Java embed generator code requires the GSON library module.
Download the GSON JAR file from: https://mvnrepository.com/artifact/com.google.code.gson/gson. 
Version 2.8.6 has been tested to work.

Parameters:
- `classpath` or `cp`: the file path to the GSON Library Jar file
- `env`: the target Looker environment, e.g.: `prod` or `test`
- `embed_url`: the target look or dashboard, e.g.: `looks/98`
- `-e`: set the flag for optional embed filter
- `embed filter jsons string`: a JSON string specifying the filter, e.g.: '{"filterName":"City","matchType":"=","matchValue":"Metropolis"}'
- `-u`: set the flag for optional user-attribute
- `attribute`: a User-Attribute to pass, e.g.: `browser`
- `filter`: a filter on the passed User-Attribute, e.g.: `Chrome`

The Java version accepts all optional attribute and filter parameters as follows:

```
java -cp <<filepath>> looker_embed_generator.java <<environment>> -e  '{"filter-name":"filtername-value","matchtype":"matchtype-value","values":"filter-value"}' -u <<embed_url>> [<<attribute>> <<filter>>]
```

### Running the Python version

Parameters:
- `embed_url`: the target look or dashboard, e.g.: `looks/98`
- `json_filter`: an optional dashboard filter by filter-names and filter-values as a JSON object of the form `'{"filter-name":"filter-value"}'`, e.g.: `'{"City":"Metropolis"}'`

The Python version will accept the `embed_url` as a required argument:
```
python looker_embed_generator.py <<embed url>>
```

The Python version can also be passed dashboard filter-names and filter-values using a JSON string:
```
python looker_embed_generator.py <<embed url>> <<json_filter>>
```

## Getting Help

Contact the GDX Analytics team for a valid LOOKERKEY value and usage help.

## Contributors

The GDX Analytics team will be the main contributors to this project currently. They will also maintain the code.

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
