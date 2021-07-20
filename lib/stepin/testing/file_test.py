# coding=utf-8

import os
import shutil

import tempfile
import unittest


class FileTest(unittest.TestCase):
    def setUp(self):
        self.temp_folder = tempfile.mkdtemp()

    def tpath(self, *pp):
        return os.path.join(self.temp_folder, *pp)

    def tearDown(self):
        shutil.rmtree(self.temp_folder)
