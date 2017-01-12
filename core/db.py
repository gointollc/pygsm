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
import sys, psycopg2, psycopg2.extensions, psycopg2.extras

from core import log
from core.config import settings

# We want to assign directly to this module
this = sys.modules[__name__]

this.db_connection = None
this.db_cursor = None

# functions
def connect():
    """ Connect to the database """

    this.db_connection = psycopg2.connect(
        database    = settings['DB_NAME'],
        user        = settings['DB_USER'],
        password    = settings['DB_PASS'],
        host        = settings['DB_HOST'],
        port        = settings['DB_PORT']
    )

    if this.db_connection.status != psycopg2.extensions.STATUS_READY:
        # oops
        log.error("ERROR: Database connection failed!")
    else:
        # get the cursor
        this.db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return this.db_connection

# setup
if __name__ != '__main__':

    connect()
    psycopg2.extras.register_uuid()
    psycopg2.extras.register_default_jsonb(this.db_connection)