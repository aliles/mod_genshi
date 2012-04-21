"""mod_genshi development server.
"""
from wsgiref.simple_server import make_server

from mod_genshi.app import handler

if __name__ == '__main__':
    httpd = make_server('', 8000, handler)
    httpd.serve_forever()
