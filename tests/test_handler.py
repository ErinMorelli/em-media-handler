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
import shutil
from re import match
from cStringIO import StringIO

import _common
from _common import unittest
from _common import tempfile

import mediahandler.handler as MH
import mediahandler.util.notify as Notify


# class NewHandlerTests(unittest.TestCase):

#     def test_empty_args(self):
#         self.assertRaises(TypeError, MH.Handler)

#     def test_none_args(self):
#         self.assertRaises(ValueError, MH.Handler, None)

#     def test_non_dict_args(self):
#         self.assertRaises(TypeError, MH.Handler, 'string')
#         self.assertRaises(TypeError, MH.Handler, ['an', 'array'])
#         self.assertRaises(TypeError, MH.Handler, True)
#         self.assertRaises(TypeError, MH.Handler, 8)

#     def test_good_args(self):
#         # Build arguments
#         args = {
#             'media': '/path/to/files',
#             'type': 'TV',
#             'use_deluge': False
#         }
#         # Run handler
#         new_handler = MH.Handler(args)
#         # Check object structure
#         self.assertIsNotNone(new_handler.args)
#         self.assertIsNotNone(new_handler.settings)
#         self.assertIsInstance(new_handler.push, Notify.Push)
#         self.assertIsInstance(new_handler, MH.Handler)


# class ConvertTypeTests(unittest.TestCase):

#     def setUp(self):
#         # Temp args
#         args = {'use_deluge': False}
#         # Make handler
#         self.handler = MH.Handler(args)

#     def test_good_tv_types(self):
#         good_types = [
#             'tv',
#             'tv shows',
#             'TELEVISION',
#         ]
#         for good_type in good_types:
#             self.handler.args['type'] = good_type
#             self.handler._convert_type()
#             self.assertIs(self.handler.args['stype'], 'TV')
#             self.assertEqual(self.handler.args['type'], 1)

#     def test_bad_tv_types(self):
#         bad_types = [
#             'shows',
#             'episode',
#             'season'
#         ]
#         for bad_type in bad_types:
#             self.handler.args['type'] = bad_type
#             self.handler._convert_type()
#             self.assertIsNot(self.handler.args['stype'], 'TV')
#             self.assertNotEqual(self.handler.args['type'], 1)

#     def test_good_movie_types(self):
#         good_types = [
#             'Movies',
#         ]
#         for good_type in good_types:
#             self.handler.args['type'] = good_type
#             self.handler._convert_type()
#             self.assertIs(self.handler.args['stype'], 'Movies')
#             self.assertEqual(self.handler.args['type'], 2)

#     def test_bad_movie_types(self):
#         bad_types = [
#             'movie',
#             'film',
#             'cinema'
#         ]
#         for bad_type in bad_types:
#             self.handler.args['type'] = bad_type
#             self.handler._convert_type()
#             self.assertIsNot(self.handler.args['stype'], 'Movies')
#             self.assertNotEqual(self.handler.args['type'], 2)

#     def test_good_music_types(self):
#         good_types = [
#             'Music',
#         ]
#         for good_type in good_types:
#             self.handler.args['type'] = good_type
#             self.handler._convert_type()
#             self.assertIs(self.handler.args['stype'], 'Music')
#             self.assertEqual(self.handler.args['type'], 3)

#     def test_bad_music_types(self):
#         bad_types = [
#             'song',
#             'album',
#             'artist',
#         ]
#         for bad_type in bad_types:
#             self.handler.args['type'] = bad_type
#             self.handler._convert_type()
#             self.assertIsNot(self.handler.args['stype'], 'Music')
#             self.assertNotEqual(self.handler.args['type'], 3)

#     def test_good_book_types(self):
#         good_types = [
#             'books',
#             'audiobooks'
#         ]
#         for good_type in good_types:
#             self.handler.args['type'] = good_type
#             self.handler._convert_type()
#             self.assertIs(self.handler.args['stype'], 'Audiobooks')
#             self.assertEqual(self.handler.args['type'], 4)

