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

import _common
from _common import unittest
from _common import tempfile
from _common import MHTestSuite

import mediahandler.handler as MH
import mediahandler.util.notify as Notify
from mediahandler.util.config import _find_app


class NewHandlerTests(unittest.TestCase):

    def test_empty_args(self):
        regex = r'Handler class arguments should be type dict'
        self.assertRaises(
            TypeError, regex, MH.Handler)

    def test_none_args(self):
        regex = r'Missing input arguments for Handler class'
        self.assertRaisesRegexp(
            ValueError, regex, MH.Handler, None)

    def test_non_dict_args(self):
        regex = r'Handler class arguments should be type dict'
        self.assertRaisesRegexp(TypeError, regex, MH.Handler, 'string')
        self.assertRaisesRegexp(TypeError, regex, MH.Handler, ['an', 'array'])
        self.assertRaisesRegexp(TypeError, regex, MH.Handler, True)
        self.assertRaisesRegexp(TypeError, regex, MH.Handler, 8)

    def test_good_args(self):
        # Build arguments
        args = {
            'media': os.path.join('path', 'to', 'files'),
            'type': 'TV',
        }
        # Run handler
        new_handler = MH.Handler(args)
        # Check object structure
        self.assertIsNotNone(new_handler.args)
        self.assertIsNotNone(new_handler.settings)
        self.assertIsInstance(new_handler.push, Notify.Push)
        self.assertIsInstance(new_handler, MH.Handler)

    def test_good_args_config(self):
        # Get original conf file
        old_conf = _common.get_conf_file()
        # Setup temp conf path
        conf_dir = os.path.dirname(old_conf)
        new_conf = os.path.join(conf_dir, 'temp_NHT.conf')
        # Copy into temp file
        shutil.copy(old_conf, new_conf)
        # Build arguments
        args = {
            'media': os.path.join('path', 'to', 'files'),
            'type': 'TV',
            'config': new_conf,
        }
        # Run handler
        handler = MH.Handler(args)
        expected = _common.get_settings()
        # Check that they match
        self.assertDictEqual(handler.settings, expected)
        # Check object structure
        os.unlink(new_conf)


class ConvertTypeTests(unittest.TestCase):

    def setUp(self):
        # Temp args
        args = {'no_push': False}
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
        # Test name
        self.name = 'test-{0}'.format(_common.get_test_id())
        # Temp args
        args = {'no_push': False}
        # Make handler
        self.handler = MH.Handler(args)
        self.types_hash = _common.get_types_by_string()

    def test_bad_parse_path(self):
        path = os.path.join('path', 'to', 'media', 'filename')
        regex = r'Media type media not recognized'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._parse_dir, path)

    def test_bad_parse_path_stucture(self):
        # Set up args
        self.handler.args['name'] = self.name
        # Test bad path structure
        path = 'filename-only'
        regex = r'No type or name specified for media: {0}'.format(self.name)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._parse_dir, path)

    def run_good_type_path(self, stype):
        itype = self.types_hash[stype]
        # Build expected values
        filename = '{0}-{1}'.format(stype, _common.get_test_id())
        path = os.path.join('path', 'to', stype)
        full_path = os.path.join(path, filename)
        expected = {
            'path': path,
            'type': itype,
            'stype': stype,
            'name': filename,
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


class HandlerTestClass(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Dummy args
        self.name = "test-{0}".format(_common.get_test_id())
        self.args = {
            'name': self.name,
            'type': 1,
            'stype': 'TV'
        }
        # Set up handler
        self.handler = MH.Handler(self.args)
        # Make a dummy folder
        self.dir = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        # Placeholder for tmp files
        self.tmp_file = ''

    def tearDown(self):
        # Remove self.dirs
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        # Remove tmp file
        if os.path.exists(self.tmp_file):
            os.unlink(self.tmp_file)


class RemoveFileTests(HandlerTestClass):

    def run_remove_tests(self, args, skips=False, sf=False):
        self.tmp_file = _common.make_tmp_file()
        # Adjust handler settings
        self.handler.settings['single_file'] = sf
        self.handler.settings['General'] = args
        # Run handler
        self.handler._remove_files(self.tmp_file, skips)
        # Check that file exists
        if self.handler.settings['single_file']:
            self.assertFalse(os.path.exists(self.tmp_file))
        else:
            self.assertTrue(os.path.exists(self.tmp_file))

    def test_remove_keep_files(self):
        args = {
            'keep_files': True,
            'keep_if_skips': False
        }
        self.run_remove_tests(args)

    def test_remove_keep_dup_has_skips(self):
        args = {
            'keep_files': False,
            'keep_if_skips': True
        }
        self.run_remove_tests(args, True)

    def test_remove_keep_dups_no_skips(self):
        args = {
            'keep_files': False,
            'keep_if_skips': True
        }
        self.run_remove_tests(args, False, True)

    def test_remove_folder(self):
        # Adjust handler settings
        self.handler.settings['single_file'] = False
        self.handler.settings['General']['keep_files'] = False
        # Run handler
        self.handler._remove_files(self.dir, False)
        # Check that folder was deleted
        self.assertFalse(os.path.exists(self.dir))

    def test_remove_extracted(self):
        self.tmp_file = _common.make_tmp_file()
        # Adjust handler settings
        self.handler.settings['extracted'] = self.dir
        self.handler.settings['single_file'] = True
        self.handler.settings['General']['keep_files'] = False
        # Run handler
        self.handler._remove_files(self.tmp_file, False)
        # Check that file was deleted
        self.assertFalse(os.path.exists(self.tmp_file))
        self.assertFalse(os.path.exists(self.dir))


class FileHandlerTests(HandlerTestClass):

    def test_process_files_books(self):
        # Modify args & settings for books
        self.handler.args['type'] = 4
        self.handler.args['stype'] = 'Audiobooks'
        self.handler.settings['Audiobooks']['enabled'] = True
        self.handler.settings['single_file'] = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.m4b')
        # Run test
        regex = r'Folder for Audiobooks not found: .*Audiobooks'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.tmp_file)

    def test_process_files_single_video(self):
        # Modify args & settings for single video
        self.handler.args['type'] = 2
        self.handler.args['stype'] = 'Movies'
        self.handler.settings['single_file'] = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.avi')
        # Run test
        regex = r'Folder for Movies not found: .*Movies'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.tmp_file)

    def test_process_files_single_music(self):
        # Set up beets path
        _find_app(
            self.handler.settings['Music'], {'name': 'Beets', 'exec': 'beet'})
        # Modify args & settings for single music
        self.handler.args['type'] = 3
        self.handler.args['stype'] = 'Music'
        self.handler.settings['single_file'] = True
        self.handler.settings['Music']['enabled'] = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.mp3')
        # Run test
        regex = r'Unable to match tracks: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.tmp_file)

    def test_process_files_folder_video(self):
        # Modify args & settings for single video
        self.handler.args['type'] = 2
        self.handler.args['stype'] = 'Movies'
        self.handler.settings['single_file'] = False
        # Make a dummy file in dummy folder
        self.tmp_file = _common.make_tmp_file('.mkv', self.dir)
        # Run test
        regex = r'Folder for Movies not found: .*Movies'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.dir)

    def test_process_files_folder_music(self):
        # Set up beets path
        _find_app(
            self.handler.settings['Music'], {'name': 'Beets', 'exec': 'beet'})
        # Modify args & settings for single video
        self.handler.args['type'] = 3
        self.handler.args['stype'] = 'Music'
        self.handler.settings['single_file'] = False
        self.handler.settings['Music']['enabled'] = True
        # Make a dummy file in dummy folder
        self.tmp_file = _common.make_tmp_file('.mp3', self.dir)
        # Run test
        regex = r'Unable to match tracks: {0}'.format(self.dir)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.dir)


