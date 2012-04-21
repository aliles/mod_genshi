import unittest

import mod_genshi

class TestTouchstone(unittest.TestCase):

    def test_has_version(self):
        self.assertTrue(mod_genshi.__version__)
