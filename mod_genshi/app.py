"""Default mod_genshi WSGI application instance.
"""
from mod_genshi.wsgi import WSGI

__all__ = ['handler']

handler = WSGI()
