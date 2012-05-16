"""Configuration object for mod_genshi WSG application.
"""
import os


class Config(object):
    """Configuration container for mod_genshi WSGI application"""

    def __init__(self):
        self.set_defaults()

    def set_defaults(self):
        "Apply default settings"
        self.default_content_type = 'text/plain'
        self.index = 'index.html'
        # routing
        self.suffix_blocked = ('.swp', '.bak', '~')
        self.suffix_markup = ('.htm', '.html', '.xhtml', '.xml')
        self.suffix_static = ('.ico', '.gif', '.jpeg', '.jpg', '.png', '.svg')
        self.suffix_text = ('.json', '.text', '.txt')
        # template loading
        self.templatedir = os.path.abspath(os.curdir)
        # static files
        self.staticdir = os.path.abspath(os.curdir)
