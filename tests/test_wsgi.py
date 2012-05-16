import unittest2

import mod_genshi.wsgi


class ModGenshiApp(object):

    Markup = mod_genshi.wsgi.MarkupTemplate
    Text = mod_genshi.wsgi.NewTextTemplate
    HTTPForbidden = mod_genshi.wsgi.HTTPForbidden

    @classmethod
    def setUpClass(cls):
        cls.App = mod_genshi.wsgi.WSGI()
        cls.body = cls.App._body
        cls.cwd = cls.App.templatedir
        cls.get_path = cls.App._get_basic_path
        cls.get_style = cls.App._get_template_style
        cls.is_blocked = cls.App._is_path_blocked
        cls.is_static = cls.App._is_static_path_blocked
        cls.set_headers = cls.App._headers

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'App'):
            del cls.App

    def setUp(self):
        self.request = mod_genshi.wsgi.Request({})
        self.response = mod_genshi.wsgi.Response()


class TestTemplatePath(ModGenshiApp, unittest2.TestCase):

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


class TestStyle(ModGenshiApp, unittest2.TestCase):

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
        self.assertIs(self.get_style('file.xxx'), None)


class TestSecurity(ModGenshiApp, unittest2.TestCase):

    def test_index(self):
        path ='index.html'
        self.assertFalse(self.is_blocked(self.cwd, path))

    def test_parent_path(self):
        path = '../etc/password'
        self.assertRaises(self.HTTPForbidden, self.is_blocked, self.cwd, path)

    def test_hidden_file(self):
        path = '.password.txt'
        self.assertRaises(self.HTTPForbidden, self.is_blocked, self.cwd, path)

    def test_vim_swap_file(self):
        path = 'index.html.swp'
        self.assertRaises(self.HTTPForbidden, self.is_blocked, self.cwd, path)

    def test_vim_backup_file(self):
        path = 'index.html~'
        self.assertRaises(self.HTTPForbidden, self.is_blocked, self.cwd, path)

    def test_backup_file(self):
        path = 'index.html.bak'
        self.assertRaises(self.HTTPForbidden, self.is_blocked, self.cwd, path)

    def test_symbolic_link(self):
        path = 'tests/templates/passwd'
        self.assertRaises(self.HTTPForbidden, self.is_blocked, self.cwd, path)

    def test_static_file(self):
        path = 'file.mov'
        self.assertRaises(self.HTTPForbidden, self.is_static, path)


class TestHeaders(ModGenshiApp, unittest2.TestCase):

    def test_default(self):
        self.set_headers('', self.response)
        self.assertEqual(self.response.content_type, 'text/plain')
        self.assertIsNone(self.response.content_encoding)
        self.assertEqual(self.response.status_code, 200)

    def test_html(self):
        self.set_headers('index.html', self.response)
        self.assertEqual(self.response.content_type, 'text/html')
        self.assertIsNone(self.response.content_encoding)
        self.assertEqual(self.response.status_code, 200)

    def test_txt(self):
        self.set_headers('index.txt', self.response)
        self.assertEqual(self.response.content_type, 'text/plain')
        self.assertIsNone(self.response.content_encoding)
        self.assertEqual(self.response.status_code, 200)

    def test_gz(self):
        self.set_headers('file.txt.gz', self.response)
        self.assertEqual(self.response.content_type, 'text/plain')
        self.assertEqual(self.response.content_encoding, 'gzip')
        self.assertEqual(self.response.status_code, 200)


class TestBody(ModGenshiApp, unittest2.TestCase):

    def test_hello_world_txt(self):
        path = 'tests/templates/hello_world.txt'
        content = open(path, 'rt').read()
        self.body('tests/templates/hello_world.txt',
                  self.Text, self.request, self.response)
        self.assertEqual(self.response.body, content)

    def test_hello_world_html(self):
        path = 'tests/templates/hello_world.html'
        content = open(path, 'rt').read()
        self.body('tests/templates/hello_world.html',
                  self.Markup, self.request, self.response)
        self.assertEqual(self.response.body, content)

    def test_not_found(self):
        path = 'tests/templates/__not_found__.html'
        exc = mod_genshi.wsgi.TemplateNotFound
        self.assertRaises(exc, self.body, path,
                          self.Markup, self.request, self.response)

    def test_syntax_error(self):
        path = 'tests/templates/invalid.html'
        exc = mod_genshi.wsgi.TemplateError
        self.assertRaises(exc, self.body, path,
                          self.Markup, self.request, self.response)
