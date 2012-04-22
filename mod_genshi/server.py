"""mod_genshi development server.
"""
from wsgiref.simple_server import make_server
import sys

from mod_genshi.app import handler

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    httpd = make_server('', port, handler)
    httpd.serve_forever()
