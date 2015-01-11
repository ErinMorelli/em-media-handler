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

import _common
from _common import unittest

from test_media import MediaObjectTests

import mediahandler.types.tv as TV


class TVMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(TVMediaObjectTests, self).setUp()
        # Make an object
        self.episode = TV.Episode(self.settings, self.push)

    def test_new_tv_object(self):
        form = "/{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}" 
        expected = self.folder + form
        self.assertEqual(self.episode.filebot['db'], 'thetvdb')
        self.assertEqual(self.episode.filebot['format'], expected)

    def test_tv_output_good(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [Greys Anatomy]
Fetching episode data for [Grey's Anatomy]
[COPY] Rename [/Downloaded/TV/Greys.Anatomy.S10E24.720p.HDTV.X264.mkv] to [%s/Grey's Anatomy/Season 10/Grey's.Anatomy.S10E24.mkv]
Processed 1 files
Done ?(?????)?
''' % self.folder
        (new_file, skipped) = self.episode.process_output(output, self.tmp_file)
        expected = "Grey's Anatomy (Season 10, Episode 24)"
        self.assertEqual(new_file, expected)
        self.assertFalse(skipped)

    def test_tv_output_skipped(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [Fake Show]
Fetching episode data for [Fake Show]
[COPY] Rename [/Downloaded/TV/Fake.Show.S01E01.mkv] to [/TV/Fake Show/Fake.Show.S01E01.mkv]
Processed 1 files
Done ?(?????)?
'''
        regex = r'Unable to match episode: /TV/Fake Show/Fake.Show.S01E01.mkv'
        self.assertRaisesRegexp(
            SystemExit, regex, self.episode.process_output, output, self.tmp_file)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)