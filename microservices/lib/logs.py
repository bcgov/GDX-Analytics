import inspect
import logging
import os
import os.path

def setup_logging(logger):
    'set up logging'

    logger.setLevel(logging.DEBUG)

    # create stdout handler for logs at the INFO level
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create file handler for logs at the DEBUG level under the `logs/` path;
    # the log filename will share the callers filename with .log instead of .py
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    log_filename = module.__file__.replace('.py', '.log')
    handler = logging.FileHandler(os.path.join('logs', log_filename), "a",
                                  encoding=None, delay="true")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
