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
            f"bname='{self.dbname}' "
            f"host='{self.host}' "
            f"port='{self.port}' "
            f"user='{self.user}' "
            f"password={self.password}")

        return psycopg2.connect(dsn=connection_string)

    def close_connection(self):
        'closes the connection'
        self.connection.close()

    def query(self, query):
        'Performs a query'
        with self.connection as conn:
            with conn.cursor() as curs:
                try:
                    curs.execute(query)
                except psycopg2.Error:
                    logging.exception()
                    return False
                else:
                    logging.debug(f"This query was excecuted without error:"
                                  f"{query}")
                    return True

    def __init__(self, name=None, user=None, password=None):
        'The constructor opens a RedShift connection based on the arguments'
        self.dbname = name
        self.host = HOST
        self.port = PORT
        self.user = user
        self.password = password

        self.connection = self.open_connection()

    @classmethod
    def snowplow(cls):
        'A factory constructor for the GDX Analytics Snowplow database'
        return cls('snowplow', os.environ['pguser'], os.environ['pgpass'])
