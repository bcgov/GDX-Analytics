Script assumes that looker.ini and looker_api_connect.py are in the same directory.

Every user have their own client id and secret key. You can set them up in looker admin panel. Go to this URL https://analytics.gov.bc.ca/admin/users and click on Edit in front of your username and then click on Edit Keys under "Api3" section.
# API 3 client - Replace "Enter-here" with your client id 
client_id="Enter-here"
# API 3 Secret - Replace "Enter-here" with your client secret
client_secret="Enter-here"

Use this command to install dependencies.
# pipenv install
Use command to run the script where arg1 = query_id

# pipenv run python looker_api_connect.py arg1