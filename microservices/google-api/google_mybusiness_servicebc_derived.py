###################################################################
# Script Name   : google_mybusiness_servicebc_derived.py
#
# Description   : Implements a table called google_mybusiness_servicebc_derived
#               : joining google.locations and servicebc.office_info
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the pgpass user microservice
#
#               : export pgpass=<<DB_PASSWD>>
#
#
# Usage         : python google_mybusiness_servicebc_derived.py configfile.json
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

host = 'snowplow-ca-bc-gov-main-redshi-resredshiftcluster-13nmjtt8tcok7.\
c8s7belbz4fo.ca-central-1.redshift.amazonaws.com'

conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host=host,
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
ON gl.location_id = oi.google_location_id
ALTER TABLE google_mybusiness_servicebc_derived OWNER TO microservice;
GRANT SELECT ON google_mybusiness_servicebc_derived TO looker;
COMMIT;
'''

with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        except psycopg2.Error as e:
            logger.exception("Failed to execute query")
        else:
            logger.info("Executed query successfully")
