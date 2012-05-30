import unittest2
import socket

from mod_genshi.server import parse_command_line, open_browser_cmd


class TestBrowserCommnd(unittest2.TestCase):

    URL = "http://{0}:8000".format(socket.gethostname())

    def test_nothing(self):
        opts = parse_command_line([])
        cmd = open_browser_cmd(opts)
        self.assertIsNone(cmd)

    def test_current_window(self):
        opts = parse_command_line(['-b'])
        cmd = open_browser_cmd(opts)
        self.assertEqual(cmd.args, (self.URL,))
        self.assertEqual(cmd.keywords, {'new': 0, 'autoraise': False})

    def test_raise_current_window(self):
        opts = parse_command_line(['-b', '-r'])
        cmd = open_browser_cmd(opts)
        self.assertEqual(cmd.args, (self.URL,))
        self.assertEqual(cmd.keywords, {'new': 0, 'autoraise': True})

    def test_new_window(self):
        opts = parse_command_line(['-w'])
        cmd = open_browser_cmd(opts)
        self.assertEqual(cmd.args, (self.URL,))
        self.assertEqual(cmd.keywords, {'new': 1, 'autoraise': False})

    def test_new_tab(self):
        opts = parse_command_line(['-t', '-r'])
        cmd = open_browser_cmd(opts)
        self.assertEqual(cmd.args, (self.URL,))
        self.assertEqual(cmd.keywords, {'new': 2, 'autoraise': True})