#     def test_bad_book_types(self):
#         bad_types = [
#             'book',
#             'audiobook',
#             'chapter',
#         ]
#         for bad_type in bad_types:
#             self.handler.args['type'] = bad_type
#             self.handler._convert_type()
#             self.assertIsNot(self.handler.args['stype'], 'Audiobooks')
#             self.assertNotEqual(self.handler.args['type'], 4)


# class ParseDirTests(unittest.TestCase):

#     def setUp(self):
#         # Temp args
#         args = {'use_deluge': False}
#         # Make handler
#         self.handler = MH.Handler(args)

#     def test_bad_parse_path(self):
#         path = '/path/to/media/filename'
#         with self.assertRaises(SystemExit) as cm:
#             self.handler._parse_dir(path)
#         self.assertEqual(cm.exception.code, 2)

#     def test_bad_parse_path_stucture(self):
#         # Set up temp name
#         filename = 'bad-path-%s' % _common.get_test_id()
#         args = {
#             'use_deluge': False,
#             'name': filename
#         }
#         new_handler = MH.Handler(args)
#         # Test bad path structure
#         path = 'filename-only'
#         with self.assertRaises(SystemExit) as cm:
#             new_handler._parse_dir(path)
#         self.assertEqual(cm.exception.code, 2)

#     def test_good_parse_tv_path(self):
#         filename = 'tv-%s' % _common.get_test_id()
#         path = '/path/to/television/%s' % filename
#         expected = {
#             'path': '/path/to/television',
#             'type': 1,
#             'stype': 'TV',
#             'name': filename,
#             'use_deluge': False,
#             'no_push': False,
#         }
#         self.handler._parse_dir(path)
#         self.assertEqual(self.handler.args, expected)

#     def test_good_parse_movie_path(self):
#         filename = 'movie-%s' % _common.get_test_id()
#         path = '/path/to/movies/%s' % filename
#         expected = {
#             'path': '/path/to/movies',
#             'type': 2,
#             'stype': 'Movies',
#             'name': filename,
#             'use_deluge': False,
#             'no_push': False,
#         }
#         self.handler._parse_dir(path)
#         self.assertEqual(self.handler.args, expected)

#     def test_good_parse_music_path(self):
#         filename = 'music-%s' % _common.get_test_id()
#         path = '/path/to/music/%s' % filename
#         expected = {
#             'path': '/path/to/music',
#             'type': 3,
#             'stype': 'Music',
#             'name': filename,
#             'use_deluge': False,
#             'no_push': False,
#         }
#         self.handler._parse_dir(path)
#         self.assertEqual(self.handler.args, expected)

#     def test_good_parse_book_path(self):
#         filename = 'book-%s' % _common.get_test_id()
#         path = '/path/to/books/%s' % filename
#         expected = {
#             'path': '/path/to/books',
#             'type': 4,
#             'stype': 'Audiobooks',
#             'name': filename,
#             'use_deluge': False,
#             'no_push': False,
#         }
#         self.handler._parse_dir(path)
#         self.assertEqual(self.handler.args, expected)
        

# class RemoveFileTests(unittest.TestCase):

#     def setUp(self):
#         # Conf
#         self.conf = _common.get_conf_file()
#         # Temp args
#         args = {'use_deluge': False}
#         # Make handler
#         self.handler = MH.Handler(args)
#         self.tmp_file = {}

#     def tearDown(self):
#         for key in self.tmp_file.keys():
#             if os.path.exists(self.tmp_file[key]):
#                 os.unlink(self.tmp_file[key])

#     def test_remove_keep_files(self):
#         # Make temp file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.tmp',
#             delete=False)
#         self.tmp_file['kf'] = (get_file.name)
#         get_file.close()
#         # Adjust handler settings
#         self.handler.settings['General']['keep_files'] = True
#         self.handler.settings['General']['keep_if_duplicates'] = False
#         # Run handler
#         self.handler._remove_files(self.tmp_file['kf'], False)
#         # Check that file exists
#         self.assertTrue(os.path.exists(self.tmp_file['kf']))