class CheckSuccessTests(HandlerTestClass):

    def test_results_none(self):
        results = ([], [])
        regex = r'No TV files found for: {0}'.format(self.name)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._check_success, self.dir, results)

    def test_results_skips(self):
        results = ([], [self.dir])
        regex = r'Some files were skipped:\n- {0}'.format(self.dir)
        added = self.handler._check_success(self.dir, results)
        self.assertRegexpMatches(added, regex)
        self.assertTrue(os.path.exists(self.dir))

    def test_results_good(self):
        self.handler.settings['single_file'] = False
        results = ([self.dir], [])
        reg = r'Media was successfully added to your server:\n\+ {0}'.format(
            self.dir)
        added = self.handler._check_success(self.dir, results)
        self.assertRegexpMatches(added, reg)
        self.assertFalse(os.path.exists(self.dir))

    def test_results_both(self):
        self.handler.settings['single_file'] = True
        self.tmp_file = _common.make_tmp_file()
        results = ([self.tmp_file], [self.dir])
        reg1 = r'Media was successfully added to your server:\n\+ {0}'.format(
            self.tmp_file)
        reg2 = r'Some files were skipped:\n- {0}'.format(self.dir)
        regex = r'{0}\n\n{1}'.format(reg1, reg2)
        added = self.handler._check_success(self.dir, results)
        self.assertRegexpMatches(added, regex)
        self.assertTrue(os.path.exists(self.dir))


class FindZippedTests(HandlerTestClass):

    def run_process_folder_test(self, ext, filebot=False):
        # Set filebot
        if not filebot:
            del self.handler.settings['TV']['has_filebot']
            del self.handler.settings['Movies']['has_filebot']
        # Make a dummy file in dummy folder
        self.tmp_file = _common.make_tmp_file(ext, self.dir)
        # Run test
        regex = r'Filebot required to extract: {0}'.format(self.name)
        if filebot:
            regex = r'Unable to extract files: {0}'.format(self.name)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._find_zipped, self.dir)

    def run_single_file_test(self, ext, filebot=False):
        # Set filebot
        if not filebot:
            del self.handler.settings['TV']['has_filebot']
            del self.handler.settings['Movies']['has_filebot']
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file(ext)
        # Run test
        regex = r'Filebot required to extract: {0}'.format(self.name)
        if filebot:
            regex = r'Unable to extract files: {0}'.format(self.name)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._find_zipped, self.tmp_file)

    def test_process_folder_zip(self):
        self.run_process_folder_test('.zip')

    def test_process_folder_rar(self):
        self.run_process_folder_test('.rar')

    def test_process_folder_7z(self):
        self.run_process_folder_test('.7z')

    def test_process_folder_filebot(self):
        self.run_process_folder_test('.zip', True)

    def test_single_file_zip(self):
        self.run_single_file_test('.zip')

    def test_single_file_rar(self):
        self.run_single_file_test('.rar')

    def test_single_file_7z(self):
        self.run_single_file_test('.7z')

    def test_single_file_filebot(self):
        self.run_single_file_test('.zip', True)


