# Content Inventory 
The script content_mergescript.sh and asset_mergescript.sh in 
## Prerequisites
* Bash script environment
* permission to execute bash scripts in folder

## Setup
Download the appropriate script(s) to host machine
For Content Inventory

Download the associated Explore CSV and SQL Runner CSV file to host machine

## Usage

```
usage: content_mergescript_v1.sh EXPLORERCSV SQLCSV OUTPUTCSV

Generate Content Inventory CSV from the input files.

positional arguments:
    EXPLORERCSV     Explore Output for Page Views in CSV format 
    SQLCSV          SQL Runner Output for Page Metadata in CSV format
    OUTPUTCSV       merged content of Metadata and Page Views
  

```
If any required information is note supplied, you will be recieve an error message.
If EXPLORERCSV or SQLCSV do not exist then you will recieve an error message.
If OUTPUTCSV already exists then you will recieve an error message.

```
usage: asset_mergescript_v1.sh EXPLORERCSV SQLCSV OUTPUTCSV

Generate Asset Inventory CSV from the input files.

positional arguments:
    EXPLORERCSV     Explore Output for Asset Download in CSV format 
    SQLCSV          SQL Runner Output for Asset Metadata in CSV format
    OUTPUTCSV       merged content of Metadata and Page Views
  
```
Examples:

$ sh content_mergescript_v1.sh pages_explore_output1_ticket.csv pages_sql_output1_ticket.csv Pageviews_theme_year_month.csv

Combines the file pages_explore_output1_ticket.csv and file pages_sql_output1_ticket.csv to generate Pageviews_theme_year_month.csv
```
$ sh asset_mergescript_v1.sh asset_explore_output1_ticket.csv asset_sql_output1_ticket.csv AssetDownloads_theme_year_month.csv

Combines the file asset_explore_output1_ticket.csv and file asset_sql_output1_ticket.csv to generate AssetDownloads_theme_year_month.csv

## Getting Help

These scripts are intented for internal use. Please contact the GDX Analytics Team for more information.

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
