"""GDX Analytics Redshift class forms part of the shared module
"""
import os
import logging
import psycopg2

# Default RedShift host and port values for GDX Analytics
HOST = 'redshift.analytics.gov.bc.ca'
PORT = 5439

class RedShift:
    'Common microservice operations for RedShift'

    def open_connection(self):
        'opens a connection to the Redshift database using the provided'
        # The basic parameters for the data source name value parsed by psyopg2
        # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
        connection_string = (
            f"dbname='{self.dbname}' "
            f"host='{self.host}' "
            f"port='{self.port}' "
            f"user='{self.user}' "
            f"password={self.password}")

        try:
            conn = psycopg2.connect(dsn=connection_string)
            self.logger.debug(f'opened connection to {self.dbname}')
        except:
            self.logger.exception('psycopg2 threw an exception')
        return conn

    def close_connection(self):
        'closes the connection'
        self.connection.close()
        self.logger.debug('closed connection')

    def query(self, query):
        'Performs a query'
        with self.connection as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except psycopg2.Error as e:
                    self.logger.error(
                        "Loading %s to RedShift failed.", self.batchfile)
                    self.logger.error("%s", e.pgerror)
                    return False
                else:
                    self.logger.info(
                        "Loaded %s to RedShift successfully", self.batchfile)
                    return True

    def __init__(self, batchfile, name=None, user=None, password=None):
        'The constructor opens a RedShift connection based on the arguments'

        self.logger = logging.getLogger(__name__)

        self.batchfile = batchfile

        self.dbname = name
        self.host = HOST
        self.port = PORT
        self.user = user
        self.password = password

        self.connection = self.open_connection()
        self.logger.debug('connection to redshift initialized')


    @classmethod
    def snowplow(cls, batchfile):
        'A factory constructor for the GDX Analytics Snowplow database'
        return cls(
            batchfile, 'snowplow', os.environ['pguser'], os.environ['pgpass'])
