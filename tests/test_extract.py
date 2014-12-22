#!/usr/bin/python
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014 Erin Morelli
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
'''Initialize module'''

import os
import zipfile
import tempfile

import _common
from _common import unittest

import mediahandler.util.extract as Extract


class ExtractTests(unittest.TestCase):

    def setUp(self):
        # Conf 
        self.conf = _common.get_conf_file()
        # Bad zip non without extension
        get_bad_non_zip = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp',
            delete=False
        )
        self.bad_non_zip = get_bad_non_zip.name
        get_bad_non_zip.close()
        # Bad zip non with extension
        get_bad_zip = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.zip',
            delete=False
        )
        self.bad_zip = get_bad_zip.name
        get_bad_zip.close()
        # Make a good zip file contents
        # get_good_zip1 = tempfile.NamedTemporaryFile(
        #     dir=os.path.dirname(self.conf),
        #     delete=False
        # )
        # get_good_zip2 = tempfile.NamedTemporaryFile(
        #     dir=os.path.dirname(self.conf),
        #     delete=False
        # )
        # self.good_zip1 = get_good_zip1.name
        # self.good_zip2 = get_good_zip2.name
        # get_good_zip1.close()
        # get_good_zip2.close()
        # # Make zip file
        # self.zip_name = os.path.dirname(self.conf) + "/test.zip"
        # good_zip = zipfile.ZipFile(self.zip_name, "w")
        # good_zip.write(self.good_zip1)
        # good_zip.write(self.good_zip2)
        # good_zip.close()

    def tearDown(self):
        os.unlink(self.good_zip1)
        os.unlink(self.good_zip2)
        os.unlink(self.bad_zip)
        os.unlink(self.bad_non_zip)
        #os.unlink(self.zip_name)

    def test_good_extract(self):
        return

    def test_bad_extract(self):
        # Test 1
        self.assertRaises(OSError,
            Extract.get_files, self.bad_zip)
        # Test 2
        self.assertRaises(OSError,
            Extract.get_files, self.bad_non_zip)


if __name__ == '__main__':
    unittest.main()
