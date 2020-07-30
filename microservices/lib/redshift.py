"""GDX Analytics Redshift class forms part of the shared module
"""
import os
import sys
import logging
import psycopg2

# Default RedShift host and port values for GDX Analytics
HOST = 'redshift.analytics.gov.bc.ca'
PORT = 5439

class RedShift:
    'Common microservice operations for RedShift'

    def print_psycopg2_exception(self, err):
        'handles and parses psycopg2 exceptions'
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno

        # print the connect() error
        self.logger.error("psycopg2 ERROR: %s", err)
        self.logger.debug("pgerror: %s", err.pgerror)
        self.logger.debug("pgcode: %s", err.pgcode)
        self.logger.debug("psycopg2 error on line number: %s", line_num)
        self.logger.debug("psycopg2 traceback: %s", traceback)
        self.logger.debug("psycopg2 error type: %s", err_type)

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

        connection_string_log = (
            "dbname='%s' host='%s' port='%s' user='%s'" % 
            (self.dbname,self.host,self.port,self.user))

        try:
            conn = psycopg2.connect(dsn=connection_string)
            self.logger.debug(
                "opened connection on connection string\n%s",
                connection_string_log)
        except psycopg2.Error as err:
            self.print_psycopg2_exception(err)
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
                except psycopg2.Error as err:
                    self.logger.error(
                        "Loading %s to RedShift failed.", self.batchfile)
                    self.print_psycopg2_exception(err)
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
