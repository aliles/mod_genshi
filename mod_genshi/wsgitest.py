try:
    import unittest2 as unittest
except ImportError:
    import unittest

import string

import webob

import mod_genshi.wsgi

__all__ = ['TestWSGI']


class TestWSGIType(type):
    """Base type for TestWSGI

    To allow sub classes to define a setUpClass method, this type meta class
    will rename the setUpClass method on sub classes to a unique name that
    is called by the setUpClass method of TestWSGI.
    """

    @staticmethod
    def unused_name(suffix, names):
        """Create new, unique name with a given suffix."""
        for letter in string.letters:
            name = "_{0}_{1}".format(letter, suffix)
            if name not in names:
                break
        return name

    @classmethod
    def rename_method(meta, method, classdict):
        """Rename class method to new, unique name with same suffix."""
        if method in classdict:
            function = classdict[method]
            name = meta.unused_name(method, set(classdict.keys()))
            del classdict[method]
            classdict[name] = function

    def __new__(meta, classname, bases, classdict):
        if classname != 'TestWSGI':
            meta.rename_method('setUpClass', classdict)
            meta.rename_method('tearDownClass', classdict)
        return type.__new__(meta, classname, bases, classdict)


class TestWSGI(unittest.TestCase):
    """Subclass of unittest.TestCase for WSGI application testing.

    This class also provides the following methods.

     - get_request(url), create a new WSGI request object for URL.
     - get_response(request), generate the application response for request.

    Each sub class of this class will have an APPLICATION attribute. This is a
    new mod_genshi WSGI application. The base directory of the application
    will default to the current directory. This can be over ridden by creating
    a new BASE class attribute.

    Sub classes may define a setUpClass and tearDownClass.
    """

    __metaclass__ = TestWSGIType

    @classmethod
    def _call_suffixes(cls, suffix):
        for name in dir(cls):
            if not name.endswith(suffix) or name == suffix:
                continue
            attr = getattr(cls, name)
            if not hasattr(attr, '__call__'):
                continue
            attr()

    @classmethod
    def setUpClass(cls):
        """Create a new mod_genshi WSGI application."""
        if not hasattr(cls, 'BASE'):
            cls.BASE = '.'
        cls.APPLICATION = mod_genshi.wsgi.WSGI(cls.BASE)
        cls._call_suffixes('setUpClass')

    @classmethod
    def tearDownClass(cls):
        """Shutdown the mod_genshi WSGI application."""
        if hasattr(cls, 'APPLICATION'):
            del cls.APPLICATION
        cls._call_suffixes('tearDownClass')

    def get_request(self, url):
        """Create a new WSGI request object from the given URL."""
        return webob.Request.blank(url)

    def get_response(self, request):
        """Generate a WSGI response for the given request."""
        return request.get_response(self.APPLICATION)
