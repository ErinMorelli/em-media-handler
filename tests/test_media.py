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
from re import search

import _common
from _common import unittest
from _common import tempfile
from _common import MHTestSuite

import mediahandler.types as Types
import mediahandler.util.notify as Notify


class MediaObjectTests(unittest.TestCase):

    def setUp(self):
        # Conf
        self.conf = _common.get_conf_file()
        # Set up push object
        self.push = Notify.MHPush({
            'enabled': False,
            'notify_name': '',
            'pushover':{
                'api_key': _common.random_string(),
                'user_key': _common.random_string(),
            },
        }, True)
        # Make temp stuff
        self.folder = tempfile.mkdtemp(
            dir=os.path.dirname(self.conf))
        self.tmp_file = _common.make_tmp_file('.avi')
        # Build base settings
        self.settings = _common.get_settings()['TV']
        self.settings['folder'] = self.folder

    def tearDown(self):
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        if os.path.exists(self.tmp_file):
            os.unlink(self.tmp_file)


class BaseMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call super
        super(BaseMediaObjectTests, self).setUp()
        # Make an object
        self.media = Types.MHMediaType(self.settings, self.push)
        if not search('test_new_media_object', self.id()):
            self.media._video_settings()

    def tearDown(self):
        # Call super
        super(BaseMediaObjectTests, self).tearDown()
        # Remove extra
        if self.settings['log_file'] is not None:
            if os.path.exists(self.settings['log_file']):
                os.unlink(self.settings['log_file'])

    def test_new_media_object(self):
        # Check results
        self.assertEqual(self.media.type, 'mediatype')
        self.assertEqual(self.media.ptype, 'Media Type')
        self.assertEqual(self.media.dst_path, self.folder)
        self.assertIsInstance(self.media.push, Notify.MHPush)
        self.assertFalse(hasattr(self.media, 'cmd'))

    def test_missing_filebot(self):
        # Make new object
        self.media = Types.MHMediaType(self.settings, self.push)
        # Remove filebot
        self.media.filebot = None
        # Run test
        regex = r'Filebot required to process Media Type files'
        self.assertRaisesRegexp(
            SystemExit, regex, self.media._video_settings)

    def test_new_media_bad_folder(self):
        # Dummy folder path
        self.settings['folder'] = os.path.join('path', 'to', 'fake')
        # Run test 1
        regex1 = r'Folder for Media Type not found: {0}'.format(
            self.settings['folder'])
        self.assertRaisesRegexp(
            SystemExit, regex1, Types.MHMediaType, self.settings, self.push)
        # Run test 2
        regex2 = r'Folder for Media Type not found: .*Media'
        self.assertRaisesRegexp(
            SystemExit, regex2, Types.MHMediaType, {}, self.push)

    def test_media_add(self):
        regex = r'Unable to match mediatype files: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.media.add, self.tmp_file)

    def test_media_add_logging(self):
        self.media.log_file = os.path.join(self.folder, 'media.log')
        regex = r'Unable to match mediatype files: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.media.add, self.tmp_file)

    def test_process_output_good(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [@midnight, At Midnight]
Fetching episode data for [@midnight]
Fetching episode data for [Midnight Caller]
[COPY] Rename [/Downloaded/TV/At.Midnight.2015.01.08.720p.HDTV.x264.mkv] to [/media/TV/@midnight/Season 2015/@midnight.S2015E01.mkv]
Processed 1 files
Done ?(?????)?
'''
        (new_file, skipped) = self.media._process_output(output, self.tmp_file)
        expected = ['/media/TV/@midnight/Season 2015/@midnight.S2015E01']
        self.assertEqual(skipped, [])
        self.assertEqual(new_file, expected)

    def test_process_output_skipped(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [Downton Abbey]
Fetching episode data for [Downton Abbey]
Skipped [/Downloaded/TV/Downton.Abbey.5x03.720p.HDTV.x264.mkv] because [/Media/TV/Downton Abbey/Season 5/Downton.Abbey.S05E03.mkv] already exists
Processed 1 files
Done ?(?????)?
'''
        (new_file, skipped) = self.media._process_output(output, self.tmp_file)
        expected = ['/Downloaded/TV/Downton.Abbey.5x03.720p.HDTV.x264.mkv']
        self.assertEqual(skipped, expected)
        self.assertEqual(new_file, [])

    def test_remove_bad_files(self):
        # Add files to folder
        bad_folder = tempfile.mkdtemp(dir=self.folder)
        file1 = _common.make_tmp_file('.nfo', self.folder)
        file2 = _common.make_tmp_file('.srt', self.folder)
        file3 = _common.make_tmp_file('.txt', bad_folder)
        # Run test
        self.media._remove_bad_files(self.folder)
        # Check results
        self.assertFalse(os.path.exists(file1))
        self.assertFalse(os.path.exists(file2))
        self.assertFalse(os.path.exists(file3))
        self.assertTrue(os.path.exists(bad_folder))
        self.assertTrue(os.path.exists(self.tmp_file))


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
