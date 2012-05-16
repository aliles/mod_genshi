import unittest2

from webob import Request
import mod_genshi.wsgi


class TestRequests(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.App = mod_genshi.wsgi.WSGI()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'App'):
            del cls.App

    def test_hello_world_html(self):
        path = 'tests/templates/hello_world.html'
        with open(path, 'rt') as template:
            content = template.read()
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/html')
        self.assertEqual(response.body, content)

    def test_hello_world_text(self):
        path = 'tests/templates/hello_world.txt'
        with open(path, 'rt') as template:
            content = template.read()
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/plain')
        self.assertEqual(response.body, content)

    def test_static_file(self):
        path = 'tests/templates/logo.png'
        with open(path, 'rb') as template:
            content = template.read()
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'image/png')
        self.assertEqual(response.body, content)

    def test_forbidden(self):
        path = 'tests/templates/passwd'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 403)

    def test_not_found_generic(self):
        path = 'tests/templates/_does_not_exist_'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 403)

    def test_not_found_template(self):
        path = 'tests/templates/_does_not_exist_.html'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 404)

    def test_not_found_static(self):
        path = 'tests/templates/_does_not_exist_.png'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 404)

    def test_server_error(self):
        path = 'tests/templates/invalid.html'
        request = Request.blank(path)
        response = request.get_response(self.App)
        self.assertEqual(response.status_int, 500)
