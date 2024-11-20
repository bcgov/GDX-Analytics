## vue_js_tracker

This is an example Vue.js application to demonstrate how to install the the GDX_Analytics Snowplow Standalone Tracker vE.2.14.0 in the Vue.js framework.

## Features

This app contains the Snowplow Tracker Standalone vE.2.14.0, which is installed in the header
section of index.html. It also leverages the Vue Router Add-on by calling the Snowplow 'trackPageView' function, whenever the Vue Router changes the navigation.

## Project Status 

This project is currently under development and actively supported by the GDX Analytics Team.

## Requirements

This project is built using Vue.js 3, utilizing Vue CLI Service, along with Vue Router for client-side routing. It is compatible with Node.js version 16 or higher.

## To run this application

From the root of the application, run the following commands to install dependencies and serve the application using the vue-cli-service. This will serve the application from localhost.

### Install the project dependencies in the node_modules folder

This command respects versioning saved in package-lock.json when installing project dependencies. 

```
npm ci
```

### Compiles and hot-reloads for development

```
npm run serve
```
executes the serve script defined in package.json

```JSON
"scripts": {
  "serve": "vue-cli-service serve"
}
```
and starts the development server using Vue CLI Service, accessible at http://localhost:8080/ 

See the official Vue CLI Service documentation here: https://cli.vuejs.org/guide/cli-service.html

## Getting Help or Reporting an Issue
 
For inquiries about starting a new analytics account please contact the GDX Analytics Team.

## How to Contribute
 
If you would like to contribute to the guide, please see our [CONTRIBUTING](CONTRIBUTING.md) guideleines.
 
Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
 
## License
```
Copyright 2015 Province of British Columbia
 
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 
   http://www.apache.org/licenses/LICENSE-2.0
 
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
```
