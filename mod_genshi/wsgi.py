"""WSGI application class for mod_genshi
"""

__all__ = ['WSGI']


class WSGI(object):
    """mod_genshi WSGI application."""

    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Hello world!\n']
