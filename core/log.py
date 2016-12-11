"""
pygsm - A RESTful API that acts as a game server tracker

Copyright (C) 2016 GoInto, LLC

This file is part of pygsm.

pygsm is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free 
Software Foundation, either version 2 of the License, or (at your option)
any later version.

pygsm is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE.

See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with pygsm. If 
not, see <http://www.gnu.org/licenses/>.
"""
import logging
from datetime import datetime

from core.config import settings

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