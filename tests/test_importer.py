import os
import sys

import unittest2

from mod_genshi import importer


class TestImporter(unittest2.TestCase):

    PACKAGE = 'tests/path'
    MODULE = 'tests/path/package/module.py'

    @classmethod
    def setUpClass(cls):
        cls.importer = importer.register(cls.PACKAGE)

    @classmethod
    def tearDownClass(cls):
        cls.importer.clear()
        importer.unregister(cls.PACKAGE)

    def setUp(self):
        self.assertNotIn('package', sys.modules)
        self.assertNotIn('package.module', sys.modules)

    def tearDown(self):
        self.importer.clear()

    def test_sys_path(self):
        self.assertIn(self.importer._token, sys.path)

    def test_import(self):
        __import__('package')
        self.assertIn('package', sys.modules)
        self.assertNotIn('package.module', sys.modules)
        __import__('package.module')
        self.assertIn('package', sys.modules)
        self.assertIn('package.module', sys.modules)

    def test_loaded(self):
        __import__('package')
        self.assertIn('package', self.importer.loaded)
        del self.importer.loaded
        self.assertNotIn('package', self.importer.loaded)
        self.assertNotIn('package', sys.modules)

    def test_modified(self):
        __import__('package.module')
        self.assertEqual(len(self.importer.modified), 0)
        os.utime(self.MODULE, None)
        self.assertGreater(len(self.importer.modified), 0)
        del self.importer.modified
        self.assertNotIn('package.module', sys.modules)

    def test_register(self):
        importer.register(self.PACKAGE)

    def test_unregister(self):
        importer.unregister('UNKNOWN PATH')
