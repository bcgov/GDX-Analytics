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
        self.logger.error("psycopg2 %s: %s", err.__class__.__name__, err)
        self.logger.debug("pgerror: %s", err.pgerror)
        self.logger.debug("pgcode: %s", err.pgcode)
        self.logger.debug("psycopg2 error on line number: %s", line_num)
        self.logger.debug("psycopg2 traceback: %s", traceback)
        self.logger.debug("psycopg2 error type: %s", err_type)

        '''
        XX000 is the code for an InternalError Exception in psycopg2.
        It is raised when the database encounters an error due to some
        operation that cannot be completed for some reason.
        
        In these microservices, this can occur when some content of a structured
        file is S3 being loaded to a Redshift table is either mismatched with the
        datatype in the destination table, or is otherwise misstructured.

        When Redshift encounters a database load errors, a row is written to
        stl_load_errors describing it's details. The output to INFO here gives
        direction on how to query that table to extract the error of concern.

        reference:
        https://www.psycopg.org/docs/module.html?highlight=internalerror#psycopg2.InternalError
        https://docs.aws.amazon.com/redshift/latest/dg/r_STL_LOAD_ERRORS.html
        '''
        if str(err.pgcode) == 'XX000':
            self.logger.info(
                "To begin investigating this database error, connect to the "
                "%s database with adminitrative credentials, then execute:\n"
                "> SELECT TOP 1 * FROM stl_load_errors WHERE filename LIKE "
                "'%%%s%%';", self.dbname, self.batchfile)

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
            f"dbname='{self.dbname}' "
            f"host='{self.host}' "
            f"port='{self.port}' "
            f"user='{self.user}'")

        try:
            conn = psycopg2.connect(dsn=connection_string)
            self.logger.debug(
                "Opened connection on connection string:\n%s",
                connection_string_log)
        except psycopg2.Error as err:
            self.logger.error(
                "Failed to connect using connection string:\n%s",
                connection_string_log)
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


    @classmethod
    def snowplow(cls, batchfile):
        'A factory constructor for the GDX Analytics Snowplow database'
        return cls(
            batchfile, 'snowplow', os.environ['pguser'], os.environ['pgpass'])
