def build_request(method, *args, **kwargs):
    """
    Creates a request object with with specified method name, positional
    arguments and keyword arguments.

    :param str method: Method name.
    :param args: Arguments.
    :param kwargs: Keyword arguments.
    :return dict: A request object with following fields:
        - method
        - args
        - kwargs
    """
    return {
        'method': method,
        'args'  : args  ,
        'kwargs': kwargs,
    }

def build_response(status_code, status_text, data):
    """
    Creates a response object with specified status code, status code
    description and data.

    :param int status_code: Response status code.
    :param str status_text: Response status code description.
    :param data: Response data.
    :return dict: A response object with following fields:
        - status_code
        - status_text
        - data
    """
    return {
        'status_code': status_code,
        'status_text': status_text,
        'data': data,
    }
