import argparse
import logging
import lib.logs as log
from lib.redshift import RedShift

# Ctrl+C
def signal_handler(signal, frame):
    '''handler function for Ctrl+c'''
    logger.debug('Ctrl+C pressed!')
    sys.exit(0)

def main():
    logger = logging.getLogger(__name__)
    log.setup()

    query = "SELECT COUNT(*) FROM google.googlesearch"

    snowDb = Redshift.snowplow()
    response = snowDb.query(query)

    logger.info(response)

    snowDb.close_connection()

if __name__ == "__main__":
    main()