#     def test_remove_keep_dup_has_skips(self):
#         # Make temp file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.tmp',
#             delete=False)
#         self.tmp_file['hs'] = get_file.name
#         get_file.close()
#         # Adjust handler settings
#         self.handler.settings['General']['keep_files'] = False
#         self.handler.settings['General']['keep_if_duplicates'] = True
#         # Run handler
#         self.handler._remove_files(self.tmp_file['hs'], True)
#         # Check that file exists
#         self.assertTrue(os.path.exists(self.tmp_file['hs']))

#     def test_remove_keep_dups_no_skips(self):
#         # Make temp file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.tmp',
#             delete=False)
#         self.tmp_file['ns'] = get_file.name
#         get_file.close()
#         # Adjust handler settings
#         self.handler.settings['single_file'] = True
#         self.handler.settings['General']['keep_files'] = False
#         self.handler.settings['General']['keep_if_duplicates'] = True
#         # Run handler
#         self.handler._remove_files(self.tmp_file['ns'], False)
#         # Check that file was deleted
#         self.assertFalse(os.path.exists(self.tmp_file['ns']))

#     def test_remove_folder(self):
#         # Make temp folder
#         get_folder = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Adjust handler settings
#         self.handler.settings['single_file'] = False
#         self.handler.settings['General']['keep_files'] = False
#         # Run handler
#         self.handler._remove_files(get_folder, False)
#         # Check that folder was deleted
#         self.assertFalse(os.path.exists(get_folder))

#     def test_remove_extracted(self):
#         # Make temp file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.tmp',
#             delete=False)
#         self.tmp_file['ex'] = get_file.name
#         get_file.close()
#         # Make temp folder
#         get_folder = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Adjust handler settings
#         self.handler.settings['extracted'] = get_folder
#         self.handler.settings['single_file'] = True
#         self.handler.settings['General']['keep_files'] = False
#         # Run handler
#         self.handler._remove_files(self.tmp_file['ex'], False)
#         # Check that file was deleted
#         self.assertFalse(os.path.exists(self.tmp_file['ex']))
#         self.assertFalse(os.path.exists(get_folder))


# class SingleFileTests(unittest.TestCase):

#     def setUp(self):
#         # Conf
#         self.conf = _common.get_conf_file()
#         # Dummy args
#         self.name = "test-%s" % _common.get_test_id()
#         self.args = {
#             'use_deluge': False,
#             'name': self.name,
#             'type': 1,
#             'stype': 'TV'
#         }

#     def test_single_file_bool(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.mkv')
#         file_name = get_file.name
#         # Run test
#         regex = r'Folder for TV not found: .*'
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._single_file, file_name)
#         # Check settings
#         self.assertTrue(handler.settings['single_file'])
#         get_file.close()

#     def test_single_file_zip(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = False
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.zip')
#         file_name = get_file.name
#         # Run test
#         regex = r'Filebot required to extract: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._single_file, file_name)

#     def test_single_file_rar(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = False
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.rar')
#         file_name = get_file.name
#         # Run test
#         regex = r'Filebot required to extract: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._single_file, file_name)

#     def test_single_file_7z(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = False
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.7z')
#         file_name = get_file.name
#         # Run test
#         regex = r'Filebot required to extract: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._single_file, file_name)

#     def test_single_file_filebot(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = True
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.zip')
#         file_name = get_file.name
#         # Run test
#         regex = r'Unable to extract files: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._single_file, file_name)


# class ProcessFolderTests(unittest.TestCase):

#     def setUp(self):
#         # Conf
#         self.conf = _common.get_conf_file()
#         # Dummy args
#         self.name = "test-%s" % _common.get_test_id()
#         self.args = {
#             'use_deluge': False,
#             'name': self.name,
#             'type': 1,
#             'stype': 'TV'
#         }
#         # Store created dirs
#         self.dirs = {}

#     def tearDown(self):
#         # Remove self.dirs
#         for key in self.dirs.keys():
#             shutil.rmtree(self.dirs[key])

