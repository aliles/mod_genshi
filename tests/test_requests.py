import os
import sys

import unittest2

from webob import Request
import mod_genshi.wsgi


class TestRequests(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.App = mod_genshi.wsgi.WSGI('tests/app')

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'App'):
            del cls.App

    def test_hello_world_html(self):
        path = 'templates/hello_world.html'
        with open(os.path.join(self.App.config.base, path), 'rt') as template:
            content = template.read()
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/html')
        self.assertEqual(response.body, content)

    def test_hello_world_text(self):
        path = 'templates/hello_world.txt'
        with open(os.path.join(self.App.config.base, path), 'rt') as template:
            content = template.read()
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/plain')
        self.assertEqual(response.body, content)

    def test_static_file(self):
        path = 'static/logo.png'
        with open(os.path.join(self.App.config.base, path), 'rb') as template:
            content = template.read()
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'image/png')
        self.assertEqual(response.body, content)

    def test_forbidden(self):
        path = 'static/passwd'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 403)

    def test_not_found_generic(self):
        path = 'static/_does_not_exist_'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 403)

    def test_not_found_template(self):
        path = 'templates/_does_not_exist_.html'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 404)

    def test_not_found_static(self):
        path = 'static/_does_not_exist_.png'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 404)

    def test_server_error(self):
        path = 'templates/invalid.html'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 500)

    def test_reload_python(self):
        def set_counter():
            import python.counter
            python.counter.value = 1
        # paths
        path = 'templates/counter.txt'
        code = 'tests/app/python/counter.py'
        # initialise
        set_counter()
        # request one
        request = Request.blank(path)
        request.get_response(self.App)
        self.assertEqual(sys.modules['python.counter'].value, 2)
        # initiate reload
        os.utime(code, None)
        # request two
        request = Request.blank(path)
        request.get_response(self.App)
        self.assertEqual(sys.modules['python.counter'].value, 1)
