#!/bin/bash

###########################################################
# Description: Simplifies git workflow on remote machines #
#                                                         #
# Usage: ./workflow.sh -opt                               #
#                                                         #
# Options: -b or -branch to clone a branch                #
#          -c or -clean to delete a branch                #
###########################################################

BRANCH_PATH="$HOME/branch/"
REPO="https://github.com/bcgov/GDX-Analytics-microservice.git"

while getopts ":b(branch) :c(clean)" opt; do
  case $opt in
    b)
      read -p "Enter the branch label: " branch
      git ls-remote --heads ${REPO} ${branch} | grep ${branch} >/dev/null
      if [ "$?" == "1" ] # Check exit code of git ls-remote
      then
              echo ""$branch" doesn't exist in "$REPO""
              exit
      fi
      read -p "Enter your first and last name: " username
      read -p "Enter your email to associate commits to: " email
      git clone --single-branch --branch $branch https://github.com/bcgov/GDX-Analytics-microservice.git $branch
      cd $branch
      # Set git config
      git config user.name "${username}"
      git config user.email "${email}"
      exit 1
      ;;
    c)
      read -r -p "Enter branch name to delete: " rmbranch
      rmpath="$BRANCH_PATH$rmbranch"
      read -r -p "Are you sure you want to permanently delete branch folder $rmpath? [y/N] " rmresponse
      if [[ "$rmresponse" =~ ^([nN][oO]|[nN])$ ]]
      then
              printf "Exiting with no action\n"
              exit 1
      fi
      read -r -p "If you installed any pipenvs under $rmpath those will be removed by this cleanup task. Do you wish to continue? [y/N] " pipresponse
      if [[ "$rmresponse" =~ ^([yY][eE][sS]|[yY])$ ]] && [[ "$pipresponse" =~ ^([yY][eE][sS]|[yY])$ ]] && [[ -d "$rmpath" ]]
      then
              printf "Deleting $rmpath ...\n"
              rm -rf $rmpath
              printf "Removing Virtual Environments...\n"
              for f in $(find ~/.local/share/virtualenvs/*/.project -type f); do proj_path="$(cat $f)" && [ ! -d $proj_path ]
              done

      elif [[ "$pipresponse" =~ ^([nN][oO]|[nN])$ ]]
      then
              printf "Exiting with no action\n"
      else
              printf "The branch you entered does not exist\n"
      fi
      exit 1
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      echo "-b to clone a branch"
      echo "-c to cleanup a branch"
      exit 1
      ;;
  esac
done
# Check if no option was passed
if (( $OPTIND == 1 ))
then
        echo "This script requires an argument." >&2
        echo "-b to clone a branch"
        echo "-c to cleanup a branch"
fi
