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
import psycopg2
import logging

# Logging has two handlers: INFO to stdout and DEBUG to a file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
handler = logging.FileHandler(os.path.join('logs', log_filename),
                              "a", encoding=None, delay="true")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bc.ca',
           port='5439',
           user=os.environ['pguser'],
           password=os.environ['pgpass'])

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
ON gl.location_id = oi.google_location_id;
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
        else:
            logger.info((
                'Success: executed the transaction '
                'to prepare the google_mybusiness_servicebc_derived PDT'))
