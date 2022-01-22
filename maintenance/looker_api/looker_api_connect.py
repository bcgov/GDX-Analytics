import looker_sdk 
import os
import json
import time
import sys
import csv
query = int(sys.argv[1])
times = int(sys.argv[2])

sdk = looker_sdk.init40("config/looker.ini")

QueryList = []


# run query as per user input

i = 1
while i <= times:
    response = sdk.run_query(
    query_id=query,
    result_format="json_detail",
    cache=False,
    cache_only=False)
    # Convert string to Python dict 
    query_dic = json.loads(response) 
    Runtime_to_add = round(float(query_dic['runtime']), 2)
    QueryList.append(Runtime_to_add)
    i += 1
    
    
print("Querylist", QueryList)
minimum = min(QueryList)
print("Min", minimum)
maximum = max(QueryList)
print("Max", maximum)
sum = sum(QueryList)
length = len(QueryList)
average = round(sum/length, 2)
print("Avg", average)





    
