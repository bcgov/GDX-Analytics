import looker_sdk 
import json
import datetime
import csv
import argparse

parser = argparse.ArgumentParser()
# Positional mandatory arguments
parser.add_argument("slugInput", help="Slug id from explore.")
parser.add_argument("times", help="Number of times script is run - Value must be between 1 and 100", type=int)
# optional argument
parser.add_argument("-f", "--file", help="Boolean to create a file", action='store_true')
args = parser.parse_args()


slug_input = args.slugInput
times = args.times

if times > 100 or times <= 0:
    print("Runs per query(arg2) must be between 1 and 100")
    exit()


sdk = looker_sdk.init40("config/looker.ini")

QueryList = []
header = ['SlugId', 'Timestamp', 'RunTime']

from datetime import datetime
# datetime object containing current date and time
now = datetime.now()
 
# dd/mm/YY H:M:S
filename = slug_input + now.strftime("-%d-%m-%Y-%H-%M-%S") + '.csv'

# get query_id from slug
SlugResponse = sdk.query_for_slug(slug=slug_input)

query = SlugResponse.id

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
    Runtime_duration = round(float(query_dic['runtime']), 2)
    Ran_at = query_dic['ran_at']
    QueryList.append(Runtime_duration)
    if args.file:
        with open(filename, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            # write the data
            writer.writerow([slug_input, Ran_at, Runtime_duration])
    i += 1
if args.file:
    print("Filename =", filename)
    f.close()
    
#Print for Console 

print("RunTimes =", QueryList)
minimum = min(QueryList)
print("Min =", minimum)
maximum = max(QueryList)
print("Max =", maximum)
sum = sum(QueryList)
length = len(QueryList)
average = round(sum/length, 2)
print("Avg =", average)

    
