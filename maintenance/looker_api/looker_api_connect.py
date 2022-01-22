import looker_sdk 
import os
import json
import time
import sys
query = int(sys.argv[1])

sdk = looker_sdk.init40("config/looker.ini")

response = sdk.run_query(
    query_id=query,
    result_format="json_detail",
    cache=False,
    cache_only=False)

# Convert string to Python dict 
query_dic = json.loads(response) 

    
print("Looker runtime =", query_dic['runtime']) 
print("Cache =", query_dic['from_cache']) 