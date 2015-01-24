#!/usr/bin/python
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014-2015 Erin Morelli
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
import shutil
import zipfile as zf
import contextlib

import _common
from _common import unittest
from _common import tempfile
from _common import MHTestSuite

import mediahandler.util.extract as Extract
import mediahandler.handler as MH


class ExtractBadZipTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Tmp name
        self.name = "test-{0}".format(_common.get_test_id())
        # Make handler
        self.handler = MH.MHandler(self.conf)
        self.handler.set_settings({'name': self.name})
        self.filebot = self.handler.tv.filebot
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
        self.assertIsNone(Extract.get_files(self.filebot, self.bad_zip))

    def test_bad_non_zip(self):
        self.assertIsNone(Extract.get_files(self.filebot, self.bad_non_zip))

    def test_bad_handler_zip(self):
        # Run handler
        regex = r'Unable to extract files: {0}'.format(self.name)
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.handler.extract_files, self.bad_zip)

    def test_bad_handler_non_zip(self):
        # Run handler
        regex = r'Unable to extract files: {0}'.format(self.name)
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.handler.extract_files, self.bad_non_zip)


class ExtractGoodZipTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Tmp name
        self.name = "test-{0}".format(_common.get_test_id())
        self.folder = os.path.join(os.path.dirname(self.conf), 'test_ET')
        # Tmp args
        args = {
            'name': self.name,
            'type': 1,
            'stype': 'TV'
        }
        # Make handler
        self.handler = MH.MHandler(self.conf)
        self.handler.set_settings(args)
        self.filebot = self.handler.movies.filebot
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
        self.zip_name = os.path.join(os.path.dirname(self.conf), 'test_ET.zip')
        with contextlib.closing(zf.ZipFile(self.zip_name, "w")) as good_zip:
            good_zip.write(self.good_zip1, 'one.tmp')
            good_zip.write(self.good_zip2, 'two.tmp')

    def tearDown(self):
        os.unlink(self.good_zip1)
        os.unlink(self.good_zip2)
        os.unlink(self.zip_name)
        # Remove extracted files
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)

    def test_good_extract(self):
        files = Extract.get_files(self.filebot, self.zip_name)
        self.assertEqual(files, self.folder)
        self.assertTrue(os.path.exists(files))

    def test_good_handler_zip_tv(self):
        # Run handler
        files = self.handler.extract_files(self.zip_name)
        self.assertEqual(files, self.folder)
        self.assertTrue(os.path.exists(files))
        self.assertEqual(self.handler.extracted, self.zip_name)

    def test_good_handler_zip_movies(self):
        delattr(self.handler.tv, 'filebot')
        # Run handler
        files = self.handler.extract_files(self.zip_name)
        self.assertEqual(files, self.folder)
        self.assertTrue(os.path.exists(files))
        self.assertEqual(self.handler.extracted, self.zip_name)

    def test_good_handler_zip_found(self):
        # Run handler
        regex = r'Folder for TV not found: .*TV'
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.handler._find_zipped, self.zip_name)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
