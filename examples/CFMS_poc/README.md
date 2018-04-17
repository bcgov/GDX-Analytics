## GDX Analytics CFMS Instrumentation Proof of Concept 

This code is a proof of concept of Java code required to add Snowplow instrumentation to the CFMS application. For more information on the Snowplow Java Tracker see https://github.com/snowplow/snowplow-java-tracker.

## Project Status

Currently this project is still in development.

## To Build and Run

```
$ gradle build
$ java -jar build/libs/CFMS_poc-all-0.5.jar
```

## To download all dependencies to the "runtime" directory

```
$ gradel getDeps
```

## Special files in this repository
The files in [schemas/ca.bc.gov.cfmspoc](schemas/ca.bc.gov.cfmspoc) are the Snowplow schema files. See https://github.com/snowplow/iglu for more info.

## Getting Help

Please Contact dan.pollock@gov.b.ca for questions related to this work. 

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

