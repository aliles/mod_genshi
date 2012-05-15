import unittest2

import mod_genshi.wsgi


class TestTemplatePath(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = mod_genshi.wsgi.WSGI()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'app'):
            del cls.app

    def setUp(self):
        self.get_path = self.app._get_template_path

    def test_parent_path(self):
        exc = mod_genshi.wsgi.HTTPForbidden
        self.assertRaises(exc, self.get_path, '/../etc/password')

    def test_symbolic_link(self):
        exc = mod_genshi.wsgi.HTTPForbidden
        self.assertRaises(exc, self.get_path, 'tests/templates/passwd')

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


class TestStyle(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = mod_genshi.wsgi.WSGI()

    @classmethod
    def tearDownClass(cls):
        del cls.app

    def setUp(self):
        self.get_style = self.app._get_template_style
        self.Markup = mod_genshi.wsgi.MarkupTemplate
        self.Text = mod_genshi.wsgi.NewTextTemplate

    def test_htm(self):
        self.assertIs(self.get_style('file.htm'), self.Markup)

    def test_html(self):
        self.assertIs(self.get_style('file.html'), self.Markup)

    def test_xhtml(self):
        self.assertIs(self.get_style('file.xhtml'), self.Markup)

    def test_xml(self):
        self.assertIs(self.get_style('file.xml'), self.Markup)

    def test_json(self):
        self.assertIs(self.get_style('file.json'), self.Text)

    def test_text(self):
        self.assertIs(self.get_style('file.text'), self.Text)

    def test_txt(self):
        self.assertIs(self.get_style('file.txt'), self.Text)

    def test_unknown(self):
        exc = mod_genshi.wsgi.HTTPNotFound
        self.assertRaises(exc, self.get_style, 'file.xxx')


class TestSecurity(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = mod_genshi.wsgi.WSGI()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'app'):
            del cls.app

    def setUp(self):
        self.is_blocked = self.app._is_path_blocked
        self.exception = mod_genshi.wsgi.HTTPForbidden

    def test_parent_path(self):
        self.assertRaises(self.exception, self.is_blocked, '/../etc/password')

    def test_hidden_file(self):
        self.assertRaises(self.exception, self.is_blocked, '/.password.txt')

    def test_vim_swap_file(self):
        self.assertRaises(self.exception, self.is_blocked, '/index.html.swp')

    def test_vim_backup_file(self):
        self.assertRaises(self.exception, self.is_blocked, '/index.html~')

    def test_backup_file(self):
        self.assertRaises(self.exception, self.is_blocked, '/index.html.bak')


class TestHeaders(unittest2.TestCase):

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

    def test_gz(self):
        self.headers('file.txt.gz', self.response)
        self.assertEqual(self.response.content_type, 'text/plain')
        self.assertEqual(self.response.content_encoding, 'gzip')
        self.assertEqual(self.response.status_code, 200)


class TestBody(unittest2.TestCase):

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
        self.Markup = mod_genshi.wsgi.MarkupTemplate
        self.Text = mod_genshi.wsgi.NewTextTemplate

    def test_hello_world_txt(self):
        path = 'tests/templates/hello_world.txt'
        content = open(path, 'rt').read()
        self.body('tests/templates/hello_world.txt', self.Text, self.req, self.resp)
        self.assertEqual(self.resp.body, content)

    def test_hello_world_html(self):
        path = 'tests/templates/hello_world.html'
        content = open(path, 'rt').read()
        self.body('tests/templates/hello_world.html', self.Markup, self.req, self.resp)
        self.assertEqual(self.resp.body, content)

    def test_not_found(self):
        path = 'tests/templates/__not_found__.html'
        exc = mod_genshi.wsgi.TemplateNotFound
        self.assertRaises(exc, self.body, path, self.Markup, self.req, self.resp)
