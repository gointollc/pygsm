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
"""
auth.py 

This file handles authentication for the API on methods that require it.
"""
import uuid
from core.db import DB
from core.config import settings

db = DB()

""" Exceptions """
class InvalidValidator(TypeError): pass
class AuthenticationFailed(Exception): pass

""" PSK Format verification functions 

    These functions, as well as any user-defined ones, should take one 
    argument(the PSK) and use assertions to verify the PSK format.
"""

def verify_string(s):
    """ Make sure value is string """
    # check type
    if type(s) != str:
        return False

    return True

def verify_uuid(u):
    """ Make sure value is a valid UUID """
    # try and create a UUID object
    try:
        uuid.UUID(u)
    except ValueError: 
        return False

    return True

def verify_md5(m):
    """ Make sure value is md5 string """
    # check length
    if len(m) != 32:
        return False
    # make sure it's valid hex
    try:
        int(m, 16)
    except ValueError:
        return False

    return True

class Auth:
    """ Handles authentication and stores information of the user """

    # Should be defined with key as name and a verification function as
    # the value.
    validators = {
        'string': verify_string,
        'uuid': verify_uuid,
        'md5': verify_md5,
    }

    # This PSK
    psk = None

    # Whether or not this is a development key
    development = True

    # Description info put in the DB
    description = None

    def __init__(self, psk):

        # sanity check
        if not psk:
            raise Exception("Auth must be instantiated with a PSK")

        self.psk = psk

    def register_validator(self, name, validator):
        """ Register a PSK type with its validator """
        
        if not callable(validator):
            raise InvalidValidator("The provided validator is not callable")

        valid_types[name] = validator

    def validate(self, type_name = 'string'):
        """ Make sure the PSK fits the required format """

        # Make sure this type is even a validator we have
        if type_name not in self.validators:
            raise InvalidValidator("Validator was not found.")

        #validate
        try:
            return self.validators[type_name](self.psk)
        except AssertionError:
            return False

    def check_db(self):
        """ Check the PSK against the database """

        db.cursor.execute("""SELECT psk, development, description FROM 
            psk WHERE active = true AND psk = %s""", [self.psk])
        
        if db.cursor.rowcount > 0:
            psk_entry = db.cursor.fetchone()
            description = psk_entry['description']
            development = psk_entry['development']
            return True
        else:
            return False

    def authenticate(self, type_name = 'string'):
        """ Authenticate with the PSK """

        # validate the PSK
        if not self.validate(type_name):
            raise AuthenticationFailed("Authentication failed")

        # Make sure it's a real PSK
        if not self.check_db():
            raise AuthenticationFailed("Authentication failed")

        return True

def authenticate(psk):
    """ Authenticate with the PSK """
    auth = Auth(psk)

    try:
        auth.authenticate(settings['AUTH_PSK_FORMAT'])
    except AuthenticationFailed:
        return None

    return auth