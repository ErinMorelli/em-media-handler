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
import shutil

import _common
from _common import unittest
from _common import tempfile

import mediahandler.types as Types
import mediahandler.util.notify as Notify


class BaseMediaObjectTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Set up push object
        self.push = Notify.Push({
            'enabled': True,
            'notify_name': '',
            'api_key': _common.random_string(),
            'user_key': _common.random_string(),
        }, True)
        # Make temp dir
        self.folder = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Build base settings
        self.settings = { 'folder': self.folder }
        # Make an object
        self.media = Types.Media(self.settings, self.push)

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_new_media_object(self):
        expected = {
            'bin': '/usr/local/bin/filebot',
            'action': 'copy',
            'db': '',
            'flags': ['-non-strict', '-no-analytics'],
            'format': ''
        }
        # Check results
        self.assertEqual(self.media.type, 'media')
        self.assertEqual(self.media.ptype, 'Media')
        self.assertEqual(self.media.dst_path, self.folder)
        self.assertIsInstance(self.media.push, Notify.Push)
        self.assertDictEqual(self.media.filebot, expected)

    def test_new_media_bad_folder(self):
        # Dummy folder path
        tmp = { 'folder': '/path/to/fake' }
        # Run test 1
        regex1 = r'Folder for Media not found: /path/to/fake'
        self.assertRaisesRegexp(
            SystemExit, regex1, Types.Media, tmp, self.push)
        # Run test 2
        regex2 = r'Folder for Media not found: .*/Media/Media'
        self.assertRaisesRegexp(
            SystemExit, regex2, Types.Media, {}, self.push)


# TO DO:
#  - add
#  - media_info
#  - process_output
#  - match_error


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
