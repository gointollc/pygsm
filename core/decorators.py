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
from psycopg2.extensions import TRANSACTION_STATUS_INERROR
from core.db import db_connection, db_cursor

def rollback_on_failure(func):
    """ Decorateor that will rollback failed transactions """

    def wrapper(*args, **kwargs):
        
        result = func(*args, **kwargs)
        
        status = db_connection.get_transaction_status()

        if status == TRANSACTION_STATUS_INERROR:
            db_connection.rollback()

        return result
