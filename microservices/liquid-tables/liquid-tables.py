import sys
import os
import argparse
import logging
import lib.logs as log
from lib.redshift import RedShift as Redshift

def main(sql):
    
    logger = logging.getLogger(__name__)
    log.setup()

    if not os.path.isfile(sql):
        logger.info('File not found: %s', sql)
        sys.exit(1)

    query = open(sql, 'r').read()

    snowDb = Redshift.snowplow()

    logger.debug('Query starting')
    response = snowDb.query(query)
    logger.debug('Query finished')
    logger.info(response)

    snowDb.close_connection()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='pass config and ddl to perform operation on database')
    parser.add_argument('sql', help='SQL files to execute against the Snowplow database')
    args = parser.parse_args()
    main(args.sql)
