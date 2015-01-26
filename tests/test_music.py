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
from _common import MHTestSuite

from test_media import MediaObjectTests

from mediahandler.util.config import _find_app
import mediahandler.types.music as Music


class MusicMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(MusicMediaObjectTests, self).setUp()
        # Get music settings
        self.settings = _common.get_settings()['Music']
        self.settings['single_track'] = False
        # Set up beets path
        _find_app(self.settings, {'name': 'Beets', 'exec': 'beet'})
        # Set up music object
        self.tracks = Music.MHMusic(self.settings, self.push)

    def test_new_music_object(self):
        expected = r"(Tagging|To)\:\n\s{1,4}(.*)\nURL\:\n\s{1,4}(.*)\n"
        self.assertEqual(self.tracks.query.tags, '-ql')
        self.assertEqual(self.tracks.query.added, expected)

    def test_new_music_single(self):
        self.settings['single_track'] = True
        self.tracks = Music.MHMusic(self.settings, self.push)
        # Check results
        expected = r"(Tagging track)\:\s(.*)\nURL\:\n\s{1,4}(.*)\n"
        self.assertEqual(self.tracks.query.tags, '-sql')
        self.assertEqual(self.tracks.query.added, expected)

    def test_music_add_log(self):
        # Make dummy logfile
        name = 'test-{0}.log'.format(_common.get_test_id())
        folder = os.path.join(os.path.dirname(self.conf), 'tmpl')
        log_file = os.path.join(folder, name)
        self.tracks.log_file = log_file
        # Run tests
        regex = r'Unable to match music files: {0}'.format(self.tmp_file)
        self.assertRaisesRegexp(
            SystemExit, regex, self.tracks.add, self.tmp_file)
        self.assertTrue(os.path.exists(folder))
        # Clean up
        shutil.rmtree(folder)

    def test_music_output_good(self):
        output = '''
/Downloaded/Music/Alt-J - This Is All Yours (2014) CD RIP [MP3 @ 320 KBPS] (13 items)
Correcting tags from:
    Alt-J - This Is All Yours
To:
    alt-J - This Is All Yours
URL:
    http://musicbrainz.org/release/e6f60da3-1d37-4aba-a309-6e65b84ffe66
(Similarity: 96.9%) (tracks) (CD, 2014, Infectious Records)

/Downloaded/Music/Eisley - Discographie (2002-2012)/Eisley - (2005) Room Noises ALBUM (13 items)
Tagging:
    Eisley - Room Noises
URL:
    http://musicbrainz.org/release/4186b65f-c36d-4dac-82d3-221d3f8c7925
(Similarity: 100.0%) (2005, US)
'''
        (new_file, skipped) = self.tracks._process_output(output, self.tmp_file)
        expected = ['alt-J - This Is All Yours', 'Eisley - Room Noises']
        self.assertEqual(new_file, expected)
        self.assertEqual(skipped, [])

    def test_music_output_single_good(self):
        # Single file
        self.settings['single_track'] = True
        self.tracks = Music.MHMusic(self.settings, self.push)
        output = '''
/Downloaded/Music/Taylor Swift - Blank Space {2014-Single}/02 Blank Space.mp3
Tagging track: Taylor Swift - Blank Space
URL:
    http://musicbrainz.org/recording/c3fe7791-0a91-4f0a-a89b-b056f38d3cde
(Similarity: 100.0%)
'''
        (new_file, skipped) = self.tracks._process_output(output, self.tmp_file)
        self.assertEqual(new_file, ['Taylor Swift - Blank Space'])
        self.assertEqual(skipped, [])

    def test_music_output_skipped(self):
        output = '''
/Downloaded/Music/Eisley - Discographie (2002-2012)/Eisley - (2003) Marvelous Things EP (1 items)
Skipping.

/Downloaded/Music/Eisley - Discographie (2002-2012)/Eisley - (2005) Room Noises ALBUM (13 items)
Tagging:
    Eisley - Room Noises
URL:
    http://musicbrainz.org/release/4186b65f-c36d-4dac-82d3-221d3f8c7925
(Similarity: 100.0%) (2005, US)

/Downloaded/Music/Eisley - Discographie (2002-2012)/Eisley - (2009) Fire Kite EP (1 items)
Skipping.
'''
        (new_file, skipped) = self.tracks._process_output(output, self.tmp_file)
        new_expected = ['Eisley - Room Noises']
        skip_expected = [
            'Eisley - (2003) Marvelous Things EP',
            'Eisley - (2009) Fire Kite EP',
        ]
        self.assertEqual(new_file, new_expected)
        self.assertEqual(skipped, skip_expected)

    def test_music_output_single_skipped(self):
        # Single file
        self.settings['single_track'] = True
        self.tracks = Music.MHMusic(self.settings, self.push)
        output = '''
/Downloaded/Music/Taylor Swift - Blank Space {2014-Single} (1 items)
Skipping.
'''
        (new_file, skipped) = self.tracks._process_output(output, self.tmp_file)
        expected = ['Taylor Swift - Blank Space {2014-Single}']
        self.assertEqual(new_file, [])
        self.assertEqual(skipped, expected)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
