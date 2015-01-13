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

import mediahandler.util.args as Args
import mediahandler.util.torrent as Torrent


class ArgsTests(unittest.TestCase):

    def test_empty_args(self):
        sys.argv = ['']
        self.assertRaisesRegexp(
            SystemExit, '2', Args.get_arguments)

    def test_show_help(self):
        # Test 1
        sys.argv = ['', '-h']
        self.assertRaisesRegexp(
            SystemExit, '1', Args.get_arguments)
        # Test 2
        sys.argv = ['', '--help']
        self.assertRaisesRegexp(
            SystemExit, '1', Args.get_arguments)

    def test_cli_default_args(self):
        sys.argv = ['', '-f', '/path/to/files']
        args = Args.get_arguments()
        expected = {
            'media': '/path/to/files',
            'no_push': False,
            'single_track': False,
        }
        self.assertDictEqual(args, expected)

    def test_cli_bad_type_args(self):
        sys.argv = ['', '-f', '/path/to/files', '-t', 'TV']
        self.assertRaisesRegexp(
            SystemExit, '2', Args.get_arguments)
        sys.argv = ['', '-f', '/path/to/files', '-t', 5]
        self.assertRaisesRegexp(
            SystemExit, '2', Args.get_arguments)

    def test_cli_bad_args(self):
        sys.argv = ['', '--test']
        self.assertRaisesRegexp(
            SystemExit, '2', Args.get_arguments)
        sys.argv = ['', '-k']
        self.assertRaisesRegexp(
            SystemExit, '2', Args.get_arguments)

    def test_cli_all_args(self):
        sys.argv = ['', '-f', '/path/to/files',
                    '-t', '1', '-c', '/path/to/test.conf',
                    '-q', 'test query', '-s', '-n']
        args = Args.get_arguments()
        expected = {
            'single_track': True,
            'search': 'test query',
            'media': '/path/to/files',
            'no_push': True,
            'type': 'TV',
            'config': '/path/to/test.conf'
        }
        self.assertDictEqual(args, expected)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)