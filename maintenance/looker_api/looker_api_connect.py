import looker_sdk 
import os
import json
import time
import sys
query = int(sys.argv[1])

sdk = looker_sdk.init40("looker.ini")
before = time.perf_counter()
response = sdk.run_query(
    query_id=742831,
    result_format="json_detail",)

after = time.perf_counter()
print(f"Query was run in {after - before:0.4f} seconds")
print(query)