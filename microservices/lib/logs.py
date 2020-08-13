# ref: https://github.com/acschaefer/duallog

import inspect
import logging
import copy
import os

# Define the default logging message formats.
FILE_FORMAT = '%(levelname)s:%(name)s:%(asctime)s:%(message)s'
CONS_FORMAT = '%(message)s'

'''
The Custom Handler classes below override logging File and Stream Handlers
to allow log formatting on evert line of a log message, instead of only on
the first line as is the default handling emit method of logging's handlers.

Emit creates a copy of the LogRecord (a logged event), and sets the copy's
message to getMessage() which is the argument-evaluated form of the message,
it then sets the arguments to an empty tuple. the LogRecord's message is then
split on each newline and each line gets emitted to the super class's emit().
As a result, each line is treated as a new LogRecord with no arguments to be
evaluated; so the Formatter formats each new line of logged messages.

References:
https://docs.python.org/3.7/library/logging.html#logging.LogRecord
https://docs.python.org/3.7/library/logging.html#logging.LogRecord.getMessage
'''
class CustomFileHandler(logging.FileHandler):
    def __init__(self, file):
        super(CustomFileHandler, self).__init__(file)

    def emit(self, record):
        fh_repack = copy.copy(record)
        fh_repack.msg = fh_repack.getMessage()
        fh_repack.args = ()
        messages = fh_repack.msg.split('\n')
        for message in messages:
            fh_repack.msg = message
            super(CustomFileHandler, self).emit(fh_repack)

class CustomStreamHandler(logging.StreamHandler):
    def __init__(self):
        super(CustomStreamHandler, self).__init__()

    def emit(self, record):
        sh_repack = copy.copy(record)
        sh_repack.msg = sh_repack.getMessage()
        sh_repack.args = ()
        messages = sh_repack.msg.split('\n')
        for message in messages:
            sh_repack.msg = message
            super(CustomStreamHandler, self).emit(sh_repack)

def setup(dir='logs', minLevel=logging.INFO):
    """ Set up dual logging to console and to logfile.
    """

    # Create the root logger.
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create the log filename based on caller filename
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    file_name = module.__file__.replace('.py', '.log')

    # Validate the given directory.
    dir = os.path.normpath(dir)

    # Create a folder for the logfiles.
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Construct the name of the logfile.
    file_path = os.path.join(dir, file_name)

    # Set up logging to the logfile.
    file_handler = CustomFileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(FILE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Set up logging to the console.
    stream_handler = CustomStreamHandler()
    stream_handler.setLevel(minLevel)
    stream_formatter = logging.Formatter(CONS_FORMAT)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient.discovery").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient.discovery_cache").setLevel(
        logging.ERROR)
    logging.getLogger("oauth2client.client").setLevel(logging.WARNING)
