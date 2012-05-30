import os
import sys

import mod_genshi.wsgi
import mod_genshi.wsgitest


class ModGenshiApp(mod_genshi.wsgitest.TestWSGI):

    BASE = 'tests/app'

    Markup = mod_genshi.wsgi.MarkupTemplate
    Text = mod_genshi.wsgi.NewTextTemplate
    HTTPForbidden = mod_genshi.wsgi.HTTPForbidden

    @classmethod
    def setUpClass(cls):
        cls.body = cls.APPLICATION._body
        cls.cwd = cls.APPLICATION.config.templatedir
        cls.get_path = cls.APPLICATION._get_basic_path
        cls.get_style = cls.APPLICATION._get_template_style
        cls.is_blocked = cls.APPLICATION._is_path_blocked
        cls.is_static = cls.APPLICATION._is_static_path_blocked
        cls.set_headers = cls.APPLICATION._headers

    def setUp(self):
        self.request = mod_genshi.wsgi.Request({})
        self.response = mod_genshi.wsgi.Response()


class TestTemplatePath(ModGenshiApp):

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


class TestStyle(ModGenshiApp):

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


class TestSecurity(ModGenshiApp):

    def test_index(self):
        path = 'index.html'
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
        path = 'static/passwd'
        self.assertRaises(self.HTTPForbidden, self.is_blocked, self.cwd, path)

    def test_static_file(self):
        path = 'file.mov'
        self.assertRaises(self.HTTPForbidden, self.is_static, path)


class TestHeaders(ModGenshiApp):

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


class TestBody(ModGenshiApp):

    def test_hello_world_txt(self):
        path = 'templates/hello_world.txt'
        content = open(os.path.join(self.BASE, path), 'rt').read()
        self.body(path, self.Text, self.request, self.response)
        self.assertEqual(self.response.body, content)

    def test_hello_world_html(self):
        path = 'templates/hello_world.html'
        content = open(os.path.join(self.BASE, path), 'rt').read()
        self.body(path, self.Markup, self.request, self.response)
        self.assertEqual(self.response.body, content)

    def test_not_found(self):
        path = 'templates/__not_found__.html'
        exc = mod_genshi.wsgi.TemplateNotFound
        self.assertRaises(exc, self.body, path,
                          self.Markup, self.request, self.response)

    def test_syntax_error(self):
        path = 'templates/invalid.html'
        exc = mod_genshi.wsgi.TemplateError
        self.assertRaises(exc, self.body, path,
                          self.Markup, self.request, self.response)

    def test_load_python(self):
        path = 'templates/counter.txt'
        self.assertNotIn('python.counter', sys.modules)
        self.body(path, self.Text, self.request, self.response)
        self.assertIn('python.counter', sys.modules)
