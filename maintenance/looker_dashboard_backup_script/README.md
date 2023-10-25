# Looker Dashboard Backup Script

These scripts are designed to perform a backup of Looker dashboards from all spaces under shared frolder in our Looker instances and push the data to a Git repository. They are currently scheduled to run as a nightly cron job in both dev and prod instances.

## Prerequisites

Before using this script, make sure you have the following:

1. Access to looker_dev and looker_prod instances via terminal
2. Environment Variable GZR_PATH set in your bashrc file like this 
    `export GZR_PATH="/home/looker/bin/gzr"`
3. The `gzr` command-line tool installed, which is used to interact with Looker via the Looker API.
4. Properly configured `.netrc` file containing your Looker credentials.

All of the above prerequisites are already satisfied in looker_dev instance

## Usage for git_looker_dev_backup_script.sh

1. Login to looker_dev
2. Go to home/looker/scripts directory
3. Run `./git_looker_dev_backup_script.sh`
4. Check `dev-backup branch` of this Github Directory https://github.com/bcgov/GDX-Analytics-Gazer-Looker-Dev-Integration to verify the backup

## Usage for git_looker_prod_backup_script.sh

1. Login to looker_prod
2. Go to home/looker/scripts directory
3. Run `./git_looker_prod_backup_script.sh`
4. Check `prod-backup branch` of this Github Directory https://github.com/bcgov/GDX-Analytics-Gazer-Looker-Prod-Integration to verify the backup

## Further reading
1. Further reading can be done about backup and resore process at our confluence page - https://apps.itsm.gov.bc.ca/confluence/display/ANALYTICS/Looker+Dashboards+Backup+and+Restore+Process
2. More details about gazer tool can be found here https://github.com/looker-open-source/gzr  