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

import mediahandler.handler as MH
import mediahandler.util.notify as Notify


class NewHandlerTests(unittest.TestCase):

    def test_empty_args(self):
        self.assertRaises(TypeError, MH.Handler)

    def test_none_args(self):
        self.assertRaises(ValueError, MH.Handler, None)

    def test_non_dict_args(self):
        self.assertRaises(TypeError, MH.Handler, 'string')
        self.assertRaises(TypeError, MH.Handler, ['an', 'array'])
        self.assertRaises(TypeError, MH.Handler, True)
        self.assertRaises(TypeError, MH.Handler, 8)

    def test_good_args(self):
        # Build arguments
        args = {
            'media': '/path/to/files',
            'type': 'TV',
            'use_deluge': False
        }
        # Run handler
        new_handler = MH.Handler(args)
        # Check object structure
        self.assertIsNotNone(new_handler.args)
        self.assertIsNotNone(new_handler.settings)
        self.assertIsInstance(new_handler.push, Notify.Push)
        self.assertIsInstance(new_handler, MH.Handler)


class ConvertTypeTests(unittest.TestCase):

    def setUp(self):
        # Temp args
        args = {'use_deluge': False}
        # Make handler
        self.handler = MH.Handler(args)

    def test_good_tv_types(self):
        good_types = [
            'tv',
            'tv shows',
            'TELEVISION',
        ]
        for good_type in good_types:
            self.handler.args['type'] = good_type
            self.handler._convert_type()
            self.assertIs(self.handler.args['stype'], 'TV')
            self.assertEqual(self.handler.args['type'], 1)

    def test_bad_tv_types(self):
        bad_types = [
            'shows',
            'episode',
            'season'
        ]
        for bad_type in bad_types:
            self.handler.args['type'] = bad_type
            self.handler._convert_type()
            self.assertIsNot(self.handler.args['stype'], 'TV')
            self.assertNotEqual(self.handler.args['type'], 1)

    def test_good_movie_types(self):
        good_types = [
            'Movies',
        ]
        for good_type in good_types:
            self.handler.args['type'] = good_type
            self.handler._convert_type()
            self.assertIs(self.handler.args['stype'], 'Movies')
            self.assertEqual(self.handler.args['type'], 2)

    def test_bad_movie_types(self):
        bad_types = [
            'movie',
            'film',
            'cinema'
        ]
        for bad_type in bad_types:
            self.handler.args['type'] = bad_type
            self.handler._convert_type()
            self.assertIsNot(self.handler.args['stype'], 'Movies')
            self.assertNotEqual(self.handler.args['type'], 2)

    def test_good_music_types(self):
        good_types = [
            'Music',
        ]
        for good_type in good_types:
            self.handler.args['type'] = good_type
            self.handler._convert_type()
            self.assertIs(self.handler.args['stype'], 'Music')
            self.assertEqual(self.handler.args['type'], 3)

    def test_bad_music_types(self):
        bad_types = [
            'song',
            'album',
            'artist',
        ]
        for bad_type in bad_types:
            self.handler.args['type'] = bad_type
            self.handler._convert_type()
            self.assertIsNot(self.handler.args['stype'], 'Music')
            self.assertNotEqual(self.handler.args['type'], 3)

    def test_good_book_types(self):
        good_types = [
            'books',
            'audiobooks'
        ]
        for good_type in good_types:
            self.handler.args['type'] = good_type
            self.handler._convert_type()
            self.assertIs(self.handler.args['stype'], 'Audiobooks')
            self.assertEqual(self.handler.args['type'], 4)

    def test_bad_book_types(self):
        bad_types = [
            'book',
            'audiobook',
            'chapter',
        ]
        for bad_type in bad_types:
            self.handler.args['type'] = bad_type
            self.handler._convert_type()
            self.assertIsNot(self.handler.args['stype'], 'Audiobooks')
            self.assertNotEqual(self.handler.args['type'], 4)