#     def test_process_file_bool(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Make a dummy folder
#         self.dirs['b'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Run test
#         regex = r'No TV files found for: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._process_folder, self.dirs['b'])
#         # Check settings
#         self.assertFalse(handler.settings['single_file'])

#     def test_process_file_zip(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = False
#         # Make a dummy folder
#         self.dirs['z'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['z'],
#             suffix='.zip',
#             delete=False)
#         # Run test
#         regex = r'Filebot required to extract: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._process_folder, self.dirs['z'])

#     def test_process_file_rar(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = False
#         # Make a dummy folder
#         self.dirs['r'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['r'],
#             suffix='.rar',
#             delete=False)
#         # Run test
#         regex = r'Filebot required to extract: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._process_folder, self.dirs['r'])

#     def test_process_file_7z(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = False
#         # Make a dummy folder
#         self.dirs['7'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['7'],
#             suffix='.7z',
#             delete=False)
#         # Run test
#         regex = r'Filebot required to extract: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._process_folder, self.dirs['7'])

#     def test_process_file_filebot(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         handler.settings['has_filebot'] = True
#         # Make a dummy folder
#         self.dirs['f'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['f'],
#             suffix='.zip',
#             delete=False)
#         # Run test
#         regex = r'Unable to extract files: %s' % self.name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._process_folder, self.dirs['f'])

#     def test_process_file_music(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Modify args & settings for music
#         handler.args['type'] = 3
#         handler.args['stype'] = 'Music'
#         handler.settings['Music']['enabled'] = False
#         # Make a dummy folder
#         self.dirs['f'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['f'],
#             suffix='.mp3',
#             delete=False)
#         # Run test
#         regex = r'Music type is not enabled'
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._process_folder, self.dirs['f'])

#     def test_process_file_video(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Make a dummy folder
#         self.dirs['v'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['v'],
#             suffix='.avi',
#             delete=False)
#         # Run test
#         regex = r'Folder for TV not found: .*'
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._process_folder, self.dirs['v'])


# class FileHandlerTests(unittest.TestCase):

#     def setUp(self):
#         # Conf
#         self.conf = _common.get_conf_file()
#         # Dummy args
#         self.name = "test-%s" % _common.get_test_id()
#         self.args = {
#             'use_deluge': False,
#             'name': self.name,
#         }
#         # Store created dirs
#         self.dirs = {}

#     def tearDown(self):
#         # Remove self.dirs
#         for key in self.dirs.keys():
#             shutil.rmtree(self.dirs[key])

#     def test_file_handler_books(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Modify args & settings for books
#         handler.args['type'] = 4
#         handler.args['stype'] = 'Audiobooks'
#         handler.settings['Audiobooks']['enabled'] = True
#         handler.settings['single_file'] = True
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.m4b')
#         file_name = get_file.name
#         # Run test
#         regex = r'Folder for Audiobooks not found: .*'
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._file_handler, file_name)
#         get_file.close()

#     def test_file_handler_single_video(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Modify args & settings for single video
#         handler.args['type'] = 2
#         handler.args['stype'] = 'Movies'
#         handler.settings['single_file'] = True
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.avi')
#         file_name = get_file.name
#         # Run test
#         regex = r'Folder for Movies not found: .*'
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._file_handler, file_name)
#         get_file.close()

#     def test_file_handler_single_music(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Modify args & settings for single music
#         handler.args['type'] = 3
#         handler.args['stype'] = 'Music'
#         handler.settings['single_file'] = True
#         handler.settings['Music']['enabled'] = True
#         # Make a dummy file
#         get_file = tempfile.NamedTemporaryFile(
#             dir=os.path.dirname(self.conf),
#             suffix='.mp3')
#         file_name = get_file.name
#         # Run test
#         regex = r'Unable to match tracks: %s' % file_name
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._file_handler, file_name)
#         get_file.close()

#     def test_file_handler_folder_video(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Modify args & settings for single video
#         handler.args['type'] = 2
#         handler.args['stype'] = 'Movies'
#         handler.settings['single_file'] = False
#         # Make a dummy folder
#         self.dirs['f'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['f'],
#             suffix='.mkv',
#             delete=False)
#         # Run test
#         regex = r'Folder for Movies not found: .*'
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._file_handler, self.dirs['f'])

