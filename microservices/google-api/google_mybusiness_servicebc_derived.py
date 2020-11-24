###################################################################
# Script Name   : google_mybusiness_servicebc_derived.py
#
# Description   : Creates google_mybusiness_servicebc_derived, which is a
#               : persistent derived table (PDT) joining google.locations
#               : with servicebc.office_info, and servicebc.datedimension
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the pgpass user microservice
#
#               : export pguser=<<database_username>>
#               : export pgpass=<<database_password>>
#
#
# Usage         : python google_mybusiness_servicebc_derived.py
#
import os
import sys
import logging
import psycopg2
import lib.logs as log

# Set up logging
logger = logging.getLogger(__name__)
log.setup()

# set up the Redshift connection
dbname = 'snowplow'
host = 'redshift.analytics.gov.bc.ca'
port = '5439'
user = os.environ['pguser']
password = os.environ['pgpass']
conn_string = (f"dbname='{dbname}' host='{host}' port='{port}' "
               f"user='{user}' password={password}")

query = '''
BEGIN;
SET SEARCH_PATH TO google;
DROP TABLE IF EXISTS google_mybusiness_servicebc_derived;
CREATE TABLE google_mybusiness_servicebc_derived AS
SELECT
  gl.*,
  oi.site AS office_site,
  oi.officesize AS office_size,
  oi.area AS area_number,
  oi.id AS office_id,
  oi.current_area as current_area,
  dd.isweekend::BOOLEAN,
  dd.isholiday::BOOLEAN,
  dd.lastdayofpsapayperiod::date,
  dd.fiscalyear,
  dd.fiscalmonth,
  dd.fiscalquarter,
  dd.sbcquarter,
  dd.day,
  dd.weekday,
  dd.weekdayname
FROM google.locations AS gl
JOIN servicebc.datedimension AS dd
ON gl.date::date = dd.datekey::date
LEFT JOIN servicebc.office_info AS oi
ON gl.location_id = oi.google_location_id AND end_date IS NULL;
ALTER TABLE google_mybusiness_servicebc_derived OWNER TO microservice;
GRANT SELECT ON google_mybusiness_servicebc_derived TO looker;
COMMIT;
'''

with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        except psycopg2.Error:
            logger.exception((
                'Error: failed to execute the transaction '
                'to prepare the google_mybusiness_servicebc_derived PDT'))
            sys.exit(1)
        else:
            logger.info((
                'Success: executed the transaction '
                'to prepare the google_mybusiness_servicebc_derived PDT'))
            sys.exit(0)
