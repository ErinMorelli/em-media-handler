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
import sys
import zipfile
from shutil import rmtree

import _common
from _common import unittest
from _common import tempfile

import mediahandler.util.extract as Extract
import mediahandler.handler as MH


class ExtractBadZipTests(unittest.TestCase):

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

    def tearDown(self):
        os.unlink(self.bad_zip)
        os.unlink(self.bad_non_zip)

    def test_bad_zip(self):
        self.assertIsNone(Extract.get_files(self.bad_zip))
    
    def test_bad_non_zip(self):
        self.assertIsNone(Extract.get_files(self.bad_non_zip))


class ExtractGoodZipTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Make a good zip file contents
        get_good_zip1 = tempfile.NamedTemporaryFile(
            suffix='.tmp',
            delete=False
        )
        get_good_zip2 = tempfile.NamedTemporaryFile(
            suffix='.tmp',
            delete=False
        )
        self.good_zip1 = get_good_zip1.name
        self.good_zip2 = get_good_zip2.name
        get_good_zip1.close()
        get_good_zip2.close()
        # Make zip file
        self.zip_name = os.path.dirname(self.conf) + "/test_ET.zip"
        with zipfile.ZipFile(self.zip_name, "w") as good_zip:
            good_zip.write(self.good_zip1, 'one.tmp')
            good_zip.write(self.good_zip2, 'two.tmp')

    def tearDown(self):
        os.unlink(self.good_zip1)
        os.unlink(self.good_zip2)
        os.unlink(self.zip_name)
        #rmtree(os.path.dirname(self.conf)+"/test_ET")

    def test_good_extract(self):
        files = Extract.get_files(self.zip_name)
        self.assertEqual(files, os.path.dirname(self.conf)+"/test_ET")
        self.assertTrue(os.path.exists(files))


class HandlerExtractTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Tmp name
        self.name = "test-%s" % _common.get_test_id()
        # Tmp args
        args = {
            'use_deluge': False,
            'name': self.name,
        }
        # Make handler
        self.handler = MH.Handler(args)
        # Bad zip non with extension
        get_bad_zip = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.zip',
            delete=False
        )
        self.bad_zip = get_bad_zip.name
        get_bad_zip.close()
         # Bad zip non without extension
        get_bad_non_zip = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp',
            delete=False
        )
        self.bad_non_zip = get_bad_non_zip.name
        get_bad_non_zip.close()
        # Make a good zip file contents
        get_good_zip1 = tempfile.NamedTemporaryFile(
            suffix='.tmp',
            delete=False
        )
        get_good_zip2 = tempfile.NamedTemporaryFile(
            suffix='.tmp',
            delete=False
        )
        self.good_zip1 = get_good_zip1.name
        self.good_zip2 = get_good_zip2.name
        get_good_zip1.close()
        get_good_zip2.close()
        # Make zip file
        self.zip_name = os.path.dirname(self.conf) + "/test_HET.zip"
        with zipfile.ZipFile(self.zip_name, "w") as good_zip:
            good_zip.write(self.good_zip1, 'one.tmp')
            good_zip.write(self.good_zip2, 'two.tmp')

    def tearDown(self):
        os.unlink(self.bad_zip)
        os.unlink(self.bad_non_zip)
        os.unlink(self.good_zip1)
        os.unlink(self.good_zip2)
        os.unlink(self.zip_name)
        #rmtree(os.path.dirname(self.conf)+"/test_HET")

    def test_bad_handler_zip(self):
        # Run handler
        regex = r'Unable to extract files: %s' % self.name
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.handler.extract_files, self.bad_zip
        )

    def test_bad_handler_non_zip(self):
        # Run handler
        regex = r'Unable to extract files: %s' % self.name
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.handler.extract_files, self.bad_non_zip
        )

    def test_good_handler_zip(self):
        # Run handler
        files = self.handler.extract_files(self.zip_name)
        self.assertEqual(files, os.path.dirname(self.conf)+"/test_HET")
        self.assertTrue(os.path.exists(files))
        self.assertEqual(self.handler.settings['extracted'], self.zip_name)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