class ParseDirTests(unittest.TestCase):

    def setUp(self):
        # Temp args
        args = {'use_deluge': False}
        # Make handler
        self.handler = MH.Handler(args)

    def test_bad_parse_path(self):
        path = '/path/to/media/filename'
        with self.assertRaises(SystemExit) as cm:
            self.handler._parse_dir(path)
        self.assertEqual(cm.exception.code, 2)

    def test_bad_parse_path_stucture(self):
        # Set up temp name
        filename = 'bad-path-%s' % _common.get_test_id()
        args = {
            'use_deluge': False,
            'name': filename
        }
        new_handler = MH.Handler(args)
        # Test bad path structure
        path = 'filename-only'
        with self.assertRaises(SystemExit) as cm:
            new_handler._parse_dir(path)
        self.assertEqual(cm.exception.code, 2)

    def test_good_parse_tv_path(self):
        filename = 'tv-%s' % _common.get_test_id()
        path = '/path/to/television/%s' % filename
        expected = {
            'path': '/path/to/television',
            'type': 1,
            'stype': 'TV',
            'name': filename,
            'use_deluge': False,
            'no_push': False,
        }
        self.handler._parse_dir(path)
        self.assertEqual(self.handler.args, expected)

    def test_good_parse_movie_path(self):
        filename = 'movie-%s' % _common.get_test_id()
        path = '/path/to/movies/%s' % filename
        expected = {
            'path': '/path/to/movies',
            'type': 2,
            'stype': 'Movies',
            'name': filename,
            'use_deluge': False,
            'no_push': False,
        }
        self.handler._parse_dir(path)
        self.assertEqual(self.handler.args, expected)

    def test_good_parse_music_path(self):
        filename = 'music-%s' % _common.get_test_id()
        path = '/path/to/music/%s' % filename
        expected = {
            'path': '/path/to/music',
            'type': 3,
            'stype': 'Music',
            'name': filename,
            'use_deluge': False,
            'no_push': False,
        }
        self.handler._parse_dir(path)
        self.assertEqual(self.handler.args, expected)

    def test_good_parse_book_path(self):
        filename = 'book-%s' % _common.get_test_id()
        path = '/path/to/books/%s' % filename
        expected = {
            'path': '/path/to/books',
            'type': 4,
            'stype': 'Audiobooks',
            'name': filename,
            'use_deluge': False,
            'no_push': False,
        }
        self.handler._parse_dir(path)
        self.assertEqual(self.handler.args, expected)
        

class RemoveFileTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Temp args
        args = {'use_deluge': False}
        # Make handler
        self.handler = MH.Handler(args)
        self.tmp_file = {}

    def tearDown(self):
        for key in self.tmp_file.keys():
            if os.path.exists(self.tmp_file[key]):
                os.unlink(self.tmp_file[key])

    def test_remove_keep_files(self):
        # Make temp file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp',
            delete=False)
        self.tmp_file['kf'] = (get_file.name)
        get_file.close()
        # Adjust handler settings
        self.handler.settings['General']['keep_files'] = True
        self.handler.settings['General']['keep_if_duplicates'] = False
        # Run handler
        self.handler._remove_files(self.tmp_file['kf'], False)
        # Check that file exists
        self.assertTrue(os.path.exists(self.tmp_file['kf']))

    def test_remove_keep_dup_has_skips(self):
        # Make temp file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp',
            delete=False)
        self.tmp_file['hs'] = get_file.name
        get_file.close()
        # Adjust handler settings
        self.handler.settings['General']['keep_files'] = False
        self.handler.settings['General']['keep_if_duplicates'] = True
        # Run handler
        self.handler._remove_files(self.tmp_file['hs'], True)
        # Check that file exists
        self.assertTrue(os.path.exists(self.tmp_file['hs']))

    def test_remove_keep_dups_no_skips(self):
        # Make temp file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp',
            delete=False)
        self.tmp_file['ns'] = get_file.name
        get_file.close()
        # Adjust handler settings
        self.handler.settings['single_file'] = True
        self.handler.settings['General']['keep_files'] = False
        self.handler.settings['General']['keep_if_duplicates'] = True
        # Run handler
        self.handler._remove_files(self.tmp_file['ns'], False)
        # Check that file was deleted
        self.assertFalse(os.path.exists(self.tmp_file['ns']))

    def test_remove_folder(self):
        # Make temp folder
        get_folder = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Adjust handler settings
        self.handler.settings['single_file'] = False
        self.handler.settings['General']['keep_files'] = False
        # Run handler
        self.handler._remove_files(get_folder, False)
        # Check that folder was deleted
        self.assertFalse(os.path.exists(get_folder))

    def test_remove_extracted(self):
        # Make temp file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp',
            delete=False)
        self.tmp_file['ex'] = get_file.name
        get_file.close()
        # Make temp folder
        get_folder = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Adjust handler settings
        self.handler.settings['extracted'] = get_folder
        self.handler.settings['single_file'] = True
        self.handler.settings['General']['keep_files'] = False
        # Run handler
        self.handler._remove_files(self.tmp_file['ex'], False)
        # Check that file was deleted
        self.assertFalse(os.path.exists(self.tmp_file['ex']))
        self.assertFalse(os.path.exists(get_folder))


# TODO:
#  - add_media_files
#  - _single_file
#  - _process_folder
#  - _file_handler
#  - _handle_media
#  - add_media


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
