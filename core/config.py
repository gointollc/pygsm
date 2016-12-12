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
import sys, configparser, logging

from utilities import exists

config = configparser.ConfigParser()
if not config.read('pygsm.cfg'):
    print("ERROR: Could not parse pygsm.cfg.  Make sure the config file exists and is readable.")
    sys.exit(1)

settings = {}

""" 
Logging config 
"""

# defaults
default_logfile = "/tmp/pygsm.log"
default_loglevel = logging.DEBUG

# If the Logging config section exists, use its parameters
if exists(config, 'Logging'):
    settings['LOG_FILE'] = config.get('Logging', 'file', fallback=default_logfile)
    settings['LOG_LEVEL'] = getattr(logging, config.get('Logging', 'level', fallback='DEBUG'), default_loglevel)

# otherwise, use the defaults
else:
    print("ERROR: Logging section of config file is missing!")
    settings['LOG_FILE'] = default_logfile
    settings['LOG_LEVEL'] = default_loglevel

""" 
DB config 
"""

# Check and make sure the section exists
if not exists(config, 'Database'):
    print("ERROR: Database section must be defined in pygsm.cfg for pygsm to function")
    sys.exit(1)

settings['DB_HOST'] = config.get('Database', 'hostname', fallback='localhost')
settings['DB_PORT'] = config.getint('Database', 'port', fallback=5432)
settings['DB_NAME'] = config.get('Database', 'name', fallback='pygsm')
settings['DB_USER'] = config.get('Database', 'user', fallback=None)
settings['DB_PASS'] = config.get('Database', 'password', fallback=None)

# Optional preferences
settings['GAME_MAX_AGE'] = config.getint('Pref', 'game_max_age', fallback=30)

# Auth
settings['AUTH_PSK_FORMAT'] = config.get('Auth', 'psk_format', fallback='string')

# Make sure we have the required settings
if not (settings['DB_HOST'] and settings['DB_USER'] and settings['DB_PASS']):
    print("ERROR: hostname, username, and password must be defined in pygsm.cfg for pygsm to function")
    sys.exit(1)
