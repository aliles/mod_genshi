import unittest2

import mod_genshi


class TestModGenshi(unittest2.TestCase):

    def test_has_version(self):
        self.assertTrue(mod_genshi.__version__)
