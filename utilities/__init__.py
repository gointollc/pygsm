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

def exists(d, k):
    """ Check if a key exists in a dictionary """
    try:
        assert(d[k])
    except KeyError:
        return False
    finally:
        return True

def response(obj):
    """ Assemble a response """
    return {
        'code': 200,
        'success': True,
        'message': "Success",
        'results': obj,
    }

def response_positive(message, code = 200):
    """ Assemble a generic positive response """
    return {
        'code': code,
        'success': True,
        'message': message,
        'results': None,
    }

def response_error(message, code = 500):
    """ Assemble an error response """
    return {
        'code': code,
        'success': False,
        'message': message,
        'results': None,
    }