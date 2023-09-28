# Looker Dashboard Backup Script

These scripts are designed to perform a nightly backup of Looker dashboards from specific spaces in our Looker instance and push the data to a Git repository. They can be scheduled to run as a cron job.

## Prerequisites

Before using this script, make sure you have the following:

1. Access to looker_dev and looker_prod instances via terminal
2. Environment Varible GZR_PATH set in your bashrc file like this 
    `export GZR_PATH="/home/looker/bin/gzr"`
3. The `gzr` command-line tool installed, which is used to interact with Looker via the Looker API.
4. Properly configured `.netrc` file containing your Looker credentials.

All of the above prerequisites are already satisfied in looker_dev instance

## Usage for git_looker_dev_backup_script.sh

1. Login to looker_dev
2. Go to home/looker/scripts directory
3. Run `./git_looker_dev_backup_script.sh`
4. Check `dev-backup branch` of this Github Directory https://github.com/bcgov/GDX-Analytics-Gazer-Looker-Dev-Integration to verify the backup

## Modification to git_looker_dev_backup_script.sh
If there is a new folder in looker dev that we want to backup then script should be edited to add that space_id. Space id of folder can be taken from the URL such as Space_id for this folder https://dev.analytics.gov.bc.ca/folders/32 is `32`