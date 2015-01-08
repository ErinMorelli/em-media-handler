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
        self.types_hash = _common.get_types_by_string()

    def run_type_test(self, test, is_bad=False):
        stype = test['type']
        itype = self.types_hash[stype]
        # Loop through tests
        for test in test['tests']:
            # Set args
            self.handler.args['type'] = test
            # Run test
            self.handler._convert_type()
            # Check results
            if is_bad:
                self.assertIsNot(
                    self.handler.args['stype'], stype)
                self.assertNotEqual(
                    self.handler.args['type'], itype)
            else:
                self.assertIs(
                    self.handler.args['stype'], stype)
                self.assertEqual(
                    self.handler.args['type'], itype)

    def test_good_tv_types(self):
        test = {
            'tests': [
                'tv',
                'tv shows',
                'TELEVISION',
            ],
            'type': 'TV',
        }
        self.run_type_test(test)

    def test_bad_tv_types(self):
        test = {
            'tests': [
                'shows',
                'episode',
                'season'
            ],
            'type': 'TV',
        }
        self.run_type_test(test, True)

    def test_good_movie_types(self):
        test = {
            'tests': ['Movies'],
            'type': 'Movies',
        }
        self.run_type_test(test)

    def test_bad_movie_types(self):
        test = {
            'tests': [
                'movie',
                'film',
                'cinema'
            ],
            'type': 'Movies',
        }
        self.run_type_test(test, True)

    def test_good_music_types(self):
        test = {
            'tests': ['Music'],
            'type': 'Music',
        }
        self.run_type_test(test)

    def test_bad_music_types(self):
        test = {
            'tests': [
                'song',
                'album',
                'artist',
            ],
            'type': 'Music',
        }
        self.run_type_test(test, True)

    def test_good_book_types(self):
        test = {
            'tests': [
                'books',
                'audiobooks'
            ],
            'type': 'Audiobooks',
        }
        self.run_type_test(test)

    def test_bad_book_types(self):
        test = {
            'tests': [
                'book',
                'audiobook',
                'chapter',
            ],
            'type': 'Audiobooks',
        }
        self.run_type_test(test, True)


class ParseDirTests(unittest.TestCase):

    def setUp(self):
        # Temp args
        args = {'use_deluge': False}
        # Make handler
        self.handler = MH.Handler(args)
        self.types_hash = _common.get_types_by_string()

    def test_bad_parse_path(self):
        path = '/path/to/media/filename'
        regex = r'Media type media not recognized'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._parse_dir, path)

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
        regex = (r'No type or name specified for media: %s'
                % filename)
        self.assertRaisesRegexp(
            SystemExit, regex, new_handler._parse_dir, path)

    def run_good_type_path(self, stype): 
        itype = self.types_hash[stype]
        # Build expected values
        filename = '%s-%s' % (stype, _common.get_test_id())
        path = '/path/to/%s' % stype
        full_path = '%s/%s' % (path, filename)
        expected = {
            'path': path,
            'type': itype,
            'stype': stype,
            'name': filename,
            'use_deluge': False,
            'no_push': False,
        }
        self.handler._parse_dir(full_path)
        self.assertEqual(self.handler.args, expected)

    def test_good_parse_tv_path(self):
        self.run_good_type_path('TV')

    def test_good_parse_movie_path(self):
        self.run_good_type_path('Movies')

    def test_good_parse_music_path(self):
        self.run_good_type_path('Music')

    def test_good_parse_book_path(self):
        self.run_good_type_path('Audiobooks')
        

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

    def run_remove_tests(self, args, skips=False, sf=False):
        tmp = _common.random_string(3)
        # Make temp file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp',
            delete=False)
        self.tmp_file[tmp] = get_file.name
        get_file.close()
        # Adjust handler settings
        self.handler.settings['single_file'] = sf
        self.handler.settings['General'] = args
        # Run handler
        self.handler._remove_files(self.tmp_file[tmp], skips)
        # Check that file exists
        if self.handler.settings['single_file']:
            self.assertFalse(os.path.exists(self.tmp_file[tmp]))
        else:
            self.assertTrue(os.path.exists(self.tmp_file[tmp]))

    def test_remove_keep_files(self):
        args = {
            'keep_files': True,
            'keep_if_duplicates': False
        }
        self.run_remove_tests(args)

    def test_remove_keep_dup_has_skips(self):
        args = {
            'keep_files': False,
            'keep_if_duplicates': True
        }
        self.run_remove_tests(args, True)

    def test_remove_keep_dups_no_skips(self):
        args = {
            'keep_files': False,
            'keep_if_duplicates': True
        }
        self.run_remove_tests(args, False, True)

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


class SingleFileTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Dummy args
        self.name = "test-%s" % _common.get_test_id()
        self.args = {
            'use_deluge': False,
            'name': self.name,
            'type': 1,
            'stype': 'TV'
        }

    def test_single_file_bool(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.mkv')
        file_name = get_file.name
        # Run test
        regex = r'Folder for TV not found: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, handler._single_file, file_name)
        # Check settings
        self.assertTrue(handler.settings['single_file'])
        get_file.close()

    def run_single_file_test(self, ext, filebot=False):
        # Set up handler
        handler = MH.Handler(self.args)
        handler.settings['has_filebot'] = filebot
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix=ext)
        file_name = get_file.name
        # Run test
        regex = r'Filebot required to extract: %s' % self.name
        if filebot:
            regex = r'Unable to extract files: %s' % self.name
        self.assertRaisesRegexp(
            SystemExit, regex, handler._single_file, file_name)

    def test_single_file_zip(self):
        self.run_single_file_test('.zip')

    def test_single_file_rar(self):
        self.run_single_file_test('.rar')

    def test_single_file_7z(self):
        self.run_single_file_test('.7z')

    def test_single_file_filebot(self):
        self.run_single_file_test('.zip', True)


class ProcessFolderTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Dummy args
        self.name = "test-%s" % _common.get_test_id()
        self.args = {
            'use_deluge': False,
            'name': self.name,
            'type': 1,
            'stype': 'TV'
        }
        # Store created dirs
        self.dirs = {}

    def tearDown(self):
        # Remove self.dirs
        for key in self.dirs.keys():
            shutil.rmtree(self.dirs[key])

    def test_process_file_bool(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Make a dummy folder
        self.dirs['b'] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Run test
        regex = r'No TV files found for: %s' % self.name
        self.assertRaisesRegexp(
            SystemExit, regex, handler._process_folder, self.dirs['b'])
        # Check settings
        self.assertFalse(handler.settings['single_file'])

    def run_process_file_test(self, ext, filebot=False):
        # Set up handler
        handler = MH.Handler(self.args)
        handler.settings['has_filebot'] = filebot
        # Make a dummy folder
        self.dirs[ext] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Make a dummy file in dummy folder
        get_file = tempfile.NamedTemporaryFile(
            dir=self.dirs[ext],
            suffix=ext,
            delete=False)
        # Run test
        regex = r'Filebot required to extract: %s' % self.name
        if filebot:
            regex = r'Unable to extract files: %s' % self.name
        self.assertRaisesRegexp(
            SystemExit, regex, handler._process_folder, self.dirs[ext])

    def test_process_file_zip(self):
        self.run_process_file_test('.zip')

    def test_process_file_rar(self):
        self.run_process_file_test('.rar')

    def test_process_file_7z(self):
        self.run_process_file_test('.7z')

    def test_process_file_filebot(self):
        self.run_process_file_test('.zip', True)

    def test_process_file_music(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for music
        handler.args['type'] = 3
        handler.args['stype'] = 'Music'
        handler.settings['Music']['enabled'] = False
        # Make a dummy folder
        self.dirs['f'] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Make a dummy file in dummy folder
        get_file = tempfile.NamedTemporaryFile(
            dir=self.dirs['f'],
            suffix='.mp3',
            delete=False)
        # Run test
        regex = r'Music type is not enabled'
        self.assertRaisesRegexp(
            SystemExit, regex, handler._process_folder, self.dirs['f'])

    def test_process_file_video(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Make a dummy folder
        self.dirs['v'] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Make a dummy file in dummy folder
        get_file = tempfile.NamedTemporaryFile(
            dir=self.dirs['v'],
            suffix='.avi',
            delete=False)
        # Run test
        regex = r'Folder for TV not found: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, handler._process_folder, self.dirs['v'])


class FileHandlerTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Dummy args
        self.name = "test-%s" % _common.get_test_id()
        self.args = {
            'use_deluge': False,
            'name': self.name,
        }
        # Store created dirs
        self.dirs = {}

    def tearDown(self):
        # Remove self.dirs
        for key in self.dirs.keys():
            shutil.rmtree(self.dirs[key])

    def test_file_handler_books(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for books
        handler.args['type'] = 4
        handler.args['stype'] = 'Audiobooks'
        handler.settings['Audiobooks']['enabled'] = True
        handler.settings['single_file'] = True
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.m4b')
        file_name = get_file.name
        # Run test
        regex = r'Folder for Audiobooks not found: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, handler._file_handler, file_name)
        get_file.close()

    def test_file_handler_single_video(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for single video
        handler.args['type'] = 2
        handler.args['stype'] = 'Movies'
        handler.settings['single_file'] = True
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.avi')
        file_name = get_file.name
        # Run test
        regex = r'Folder for Movies not found: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, handler._file_handler, file_name)
        get_file.close()

    def test_file_handler_single_music(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for single music
        handler.args['type'] = 3
        handler.args['stype'] = 'Music'
        handler.settings['single_file'] = True
        handler.settings['Music']['enabled'] = True
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.mp3')
        file_name = get_file.name
        # Run test
        regex = r'Unable to match tracks: %s' % file_name
        self.assertRaisesRegexp(
            SystemExit, regex, handler._file_handler, file_name)
        get_file.close()

    def test_file_handler_folder_video(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for single video
        handler.args['type'] = 2
        handler.args['stype'] = 'Movies'
        handler.settings['single_file'] = False
        # Make a dummy folder
        self.dirs['f'] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Make a dummy file in dummy folder
        get_file = tempfile.NamedTemporaryFile(
            dir=self.dirs['f'],
            suffix='.mkv',
            delete=False)
        # Run test
        regex = r'Folder for Movies not found: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, handler._file_handler, self.dirs['f'])

    def test_file_handler_folder_music(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for single video
        handler.args['type'] = 3
        handler.args['stype'] = 'Music'
        handler.settings['single_file'] = False
        handler.settings['Music']['enabled'] = True
        # Make a dummy folder
        self.dirs['m'] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Make a dummy file in dummy folder
        get_file = tempfile.NamedTemporaryFile(
            dir=self.dirs['m'],
            suffix='.mp3',
            delete=False)
        # Run test
        regex = r'Unable to match tracks: %s' % self.dirs['m']
        self.assertRaisesRegexp(
            SystemExit, regex, handler._file_handler, self.dirs['m'])


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

    def test_handle_good_path(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Make a dummy file
        self.dirs['g'] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Modify args
        handler.args['media'] = self.dirs['g']
        # Run test
        regex = r'No TV files found for: %s' % self.name
        self.assertRaisesRegexp(SystemExit, regex, handler._handle_media)

    def test_handle_bad_path(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Make a dummy file
        self.dirs['b'] = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Modify args
        handler.args = {
            'media': self.dirs['b'],
            'use_deluge': False,
            'name': self.name,
        }
        # Run test
        regex = r'Media type .* not recognized'
        self.assertRaisesRegexp(SystemExit, regex, handler._handle_media)

    def test_handle_fake_path(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args
        handler.args['media'] = '/path/to/fake'
        # Run test
        regex = r'No media files found: %s' % self.name
        self.assertRaisesRegexp(SystemExit, regex, handler._handle_media)


class AddMediaFilesTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Dummy args
        self.name = "test-%s" % _common.get_test_id()
        self.args = {
            'use_deluge': False,
            'name': self.name,
            'type': 1,
            'stype': 'TV'
        }
        # Store created dirs
        self.dirs = {}
        self.types_hash = _common.get_types_by_string()

    def tearDown(self):
        # Remove self.dirs
        for key in self.dirs.keys():
            shutil.rmtree(self.dirs[key])

    def test_forced_single_track(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for single track
        handler.args['type'] = 3
        handler.args['stype'] = 'Music'
        handler.args['single_track'] = True
        handler.settings['single_file'] = False
        handler.settings['Music']['enabled'] = True
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.mp3')
        file_name = get_file.name        
        # Run test
        self.assertNotIn('single_track', handler.settings['Music'].keys())
        regex = r'Unable to match tracks: %s' % file_name
        self.assertRaisesRegexp(
            SystemExit, regex, handler.add_media_files, file_name)
        # Check settings
        self.assertTrue(handler.settings['Music']['single_track'])
        get_file.close()

    def test_detected_single_track(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for single track
        handler.args['type'] = 3
        handler.args['stype'] = 'Music'
        handler.settings['single_file'] = True
        handler.settings['Music']['enabled'] = True
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.mp3')
        file_name = get_file.name        
        # Run test
        self.assertNotIn('single_track', handler.settings['Music'].keys())
        regex = r'Unable to match tracks: %s' % file_name
        self.assertRaisesRegexp(
            SystemExit, regex, handler.add_media_files, file_name)
        # Check settings
        self.assertTrue(handler.settings['Music']['single_track'])
        get_file.close()

    def test_custom_book_search(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Search string
        search_string = _common.random_string(10)
        # Modify args & settings for books
        handler.args['type'] = 4
        handler.args['stype'] = 'Audiobooks'
        handler.args['search'] = search_string
        handler.settings['single_file'] = False
        handler.settings['Audiobooks']['enabled'] = True
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.m4b')
        file_name = get_file.name        
        # Run test
        self.assertNotIn(
            'custom_search', handler.settings['Audiobooks'].keys())
        regex = r'Folder for Audiobooks not found: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, handler.add_media_files, file_name)
        # Check settings
        self.assertIs(
            handler.settings['Audiobooks']['custom_search'], search_string)
        get_file.close()

    def run_add_type_test(self, stype, enabled=True):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for books
        handler.args['type'] = self.types_hash[stype]
        handler.args['stype'] = stype
        handler.settings['single_file'] = True
        handler.settings[stype]['enabled'] = enabled
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp')
        file_name = get_file.name
        # Run test
        regex = r'%s type is not enabled' % stype
        if enabled:
            regex = r'Folder for %s not found: .*' % stype
            if stype is 'Music':
                regex = r'Unable to match tracks: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, handler.add_media_files, file_name)
        get_file.close()

    def test_add_tv_enabled(self):
        self.run_add_type_test('TV')

    def test_add_tv_disabled(self):
        self.run_add_type_test('TV', False)

    def test_add_movies_enabled(self):
        self.run_add_type_test('Movies')

    def test_add_movies_disabled(self):
        self.run_add_type_test('Movies', False)

    def test_add_music_enabled(self):
        self.run_add_type_test('Music')

    def test_add_music_disabled(self):
        self.run_add_type_test('Music', False)

    def test_add_books_enabled(self):
        self.run_add_type_test('Audiobooks')

    def test_add_books_disabled(self):
        self.run_add_type_test('Audiobooks', False)

    def test_bad_module_name(self):
        # Set up handler
        handler = MH.Handler(self.args)
        # Modify args & settings for books
        # handler.args['type'] = self.types_hash[stype]
        handler.args['stype'] = 'Fake'
        handler.settings['single_file'] = True
        # Make a dummy file
        get_file = tempfile.NamedTemporaryFile(
            dir=os.path.dirname(self.conf),
            suffix='.tmp')
        file_name = get_file.name
        # Run first test
        self.assertRaises(
            KeyError, handler.add_media_files, file_name)
        # Secont test
        handler.settings['Fake'] = {
            'enabled': True
        }
        self.assertRaises(
            ImportError, handler.add_media_files, file_name)
        get_file.close()


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
    