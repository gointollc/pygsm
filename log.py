import logging
from datetime import datetime
from config import settings

logging.basicConfig(filename = settings['LOG_FILE'], level = settings['LOG_LEVEL'])

def debug(msg):
    logging.debug(msg)
def info(msg):
    logging.info(msg)
def warning(msg):
    logging.warning(msg)
def error(msg):
    logging.error(msg)
def critical(msg):
    logging.critical(msg)

debug("Log opened on %s" % datetime.now())