
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