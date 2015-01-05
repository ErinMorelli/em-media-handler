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

import sys

from _common import unittest

import mediahandler.util.args as Args


class ArgsTests(unittest.TestCase):

    def test_get_deluge_args(self):
        sys.argv = ['', 'hash', 'filename.tmp', '/path/to/file']
        args = Args.get_arguments()
        expected = {
            'path': '/path/to/file',
            'hash': 'hash',
            'name': 'filename.tmp',
            'use_deluge': True
        }
        self.assertEqual(args, expected)

    def test_bad_deluge_args(self):
        sys.argv = ['', 'hash', 'test.tmp', '/path/to/file', 'extra']
        with self.assertRaises(SystemExit) as cm:
            Args.get_arguments()
        self.assertEqual(cm.exception.code, 2)

    def test_cli_default_args(self):
        sys.argv = ['', '-f', '/path/to/files']
        args = Args.get_arguments()
        expected = {
            'media': '/path/to/files',
            'no_push': False,
            'use_deluge': False
        }
        self.assertEqual(args, expected)

    def test_cli_bad_type_args(self):
        sys.argv = ['', '-f', '/path/to/files', '-t', 'TV']
        with self.assertRaises(SystemExit) as cm:
            Args.get_arguments()
        self.assertEqual(cm.exception.code, 2)
        sys.argv = ['', '-f', '/path/to/files', '-t', 5]
        with self.assertRaises(SystemExit) as cm:
            Args.get_arguments()
        self.assertEqual(cm.exception.code, 2)

    def test_cli_all_args(self):
        sys.argv = ['', '-f', '/path/to/files',
                    '-t', '1', '-c', '/path/to/test.conf',
                    '-q', 'test query', '-s', '-n']
        args = Args.get_arguments()
        expected = {
            'single_track': True,
            'search': 'test query',
            'use_deluge': False,
            'media': '/path/to/files',
            'no_push': True,
            'type': 'TV',
            'config': '/path/to/test.conf'
        }
        self.assertEqual(args, expected)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)