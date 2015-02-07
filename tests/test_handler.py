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
from _common import tempfile
from _common import MHTestSuite

import mediahandler.handler as MH
import mediahandler.util.notify as Notify
from mediahandler.util.config import _find_app


class NewHandlerTests(unittest.TestCase):

    def test_bad_args(self):
        regex = r'takes exactly 2 arguments'
        self.assertRaises(
            TypeError, regex, MH.MHandler)
        self.assertRaises(
            TypeError, regex, MH.MHandler, 'one', 'two')

    def test_non_string_args(self):
        self.assertRaises(TypeError, MH.MHandler, {'a': 'dict'})
        self.assertRaises(TypeError, MH.MHandler, ['an', 'array'])
        self.assertRaises(TypeError, MH.MHandler, True)
        self.assertRaises(TypeError, MH.MHandler, 8)

    def test_good_args(self):
        # Run handler
        new_handler = MH.MHandler(_common.get_conf_file())
        # Check object structure
        self.assertEqual(new_handler.config, _common.get_conf_file())
        self.assertIsInstance(new_handler.push, Notify.MHPush)
        self.assertIsInstance(new_handler, MH.MHandler)
        self.assertIsNone(new_handler.extracted)
        self.assertFalse(new_handler.single_file)

    def test_missing_args(self):
        # Build arguments
        new_handler = MH.MHandler(None)
        # Run Test 
        self.assertEqual(new_handler.config, _common.get_conf_file())
        self.assertIsInstance(new_handler.push, Notify.MHPush)
        self.assertIsInstance(new_handler, MH.MHandler)
        self.assertIsNone(new_handler.extracted)
        self.assertFalse(new_handler.single_file)


class HandlerTestClass(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Dummy args
        self.name = "test-{0}".format(_common.get_test_id())
        self.args = {
            'name': self.name,
            'type': 1,
            'stype': 'TV',
            'single_track': False,
        }
        # Set up handler
        self.handler = MH.MHandler(self.conf)
        self.handler.set_settings(self.args)
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
        self.handler.single_file = sf
        self.handler.general = self.handler.MHSettings(args)
        # Run handler
        self.handler._remove_files(self.tmp_file, skips)
        # Check that file exists
        if self.handler.single_file:
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
        self.handler.single_file = False
        self.handler.general.keep_files = False
        # Run handler
        self.handler._remove_files(self.dir, False)
        # Check that folder was deleted
        self.assertFalse(os.path.exists(self.dir))

    def test_remove_extracted(self):
        self.tmp_file = _common.make_tmp_file()
        # Adjust handler settings
        self.handler.extracted = self.dir
        self.handler.single_file = True
        self.handler.general.keep_files = False
        # Run handler
        self.handler._remove_files(self.tmp_file, False)
        # Check that file was deleted
        self.assertFalse(os.path.exists(self.tmp_file))
        self.assertFalse(os.path.exists(self.dir))


class FileHandlerTests(HandlerTestClass):

    def test_process_files_books(self):
        # Modify args & settings for books
        self.handler.type = 4
        self.handler.stype = 'Audiobooks'
        self.handler.audiobooks.enabled = True
        self.handler.single_file = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.m4b')
        # Run test
        regex = r'Folder for Audiobooks not found: .*Audiobooks'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.tmp_file)

    def test_process_files_single_video(self):
        # Modify args & settings for single video
        self.handler.type = 2
        self.handler.stype = 'Movies'
        self.handler.single_file = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.avi')
        # Run test
        regex = r'Folder for Movies not found: .*Movies'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.tmp_file)

    def test_process_files_single_music(self):
        # Set up beets path
        _find_app(
            self.handler.music.__dict__, {'name': 'Beets', 'exec': 'beet'})
        # Modify args & settings for single music
        self.handler.type = 3
        self.handler.stype = 'Music'
        self.handler.single_file = True
        self.handler.music.enabled = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.mp3')
        # Run test
        regex = r'Unable to match music files: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.tmp_file)

    def test_process_files_folder_video(self):
        # Modify args & settings for single video
        self.handler.type = 2
        self.handler.stype = 'Movies'
        self.handler.single_file = False
        # Make a dummy file in dummy folder
        self.tmp_file = _common.make_tmp_file('.mkv', self.dir)
        # Run test
        regex = r'Folder for Movies not found: .*Movies'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._file_handler, self.dir)

    def test_process_files_folder_music(self):
        # Set up beets path
        _find_app(
            self.handler.music.__dict__, {'name': 'Beets', 'exec': 'beet'})
        # Modify args & settings for single video
        self.handler.type = 3
        self.handler.stype = 'Music'
        self.handler.single_file = False
        self.handler.music.enabled = True
        # Make a dummy file in dummy folder
        self.tmp_file = _common.make_tmp_file('.mp3', self.dir)
        # Run test
        regex = r'Unable to match music files: {0}'.format(self.dir)
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
        regex = r'Skipped files:\n- {0}'.format(self.dir)
        added = self.handler._check_success(self.dir, results)
        self.assertRegexpMatches(added, regex)
        self.assertTrue(os.path.exists(self.dir))

    def test_results_good(self):
        self.handler.single_file = False
        results = ([self.dir], [])
        reg = r'\+ {0}'.format(
            self.dir)
        added = self.handler._check_success(self.dir, results)
        self.assertRegexpMatches(added, reg)
        self.assertFalse(os.path.exists(self.dir))

    def test_results_both(self):
        self.handler.single_file = True
        self.tmp_file = _common.make_tmp_file()
        results = ([self.tmp_file], [self.dir])
        regex = r'\+ {0}\n\nSkipped files:\n- {1}'.format(
            self.tmp_file, self.dir)
        added = self.handler._check_success(self.dir, results)
        self.assertRegexpMatches(added, regex)
        self.assertTrue(os.path.exists(self.dir))


