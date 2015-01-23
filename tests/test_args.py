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

import _common
from _common import unittest
from _common import MHTestSuite

import mediahandler.util.args as Args


class ArgsTests(unittest.TestCase):

    def setUp(self):
        self.conf = _common.get_conf_file()
        self.folder = os.path.dirname(self.conf)

    def test_empty_args(self):
        sys.argv = ['']
        self.assertRaisesRegexp(
            SystemExit, '1', Args.get_arguments)

    def test_show_help(self):
        # Test 1
        sys.argv = ['', '-h']
        self.assertRaisesRegexp(
            SystemExit, '0', Args.get_arguments)
        # Test 2
        sys.argv = ['', '--help']
        self.assertRaisesRegexp(
            SystemExit, '0', Args.get_arguments)

    def test_cli_default_args(self):
        sys.argv = ['', self.folder,
            '--type', '4',
            '--query', 'this is my query',
            '-n',]
        args = Args.get_arguments()
        expected = {
            'config': self.conf,
            'media': self.folder,
            'name': 'mediahandler',
            'no_push': True,
            'single_track': False,
            'query': 'this is my query',
            'stype': 'Audiobooks',
            'type': 4,
        }
        self.assertDictEqual(args, expected)

    def test_cli_bad_type_args(self):
        # Bad File Path
        sys.argv = ['', '/path/to/files']
        regex1 = r'File or directory provided for {0} {1}: {2}'.format(
            'media', 'does not exist', '/path/to/files')
        self.assertRaisesRegexp(
            SystemExit, regex1, Args.get_arguments)
        # Bad type
        sys.argv = ['', self.folder, '-t', '5']
        self.assertRaisesRegexp(
            SystemExit, '2', Args.get_arguments)
        # Bad conf file
        sys.argv = ['', self.folder, '-t', '1', '-c', '/path/to/fake.yml']
        regex2 = r'File or directory provided for {0} {1}: {2}'.format(
            '-c', 'does not exist', '/path/to/fake.yml')
        self.assertRaisesRegexp(
            SystemExit, regex2, Args.get_arguments)

    def test_cli_bad_args(self):
        sys.argv = ['', '-s']
        self.assertRaisesRegexp(
            SystemExit, r'too few arguments', Args.get_arguments)


# class ParseDirTests(unittest.TestCase):

#     def setUp(self):
#         # Test name
#         self.name = 'test-{0}'.format(_common.get_test_id())
#         # Temp args
#         args = {'no_push': False}
#         # Make handler
#         self.handler = MH.MHandler(args)
#         self.types_hash = _common.get_types_by_string()

#     def test_bad_parse_path(self):
#         path = os.path.join('path', 'to', 'media', 'filename')
#         regex = r'Media type media not recognized'
#         self.assertRaisesRegexp(
#             SystemExit, regex, self.handler._parse_dir, path)

#     def test_bad_parse_path_stucture(self):
#         # Set up args
#         self.handler.args['name'] = self.name
#         # Test bad path structure
#         path = 'filename-only'
#         regex = r'No type or name specified for media: {0}'.format(self.name)
#         self.assertRaisesRegexp(
#             SystemExit, regex, self.handler._parse_dir, path)

#     def run_good_type_path(self, stype):
#         itype = self.types_hash[stype]
#         # Build expected values
#         filename = '{0}-{1}'.format(stype, _common.get_test_id())
#         path = os.path.join('path', 'to', stype)
#         full_path = os.path.join(path, filename)
#         expected = {
#             'path': path,
#             'type': itype,
#             'stype': stype,
#             'name': filename,
#             'no_push': False,
#         }
#         self.handler._parse_dir(full_path)
#         self.assertEqual(self.handler.args, expected)

#     def test_good_parse_tv_path(self):
#         self.run_good_type_path('TV')

#     def test_good_parse_movie_path(self):
#         self.run_good_type_path('Movies')

#     def test_good_parse_music_path(self):
#         self.run_good_type_path('Music')

#     def test_good_parse_book_path(self):
#         self.run_good_type_path('Audiobooks')


# class ConvertTypeTests(unittest.TestCase):

#     def setUp(self):
#         # Temp args
#         args = {'no_push': False}
#         # Make handler
#         self.handler = MH.MHandler(args)
#         self.types_hash = _common.get_types_by_string()

#     def run_type_test(self, test, is_bad=False):
#         stype = test['type']
#         itype = self.types_hash[stype]
#         # Loop through tests
#         for test in test['tests']:
#             # Set args
#             self.handler.args['type'] = test
#             # Run test
#             self.handler._convert_type()
#             # Check results
#             if is_bad:
#                 self.assertIsNot(
#                     self.handler.args['stype'], stype)
#                 self.assertNotEqual(
#                     self.handler.args['type'], itype)
#             else:
#                 self.assertIs(
#                     self.handler.args['stype'], stype)
#                 self.assertEqual(
#                     self.handler.args['type'], itype)

#     def test_good_tv_types(self):
#         test = {
#             'tests': [
#                 'tv',
#                 'tv shows',
#                 'TELEVISION',
#             ],
#             'type': 'TV',
#         }
#         self.run_type_test(test)

#     def test_bad_tv_types(self):
#         test = {
#             'tests': [
#                 'shows',
#                 'episode',
#                 'season'
#             ],
#             'type': 'TV',
#         }
#         self.run_type_test(test, True)

#     def test_good_movie_types(self):
#         test = {
#             'tests': ['Movies'],
#             'type': 'Movies',
#         }
#         self.run_type_test(test)

#     def test_bad_movie_types(self):
#         test = {
#             'tests': [
#                 'movie',
#                 'film',
#                 'cinema'
#             ],
#             'type': 'Movies',
#         }
#         self.run_type_test(test, True)

#     def test_good_music_types(self):
#         test = {
#             'tests': ['Music'],
#             'type': 'Music',
#         }
#         self.run_type_test(test)

#     def test_bad_music_types(self):
#         test = {
#             'tests': [
#                 'song',
#                 'album',
#                 'artist',
#             ],
#             'type': 'Music',
#         }
#         self.run_type_test(test, True)

#     def test_good_book_types(self):
#         test = {
#             'tests': [
#                 'books',
#                 'audiobooks'
#             ],
#             'type': 'Audiobooks',
#         }
#         self.run_type_test(test)

#     def test_bad_book_types(self):
#         test = {
#             'tests': [
#                 'book',
#                 'audiobook',
#                 'chapter',
#             ],
#             'type': 'Audiobooks',
#         }
#         self.run_type_test(test, True)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