class AddMediaTests(HandlerTestClass):

    def setUp(self):
        # Call super
        super(AddMediaTests, self).setUp()
        # Overrides
        self.args = {
            'name': self.name,
            'type': 'TV'
        }
        self.handler = MH.Handler(self.args)

    def test_handle_good_path(self):
        # Modify args
        self.handler.args['media'] = self.dir
        # Run test
        regex = r'No TV files found for: {0}'.format(self.name)
        self.assertRaisesRegexp(SystemExit, regex, self.handler.add_media)

    def test_handle_bad_path(self):
        # Modify args
        self.handler.args = {
            'media': self.dir,
            'name': self.name,
        }
        # Run test
        regex = r'Media type .* not recognized'
        self.assertRaisesRegexp(SystemExit, regex, self.handler.add_media)

    def test_handle_fake_path(self):
        # Modify args
        self.handler.args['media'] = os.path.join('path', 'to', 'fake')
        # Run test
        regex = r'No media files found: {0}'.format(self.name)
        self.assertRaisesRegexp(SystemExit, regex, self.handler.add_media)


class AddMediaFilesTests(HandlerTestClass):

    def setUp(self):
        # Call super
        super(AddMediaFilesTests, self).setUp()
        # Get types hash
        self.types_hash = _common.get_types_by_string()
        # Set up beets path
        _find_app(
            self.handler.settings['Music'], {'name': 'Beets', 'exec': 'beet'})

    def test_forced_single_track(self):
        # Modify args & settings for single track
        self.handler.args['type'] = 3
        self.handler.args['stype'] = 'Music'
        self.handler.args['single_track'] = True
        self.handler.settings['single_file'] = False
        self.handler.settings['Music']['enabled'] = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.mp3')
        # Run test
        self.assertNotIn('single_track', self.handler.settings['Music'].keys())
        regex = r'Unable to match tracks: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler.add_media_files, self.tmp_file)
        # Check settings
        self.assertTrue(self.handler.settings['Music']['single_track'])

    def test_detected_single_track(self):
        # Modify args & settings for single track
        self.handler.args['type'] = 3
        self.handler.args['stype'] = 'Music'
        self.handler.settings['single_file'] = True
        self.handler.settings['Music']['enabled'] = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.mp3')
        # Run test
        self.assertNotIn('single_track', self.handler.settings['Music'].keys())
        regex = r'Unable to match tracks: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler.add_media_files, self.tmp_file)
        # Check settings
        self.assertTrue(self.handler.settings['Music']['single_track'])

    def test_custom_book_search(self):
        # Search string
        search_str = _common.random_string(10)
        # Modify args & settings for books
        self.handler.args['type'] = 4
        self.handler.args['stype'] = 'Audiobooks'
        self.handler.args['search'] = search_str
        self.handler.settings['single_file'] = False
        self.handler.settings['Audiobooks']['enabled'] = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.m4b')
        # Run test
        self.assertNotIn(
            'custom_search', self.handler.settings['Audiobooks'].keys())
        regex = r'Folder for Audiobooks not found: .*Audiobooks'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler.add_media_files, self.tmp_file)
        # Check settings
        self.assertIs(
            self.handler.settings['Audiobooks']['custom_search'], search_str)

    def run_add_type_test(self, stype, enabled=True):
        # Modify args & settings for books
        self.handler.args['type'] = self.types_hash[stype]
        self.handler.args['stype'] = stype
        self.handler.settings['single_file'] = True
        self.handler.settings[stype]['enabled'] = enabled
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file()
        # Run test
        regex = r'{0} type is not enabled'.format(stype)
        if enabled:
            regex = r'Folder for {0} not found: .*{1}'.format(stype, stype)
            if stype is 'Music':
                regex = r'Unable to match tracks: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler.add_media_files, self.tmp_file)

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
        # Modify args & settings for books
        self.handler.args['stype'] = 'Fake'
        self.handler.settings['single_file'] = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file()
        # Run first test
        self.assertRaises(
            KeyError, self.handler.add_media_files, self.tmp_file)
        # Second test
        self.handler.settings['Fake'] = {
            'enabled': True
        }
        self.assertRaises(
            ImportError, self.handler.add_media_files, self.tmp_file)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2, buffer=True)
