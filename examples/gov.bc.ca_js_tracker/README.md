## GDX Analytics CMS Lite Dev Code

This code demonstrates the inline Javascript to track web analytics events for CMS Lite sites. The [`gov_sp_script.js`](./gov_sp_script.js) includes adding a custom context to include the Node Id. The [`gov_search_sp_script.js`](./gov_search_sp_script.js) search tracker includes a search event that will collect the search terms for gov. It only connects to Snowplow Mini and will need to be updated to the push data to the production Snowplow pipeline when development is complete.

## Project Status

Currently this project is in development.

## To Run

Add this script in the header section of the html page. Currently this script is connecting to the test instance of Snowplow (Snowplow Mini), when the development work is done the collector will have to be changed to the main pipeline.

## Getting Help

Please Contact ryan.janes@gov.bc.ca for questions related to this work. 

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

