"""Configuration object for mod_genshi WSG application.
"""
import os

__all__ = ['Config']


class Config(object):
    """Configuration container for mod_genshi WSGI application"""

    def __init__(self, base):
        self.base = os.path.abspath(base)
        self.set_defaults()

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, path):
        self._base = os.path.abspath(path)

    def set_defaults(self):
        "Apply default settings"
        # http defaults
        self.default_content_type = 'text/plain'
        self.index = 'index.html'
        # routing
        self.suffix_blocked = ('.swp', '.bak', '~')
        self.suffix_markup = ('.htm', '.html', '.xhtml', '.xml')
        self.suffix_static = ('.ico', '.gif', '.jpeg', '.jpg', '.png', '.svg')
        self.suffix_text = ('.json', '.text', '.txt')
        # python module imports
        self.pythondir = self.base
        # template loading
        self.templatedir = self.base
        # static files
        self.staticdir = self.base
