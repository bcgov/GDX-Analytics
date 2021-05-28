#!/bin/bash

BRANCH_PATH="$HOME/branch/"
REPO="https://github.com/bcgov/GDX-Analytics-microservice.git"

while getopts ":b(branch) :c(clean)" opt; do
  case $opt in
    b)
      read -p "Enter the branch label: " branch
      git ls-remote --heads ${REPO} ${branch} | grep ${branch} >/dev/null
      if [ "$?" == "1" ]
      then
              echo ""$branch" doesn't exist in "$REPO""
              exit
      fi
      read -p "Enter your GitHub Name (First name Last name): " username
      read -p "Enter your email to associate commits to: " email
      git clone --single-branch --branch $branch https://github.com/bcgov/GDX-Analytics-microservice.git $branch
      cd $branch
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
      read -r -p "Have you removed any installed virtualenvs, or were none created? [y/N] " pipresponse
      if [[ "$rmresponse" =~ ^([yY][eE][sS]|[yY])$ ]] && [[ "$pipresponse" =~ ^([yY][eE][sS]|[yY])$ ]] && [[ -d "$rmpath" ]]
      then
              printf "Deleting $rmpath ...\n"
              rm -rf $rmpath

      elif [[ "$pipresponse" =~ ^([nN][oO]|[nN])$ ]]
      then
              printf "Please remove your pipenv before deleting branch folder\n"
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
    :)
      echo "Option -$OPTARG requires an argument." >&2
      echo "-b to clone a branch"
      echo "-c to cleanup a branch"
      ;;
  esac
done
