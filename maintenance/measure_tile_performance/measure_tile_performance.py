import os
import psycopg2
import statistics
import looker_sdk
import json
import datetime
import csv
import argparse
import time
import pytz
from pytz import timezone
from datetime import datetime


NAME = 'snowplow'
HOST = 'redshift.analytics.gov.bc.ca'
PORT = 5439
user = os.environ['lookeruser_rs']
passwd = os.environ['lookerpass_rs']
connection_string = (
    f"dbname='{NAME}' "
    f"host='{HOST}' "
    f"port='{PORT}' "
    f"user='{user}' "
    f"password={passwd}")

# connects with redshift database using environment variables
# set redshift cache to 'off' before running any looker API calls
# run the API calls
# set redshift cache back to 'on' after the queries are processed.
# close the redshift connection

def cache_off():
 # set redshift cache to 'off'
    conn = psycopg2.connect(dsn=connection_string)
    with conn:
         with conn.cursor() as curs:
            try:
                curs.execute("ALTER USER looker SET enable_result_cache_for_session TO off;")
                print('redshift cache is off and connection is closed')
            except Exception as err:
                print(f'Exiting due to psycopg2 execution error: {err}')
                print('redshift cache is on and connection is closed')
                exit(1)



def cache_on():
 # set redshift cache back to 'on'
    conn = psycopg2.connect(dsn=connection_string)
    with conn:
        with conn.cursor() as curs:
            try:
                curs.execute("ALTER USER looker SET enable_result_cache_for_session TO on;")
                print('redshift cache is on and connection is closed')
            except Exception as err:
                print(f'URGENT! Exiting due to psycopg2 execution error: {err}')
                print('Requires manual run of: ALTER USER looker SET enable_result_cache_for_session TO on;')
                print('redshift cache is on and connection is closed')
                exit(1)
              



def main():
    
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
        sleep_timer = 0

    if times > 100 or times <= 0:
        print("Runs per query(arg2) must be between 1 and 100")
        exit()

    # looks for environment variables for authentication
    sdk = looker_sdk.init40()

    query_list = []
    header = ['SlugId', 'Timestamp', 'RunTime']

    # datetime object containing current date and time
    now = datetime.now()
    
    # dd/mm/YY H:M:S
    filename = slug_input + now.strftime("_%Y%m%dT%H%M%S") + '.csv'

    # get query_id from slug
    try:
        slug_response = sdk.query_for_slug(slug=slug_input)
    except Exception as err:
        print(f'Exiting due to Looker SDK exception: {err}')
        exit(1)    

    query = slug_response.id

    if args.file:
        with open(filename, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            # write the header
            writer.writerow(header)

    # set redshift cache to 'off' before running any looker API calls
    cache_off()

    # run query as per user input
    i = 1
    while i <= times :

        try:
            response = sdk.run_query(
            query_id=query,
            result_format="json_detail",
            cache=False,
            cache_only=False)
        except Exception as err:
            print(f'Exiting due to Looker SDK exception: {err}')
            cache_on()
            exit(1)


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
        
        # adding time delay between subsequent queries to keep looker open for other tasks
        if i != times and args.sleepTimer:
            time.sleep(sleep_timer)

        i += 1

    # print the filename on console
    if args.file:
        print("Filename =", filename)
        f.close()
        
    #Print for Console 
    print("RunTimes =", query_list)
    minimum = min(query_list)
    print("Min =", minimum)
    maximum = max(query_list)
    print("Max =", maximum)
    sum_of_list = sum(query_list)
    length = len(query_list)
    average = round(sum_of_list/length, 2)
    print("Avg =", average)
    #if query runs are more than 1, then calculate standard deviation
    if times > 1:
        standard_dev = round(statistics.stdev(query_list), 2)
        print("Standard Deviation =", standard_dev)

    # set redshift cache back to 'on' after the queries are processed.
    cache_on()

if __name__ == '__main__':
  main()
  
