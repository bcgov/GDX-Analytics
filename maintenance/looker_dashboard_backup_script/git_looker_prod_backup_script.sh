#!/bin/bash

cd /home/looker/GDX-Analytics-Gazer-Looker-Prod-Integration
SPACE_IDS="1"
# Define the path to the gzr executable using the environment variable
GZR_EXECUTABLE="$GZR_PATH"
# Loop through space IDs and run the gzr space export command for each
for SPACE_ID in $SPACE_IDS; do
  "$GZR_EXECUTABLE" space export "$SPACE_ID" --no-verify-ssl --host=analytics.gov.bc.ca
done
# Commit all changes with a customized message
git add .
git commit -m "Backup Looker data at $(date +"%Y-%m-%d %H:%M:%S")"

# Push changes to the prod-backup branch (verify that the branch exists)
git push origin prod-backup