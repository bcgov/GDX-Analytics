import looker_sdk 
import os
import json
import time
sdk = looker_sdk.init40("/Users/vveenu/Applications/looker_api/looker.ini")
toc = time.perf_counter()
response = sdk.run_query(
    query_id=742831,
    result_format="json_detail",)

tic = time.perf_counter()
print(f"Downloaded the tutorial in {tic - toc:0.4f} seconds")