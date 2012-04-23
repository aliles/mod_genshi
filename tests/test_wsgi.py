import unittest

import mod_genshi.wsgi


class TestTemplatePath(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = mod_genshi.wsgi.WSGI()

    @classmethod
    def tearDownClass(cls):
        del cls.app

    def setUp(self):
        self.get_path = self.app._get_template_path

    def test_parent_path(self):
        exc = mod_genshi.wsgi.HTTPForbidden
        self.assertRaises(exc, self.get_path, '/../etc/password')

    def test_empty_path(self):
        self.assertEqual(self.get_path(''), 'index.html')

    def test_single_slash(self):
        self.assertEqual(self.get_path('/'), 'index.html')

    def test_double_slash(self):
        self.assertEqual(self.get_path('//'), 'index.html')

    def test_single_char(self):
        self.assertEqual(self.get_path('a'), 'a')

    def test_leading_slash(self):
        self.assertEqual(self.get_path('/a'), 'a')

    def test_trailing_slash(self):
        self.assertEqual(self.get_path('a/'), 'a/index.html')


class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = mod_genshi.wsgi.WSGI()

    @classmethod
    def tearDownClass(cls):
        del cls.app

    def setUp(self):
        self.response = mod_genshi.wsgi.Response()
        self.headers = self.app._headers

    def test_default(self):
        self.headers('', self.response)
        self.assertEqual(self.response.content_type, 'text/plain')
        self.assertIsNone(self.response.content_encoding)
        self.assertEqual(self.response.status_code, 200)

    def test_html(self):
        self.headers('index.html', self.response)
        self.assertEqual(self.response.content_type, 'text/html')
        self.assertIsNone(self.response.content_encoding)
        self.assertEqual(self.response.status_code, 200)

    def test_txt(self):
        self.headers('index.txt', self.response)
        self.assertEqual(self.response.content_type, 'text/plain')
        self.assertIsNone(self.response.content_encoding)
        self.assertEqual(self.response.status_code, 200)


class TestBody(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = mod_genshi.wsgi.WSGI()

    @classmethod
    def tearDownClass(cls):
        del cls.app

    def setUp(self):
        self.req = mod_genshi.wsgi.Request({})
        self.resp = mod_genshi.wsgi.Response()
        self.body = self.app._body

    @unittest.skip('Plain text templates not supported')
    def test_hello_world_txt(self):
        path = 'tests/templates/hello_world.txt'
        content = open(path, 'rt').read()
        self.body('tests/templates/hello_world.txt', self.req, self.resp)
        self.assertEqual(self.resp.body, content)

    def test_hello_world_html(self):
        path = 'tests/templates/hello_world.html'
        content = open(path, 'rt').read()
        self.body('tests/templates/hello_world.html', self.req, self.resp)
        self.assertEqual(self.resp.body, content)

    def test_not_found(self):
        path = 'tests/templates/__not_found__.html'
        exc = mod_genshi.wsgi.TemplateNotFound
        self.assertRaises(exc, self.body, path, self.req, self.resp)