#     def test_file_handler_folder_music(self):
#         # Set up handler
#         handler = MH.Handler(self.args)
#         # Modify args & settings for single video
#         handler.args['type'] = 3
#         handler.args['stype'] = 'Music'
#         handler.settings['single_file'] = False
#         handler.settings['Music']['enabled'] = True
#         # Make a dummy folder
#         self.dirs['m'] = tempfile.mkdtemp(
#             dir=os.path.dirname(self.conf))
#         # Make a dummy file in dummy folder
#         get_file = tempfile.NamedTemporaryFile(
#             dir=self.dirs['m'],
#             suffix='.mp3',
#             delete=False)
#         # Run test
#         regex = r'Unable to match tracks: %s' % self.dirs['m']
#         self.assertRaisesRegexp(
#             SystemExit, regex, handler._file_handler, self.dirs['m'])


class HandleMediaTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Dummy args
        self.name = "test-%s" % _common.get_test_id()
        self.args = {
            'use_deluge': False,
            'name': self.name,
            'type': 'TV'
        }
        # Store created dirs
        self.dirs = {}

    def tearDown(self):
        # Remove self.dirs
        for key in self.dirs.keys():
            shutil.rmtree(self.dirs[key])

    def test_use_deluge_enabled(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.mkv')
        name_regex = r'%s/(.*)$' % os.path.dirname(self.conf)
        find_name = match(name_regex, get_file.name)
        file_name = find_name.group(1)
        # Modify args & settings for deluge
        handler.args['path'] = os.path.dirname(self.conf)
        handler.args['name'] = file_name
        handler.args['use_deluge'] = True
        handler.settings['Deluge']['enabled'] = True
        # Run test
        regex = r'No module named deluge.ui.client'
        self.assertRaisesRegexp(ImportError, regex, handler._handle_media)
        get_file.close()

    def test_use_deluge_disabled(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.mkv')
        name_regex = r'%s/(.*)$' % os.path.dirname(self.conf)
        find_name = match(name_regex, get_file.name)
        file_name = find_name.group(1)
        # Modify args & settings for deluge
        handler.args['path'] = os.path.dirname(self.conf)
        handler.args['name'] = file_name
        handler.args['use_deluge'] = True
        handler.settings['Deluge']['enabled'] = False
        # Run test
        regex = r'Folder for TV not found: .*'
        self.assertRaisesRegexp(SystemExit, regex, handler._handle_media)
        get_file.close()


# Dont use deluge
# Good dir
# Bad dir
#   - bad format
#   - doesnt exist

# def _handle_media(self):
#         '''Sort args based on input'''
#         logging.debug("Inputs: %s", self.args)
#         # Determing if using deluge or not
#         file_path = ''
#         use_deluge = self.args['use_deluge']
#         if use_deluge:
#             logging.info("Processing from deluge")
#             file_path = path.join(self.args['path'], self.args['name'])
#         else:
#             logging.info("Processing from command line")
#             file_path = self.args['media']
#         # Parse directory structure
#         self._parse_dir(file_path)
#         # Check that file was downloaded
#         if path.exists(file_path):
#             if self.settings['Deluge']['enabled'] and use_deluge:
#                 # Remove torrent
#                 import mediahandler.util.torrent as Torrent
#                 Torrent.remove_torrent(
#                     self.settings['Deluge'],
#                     self.args['hash'])
#             # Send to handler
#             new_files = self._file_handler(file_path)
#             # Check that files were returned
#             if new_files is None:
#                 self.push.failure("No media files found: %s" %
#                                   self.args['name'], True)
#         else:
#             # There was a problem, no files found
#             self.push.failure("No media files found: %s" %
#                               self.args['name'], True)
#         return new_files

# TODO:
#  - add_media_files
#  - _handle_media
#  - add_media


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main()#verbosity=2, buffer=True)
    