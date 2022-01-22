import looker_sdk 
import os
import json
import time
import sys
query = int(sys.argv[1])

sdk = looker_sdk.init40("looker.ini")
before = time.perf_counter()
response = sdk.run_query(
    query_id=query,
    result_format="json_detail",
    cache=false,
    cache_only=false)

after = time.perf_counter()
print(f"Query was run in {after - before:0.4f} seconds")
# Convert string to Python dict 
query_dic = json.loads(response) 

    
print(query_dic['runtime']) 
print(query_dic['from_cache']) 