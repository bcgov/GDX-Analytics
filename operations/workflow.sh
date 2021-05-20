#!/bin/bash
  
BRANCH_PATH="$HOME/branch/"

while getopts ":b :c" opt; do
  case $opt in
    b)
      read -p "Enter the branch label: " branch
      read -p "Enter your GitHub Name (First name Last name): " username
      read -p "Enter your email to associate commits to: " email
      git clone --single-branch --branch $branch https://github.com/bcgov/GDX-Analytics-microservice.git $branch
      cd $branch
      git config user.name "${username}"
      git config user.email "${email}"
      ;;
    c)
      read -r -p "Enter branch name to delete: " rmbranch
      read -r -p "Are you sure you want to permanently delete branch folder $BRANCH_PATH$rmbranch? [y/N] " rmresponse
      read -r -p "Have you removed any installed virtualenvs, or were none created? [y/N] " pipresponse
      if [[ "$rmresponse" =~ ^([yY][eE][sS]|[yY])$ ]] && [[ "$pipresponse" =~ ^([yY][eE][sS]|[yY])$ ]]
      then
              rmpath="$BRANCH_PATH$rmbranch"
              printf "Deleting $rmpath ...\n"
              rm -rf $rmpath

      elif [[ "$pipresponse" =~ ^([nN][oO]|[nN])$ ]]
      then
              printf "Please remove your pipenv before deleting branch folder\n"
      else
              printf "Exiting....\n"
      fi
      exit 1
      ;;
    \?)
      echo "Invalid option: -$OPTARG try again..." >&2
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done
