import looker_sdk 
import json
import datetime
import csv
import argparse
import time
import pytz
from pytz import timezone
import os



parser = argparse.ArgumentParser()
# Positional mandatory arguments
parser.add_argument("slugInput", help="Slug id from explore.")
parser.add_argument("times", help="Number of times script is run - Value must be between 1 and 100", type=int)
# optional arguments
parser.add_argument("sleepTimer", help="Number of seconds delay between each query, defaluted to 300s ", nargs='?', type=int)
parser.add_argument("-f", "--file", help="Boolean to create a file", action='store_true')

args = parser.parse_args()


slug_input = args.slugInput
times = args.times

if args.sleepTimer:
    sleep_timer = args.sleepTimer
else:
    sleep_timer = 300

if times > 100 or times <= 0:
    print("Runs per query(arg2) must be between 1 and 100")
    exit()

# looks for looker.ini file in your home directory
sdk = looker_sdk.init40(os.path.expanduser('~')+"/looker.ini")

query_list = []
header = ['SlugId', 'Timestamp', 'RunTime']

from datetime import datetime
# datetime object containing current date and time
now = datetime.now()
 
# dd/mm/YY H:M:S
filename = slug_input + now.strftime("_%Y%m%dT%H%M%S") + '.csv'

# get query_id from slug
slug_response = sdk.query_for_slug(slug=slug_input)

query = slug_response.id

if args.file:
    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)

# run query as per user input

i = 1
while i <= times :
    response = sdk.run_query(
    query_id=query,
    result_format="json_detail",
    cache=False,
    cache_only=False)
    # Convert string to Python dict 
    query_dic = json.loads(response) 
    runtime_duration = round(float(query_dic['runtime']), 2)
    ran_at_utc = pytz.utc.localize(datetime.fromisoformat(query_dic['ran_at'][:-1]))
    ran_at = ran_at_utc.astimezone(pytz.timezone('America/Vancouver')).isoformat()
    query_list.append(runtime_duration)
    if args.file:
        with open(filename, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            # write the data
            writer.writerow([slug_input, ran_at, runtime_duration])
    
    # adding 5 min time delay between subsequent queries to keep looker open for other tasks
    if i != times:
        time.sleep(sleep_timer)

    i += 1

if args.file:
    print("Filename =", filename)
    f.close()
    
#Print for Console 

print("RunTimes =", query_list)
minimum = min(query_list)
print("Min =", minimum)
maximum = max(query_list)
print("Max =", maximum)
sum = sum(query_list)
length = len(query_list)
average = round(sum/length, 2)
print("Avg =", average)

    
