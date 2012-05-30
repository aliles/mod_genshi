import os
import sys

import mod_genshi.wsgitest


class TestRequests(mod_genshi.wsgitest.TestWSGI):

    BASE = 'tests/app'

    def test_hello_world_html(self):
        path = 'templates/hello_world.html'
        with open(os.path.join(self.BASE, path), 'rt') as template:
            content = template.read()
        request = self.get_request(path)
        response = self.get_response(request)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/html')
        self.assertEqual(response.body, content)

    def test_hello_world_text(self):
        path = 'templates/hello_world.txt'
        with open(os.path.join(self.BASE, path), 'rt') as template:
            content = template.read()
        request = self.get_request(path)
        response = self.get_response(request)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/plain')
        self.assertEqual(response.body, content)

    def test_static_file(self):
        path = 'static/logo.png'
        with open(os.path.join(self.BASE, path), 'rb') as template:
            content = template.read()
        request = self.get_request(path)
        response = self.get_response(request)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'image/png')
        self.assertEqual(response.body, content)

    def test_forbidden(self):
        path = 'static/passwd'
        request = self.get_request(path)
        response = self.get_response(request)
        self.assertEqual(response.status_int, 403)

    def test_not_found_generic(self):
        path = 'static/_does_not_exist_'
        request = self.get_request(path)
        response = self.get_response(request)
        self.assertEqual(response.status_int, 403)

    def test_not_found_template(self):
        path = 'templates/_does_not_exist_.html'
        request = self.get_request(path)
        response = self.get_response(request)
        self.assertEqual(response.status_int, 404)

    def test_not_found_static(self):
        path = 'static/_does_not_exist_.png'
        request = self.get_request(path)
        response = self.get_response(request)
        self.assertEqual(response.status_int, 404)

    def test_server_error(self):
        path = 'templates/invalid.html'
        request = self.get_request(path)
        response = self.get_response(request)
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
        request = self.get_request(path)
        self.get_response(request)
        self.assertEqual(sys.modules['python.counter'].value, 2)
        # initiate reload
        os.utime(code, None)
        # request two
        request = self.get_request(path)
        self.get_response(request)
        self.assertEqual(sys.modules['python.counter'].value, 1)
