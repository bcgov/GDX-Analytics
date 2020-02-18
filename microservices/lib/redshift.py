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
            self.logging.debug('opened connection')
        except:
            self.logging.exception('psycopg2 threw an exception')
        return conn

    def close_connection(self):
        'closes the connection'
        self.connection.close()
        self.logging.debug('closed connection')

    def query(self, query):
        'Performs a query'
        with self.connection as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except psycopg2.Error as e:
                    logging.error("Loading {0} to RedShift failed\n{1}"
                             .format(self.batchfile, e.pgerror))
                    return False
                else:
                    logging.info("Loaded {0} to RedShift successfully"
                                    .format(self.batchfile))
                    return True

    def __init__(self, batchfile, name=None, user=None, password=None):
        'The constructor opens a RedShift connection based on the arguments'

        self.batchfile = batchfile

        self.dbname = name
        self.host = HOST
        self.port = PORT
        self.user = user
        self.password = password

        self.connection = self.open_connection()

    @classmethod
    def snowplow(cls, batchfile):
        'A factory constructor for the GDX Analytics Snowplow database'
        return cls(batchfile, 'snowplow', os.environ['pguser'], os.environ['pgpass'])
