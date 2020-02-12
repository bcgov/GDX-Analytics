import logging
import os
import os.path

def setup_logging():
    # set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create stdout handler for logs at the INFO level
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create file handler for logs at the DEBUG level in /logs/s3_to_redshift.log
    log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
    handler = logging.FileHandler(os.path.join('logs', log_filename), "a",
                                  encoding=None, delay="true")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
