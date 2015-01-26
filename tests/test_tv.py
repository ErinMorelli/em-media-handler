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

from _common import unittest
from _common import MHTestSuite

from test_media import MediaObjectTests

import mediahandler.types.tv as TV


class TVMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(TVMediaObjectTests, self).setUp()
        # Make an object
        self.episode = TV.MHTv(self.settings, self.push)

    def test_new_tv_object(self):
        form = os.path.join(
            "{n}", "Season {s}", "{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}")
        expected = os.path.join(self.folder, form)
        self.assertEqual(self.episode.cmd.db, 'thetvdb')
        self.assertEqual(self.episode.cmd.format, expected)

    def test_tv_output_good(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [Greys Anatomy]
Fetching episode data for [Grey's Anatomy]
[COPY] Rename [/Downloaded/TV/Greys.Anatomy.S10E24.720p.HDTV.X264.mkv] to [{0}]
Processed 1 files
Done ?(?????)?
'''.format(
            os.path.join(
                self.folder, "Grey's Anatomy",
                "Season 10", "Grey's.Anatomy.S10E24.mkv"))
        (new_file, skipped) = self.episode._process_output(
            output, self.tmp_file)
        expected = ["Grey's Anatomy (Season 10, Episode 24)"]
        self.assertEqual(new_file, expected)
        self.assertEqual(skipped, [])

    def test_tv_output_good_multi(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [greys anatomy]
Fetching episode data for [Grey's Anatomy]
Skipped [/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e01.avi] because [{0}/Grey's Anatomy/Season 1/Grey's.Anatomy.S01E01.avi] already exists
Skipped [/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e02.avi] because [{0}/Grey's Anatomy/Season 1/Grey's.Anatomy.S01E02.avi] already exists
Skipped [/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e03.avi] because [{0}/Grey's Anatomy/Season 1/Grey's.Anatomy.S01E03.avi] already exists
[COPY] Rename [/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e04.avi] to [{0}/Grey's Anatomy/Season 1/Grey's.Anatomy.S01E04.avi]
[COPY] Rename [/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e05.avi] to [{0}/Grey's Anatomy/Season 1/Grey's.Anatomy.S01E05.avi]
[COPY] Rename [/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e06.avi] to [{0}/Grey's Anatomy/Season 1/Grey's.Anatomy.S01E06.avi]
Processed 6 files
Done ?(?????)?
'''.format(self.folder)
        (new_files, skipped) = self.episode._process_output(
            output, self.tmp_file)
        new_expected = [
            "Grey's Anatomy (Season 1, Episode 4)",
            "Grey's Anatomy (Season 1, Episode 5)",
            "Grey's Anatomy (Season 1, Episode 6)",
        ]
        skip_expected = [
            "/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e01.avi",
            "/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e02.avi",
            "/Downloaded/Grey's Anatomy Season 1/greys.anatomy.s01e03.avi",
        ]
        self.assertEqual(new_files, new_expected)
        self.assertEqual(skipped, skip_expected)

    def test_tv_output_no_match(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [Fake Show]
Fetching episode data for [Fake Show]
[COPY] Rename [/Downloaded/TV/Fake.Show.S01E01.mkv] to [/TV/Fake Show/Fake.Show.S01E01.mkv]
[COPY] Rename [/Downloaded/TV/Fake.Show.S01E02.mkv] to [/TV/Fake Show/Fake.Show.S01E02.mkv]
Processed 1 files
Done ?(?????)?
'''
        regex = r'Unable to match tv files: {0}, {1}'.format(
            '/TV/Fake Show/Fake.Show.S01E01', '/TV/Fake Show/Fake.Show.S01E02')
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.episode._process_output, output, self.tmp_file)

    def test_tv_output_skipped(self):
        output = '''Rename episodes using [TheTVDB]
Auto-detected query: [greys anatomy]
Fetching episode data for [Grey's Anatomy]
Skipped [/Downloaded/Archer Season 3/Archer.s03e01.avi] because [{0}/Archer/Season 3/Archer.S03E01.avi] already exists
Skipped [/Downloaded/Archer Season 3/Archer.s03e02.avi] because [{0}/Archer/Season 3/Archer.S03E02.avi] already exists
Skipped [/Downloaded/Archer Season 3/Archer.s03e03.avi] because [{0}/Archer/Season 3/Archer.S03E03.avi] already exists
[COPY] Rename [/Downloaded/Archer Season 3/Archer.s03e03.nfo] to [{0}/Archer/Season 3/Archer.S03E03.nfo]
Processed 3 files
Done ?(?????)?
'''.format(self.folder)
        (new_files, skipped) = self.episode._process_output(
            output, self.tmp_file)
        expected = [
            "/Downloaded/Archer Season 3/Archer.s03e01.avi",
            "/Downloaded/Archer Season 3/Archer.s03e02.avi",
            "/Downloaded/Archer Season 3/Archer.s03e03.avi",
        ]
        self.assertEqual(new_files, [])
        self.assertEqual(skipped, expected)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