class FindZippedTests(HandlerTestClass):

    def run_process_folder_test(self, ext, filebot=False):
        # Set filebot
        if not filebot:
            delattr(self.handler.tv, 'filebot')
            self.handler.movies.filebot = None
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
            self.handler.tv.filebot = None
            delattr(self.handler.movies, 'filebot')
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

    def test_handle_good_path(self):
        # Run test
        regex = r'No TV files found for: {0}'.format(
            os.path.basename(self.dir))
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler.add_media, media=self.dir, type=1)

    def test_handle_fake_path(self):
        # Run test
        regex = r'File or directory provided for {0} {1}: {2}'.format(
            'media', 'does not exist', '/path/tv/fake')
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler.add_media, '/path/tv/fake')

    def test_main_good_path(self):
        # Set up args
        sys.argv[1:] = [self.dir, '--type', '1']
        # Run test
        regex = r'No TV files found for: {0}'.format(
            os.path.basename(self.dir))
        self.assertRaisesRegexp(
            SystemExit, regex, MH.main)

    def test_main_bad_path(self):
        # Set up args
        sys.argv[1:] = ['/path/tv/fake']
        # Run test
        regex = r'File or directory provided for {0} {1}: {2}'.format(
            'media', 'does not exist', '/path/tv/fake')
        self.assertRaisesRegexp(
            SystemExit, regex, MH.main)

    def test_config_in_args(self):
        # Set up args
        args = {
            'config': os.path.join(self.dir, 'new.yaml'),
            'no_push': True,
            'validated': True
        }
        self.assertEqual(self.handler.config, self.conf)
        self.assertFalse(hasattr(self.handler, 'no_push'))
        self.handler._parse_args_from_dict(self.dir, **args)
        self.assertEqual(self.handler.config, self.conf)
        self.assertTrue(self.handler.no_push)


class AddMediaFilesTests(HandlerTestClass):

    def setUp(self):
        # Call super
        super(AddMediaFilesTests, self).setUp()
        # Get types hash
        self.types_hash = _common.get_types_by_string()
        # Set up beets path
        _find_app(
            self.handler.music.__dict__, {'name': 'Beets', 'exec': 'beet'})

    def test_forced_single_track(self):
        # Modify args & settings for single track
        self.handler.type = 3
        self.handler.stype = 'Music'
        self.handler.single_track = True
        self.handler.single_file = False
        self.handler.music.enabled = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.mp3')
        # Run test
        self.assertFalse(hasattr(self.handler.music, 'single_track'))
        regex = r'Unable to match music files: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._add_media_files, self.tmp_file)
        # Check settings
        self.assertTrue(hasattr(self.handler.music, 'single_track'))

    def test_detected_single_track(self):
        # Modify args & settings for single track
        self.handler.type = 3
        self.handler.stype = 'Music'
        self.handler.single_file = True
        self.handler.music.enabled = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.mp3')
        # Run test
        self.assertFalse(hasattr(self.handler.music, 'single_track'))
        regex = r'Unable to match music files: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._add_media_files, self.tmp_file)
        # Check settings
        self.assertTrue(hasattr(self.handler.music, 'single_track'))

    def test_custom_book_search(self):
        # Search string
        search_str = _common.random_string(10)
        # Modify args & settings for books
        self.handler.type = 4
        self.handler.stype = 'Audiobooks'
        self.handler.query = search_str
        self.handler.single_file = False
        self.handler.audiobooks.enabled = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file('.m4b')
        # Run test
        self.assertFalse(hasattr(self.handler.audiobooks, 'custom_search'))
        regex = r'Folder for Audiobooks not found: .*Audiobooks'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._add_media_files, self.tmp_file)
        # Check settings
        self.assertIs(
            self.handler.audiobooks.custom_search, search_str)

    def run_add_type_test(self, stype, enabled=True):
        # Modify args & settings for books
        self.handler.type = self.types_hash[stype]
        self.handler.stype = stype
        self.handler.single_file = True
        getattr(self.handler, stype.lower()).enabled = enabled
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file()
        # Run test
        regex = r'{0} type is not enabled'.format(stype)
        if enabled:
            regex = r'Folder for {0} not found: .*{1}'.format(stype, stype)
            if stype is 'Music':
                regex = r'Unable to match music files: .*'
        self.assertRaisesRegexp(
            SystemExit, regex, self.handler._add_media_files, self.tmp_file)

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
        delattr(self.handler.tv, 'enabled')
        self.handler.single_file = True
        # Make a dummy file
        self.tmp_file = _common.make_tmp_file()
        # Run first test
        regex1 = r"'MHSettings' object has no attribute 'enabled'"
        self.assertRaisesRegexp(
            AttributeError, regex1,
            self.handler._add_media_files, self.tmp_file)
        # Second test
        self.handler.stype = 'Fake'
        regex2 = r"'MHandler' object has no attribute 'fake'"
        self.assertRaisesRegexp(
            AttributeError, regex2,
            self.handler._add_media_files, self.tmp_file)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
