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

import sys

from _common import unittest

import mediahandler.util.torrent as Torrent


class DelugeTests(unittest.TestCase):

    def test_empty_args(self):
        sys.argv = ['']
        self.assertRaisesRegexp(
            SystemExit, '1', Torrent.get_deluge_arguments)

    def test_get_good_args(self):
        expected = {
            'media': '/path/to/file/name',
            'name': 'name',
            'no_push': False,
            'single_track': False,
        }
        # Run test
        sys.argv = ['', 'hash', 'name', '/path/to/file']
        args = Torrent.get_deluge_arguments()
        self.assertDictEqual(args, expected)

    def test_get_bad_args(self):
        # Test 1
        sys.argv = ['', 'hash', 'name']
        self.assertRaisesRegexp(
            SystemExit, '2', Torrent.get_deluge_arguments)
        # Test 2
        sys.argv = ['', 'hash', 'name', '/path/to/file', 'extra']
        self.assertRaisesRegexp(
            SystemExit, '2', Torrent.get_deluge_arguments)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)