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
import sys
import shutil

import _common
from _common import unittest
from _common import MHTestSuite

import mediahandler.util.args as Args
import mediahandler.util.torrent as Torrent
from mediahandler.util.config import parse_config


class DelugeTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Set up dummy file
        parent_folder = os.path.dirname(self.conf)
        self.folder = os.path.join(parent_folder, 'television')
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        # Make temp file in folder
        self.tmp_file = _common.make_tmp_file('.avi', self.folder)

    def tearDown(self):
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)

    def test_empty_args(self):
        sys.argv = ['']
        self.assertRaisesRegexp(
            SystemExit, '1', Args.get_deluge_arguments)

    def test_get_good_args(self):
        expected = {
            'media': self.tmp_file,
            'name': os.path.basename(self.tmp_file),
            'no_push': False,
            'single_track': False,
            'query': None,
            'type': 1,
            'stype': 'TV'
        }
        # Run test
        sys.argv = ['', 'hash', os.path.basename(self.tmp_file), self.folder]
        (config, args) = Args.get_deluge_arguments()
        self.assertEqual(config, self.conf)
        self.assertDictEqual(args, expected)

    def test_get_bad_args(self):
        # Test 1
        sys.argv = ['', 'hash', 'name']
        self.assertRaisesRegexp(
            SystemExit, r'too few arguments', Args.get_deluge_arguments)
        # Test 2
        sys.argv = ['', 'hash', 'name', '/path/to/file']
        regex = r'File or directory provided for {0} {1}: {2}'.format(
            'path', 'does not exist', '/path/to/file')
        self.assertRaisesRegexp(
            SystemExit, regex, Args.get_deluge_arguments)


class RemoveTorrentTests(unittest.TestCase):

    @_common.skipUnlessHasMod('twisted', 'internet')
    def setUp(self):
        from twisted.internet import reactor
        self.conf = _common.get_conf_file()
        self.settings = parse_config(self.conf)['Deluge']

    @_common.skipUnlessHasMod('deluge', 'ui')
    def test_remove_torrent(self):
        Torrent.remove_deluge_torrent(self.settings, 'hash')


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
