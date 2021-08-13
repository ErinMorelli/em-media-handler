#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014-2021 Erin Morelli
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
"""Initialize module"""

import os
from re import escape

from tests.common import unittest
from tests.common import MHTestSuite

from tests.test_media import MediaObjectTests

import mediahandler.types.tv as TV


class TVMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(TVMediaObjectTests, self).setUp()
        # Make an object
        self.episode = TV.MHTv(self.settings, self.push)

    def test_new_tv_object(self):
        form = os.path.sep.join(
            ['{n}', 'Season {s}', '{n.space(".")}.{"S"+s.pad(2)}E{e.pad(2)}'])
        expected = os.path.join(self.folder, form)
        self.assertEqual(self.episode.cmd.db, 'thetvdb')
        self.assertEqual(self.episode.cmd.format, expected)

    def test_tv_output_good(self):
        title = "Grey's Anatomy"
        fro = os.path.join(os.path.sep, 'Downloaded', 'TV', 'Greys.Anatomy.S10E24.720p.HDTV.X264.mkv')
        to = os.path.join(os.path.sep, self.folder, title, "Season 10", "Grey's.Anatomy.S10E24.mkv")
        output = """Rename episodes using [TheTVDB]
Auto-detected query: [{title}]
Fetching episode data for [{title}]
[COPY] Rename [{fro}] to [{to}]
Processed 1 files
Done ?(?????)?
""".format(fro=fro, to=to, title=title)
        (new_file, skipped) = self.episode._process_output(
            output, self.tmp_file)
        expected = [f"{title} (Season 10, Episode 24)"]
        self.assertEqual(new_file, expected)
        self.assertEqual(skipped, [])

    def test_tv_output_good_multi(self):
        title = "Grey's Anatomy"
        season = "Season 1"
        one = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "greys.anatomy.s01e01.avi")
        one_to = os.path.join(os.path.sep, self.folder, title, season, "Grey's.Anatomy.S01E01.avi")
        two = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "greys.anatomy.s01e02.avi")
        two_to = os.path.join(os.path.sep, self.folder, title, season, "Grey's.Anatomy.S01E02.avi")
        three = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "greys.anatomy.s01e03.avi")
        three_to = os.path.join(os.path.sep, self.folder, title, season, "Grey's.Anatomy.S01E03.avi")
        four = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "greys.anatomy.s01e04.avi")
        four_to = os.path.join(os.path.sep, self.folder, title, season, "Grey's.Anatomy.S01E04.avi")
        five = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "greys.anatomy.s01e05.avi")
        five_to = os.path.join(os.path.sep, self.folder, title, season, "Grey's.Anatomy.S01E05.avi")
        six = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "greys.anatomy.s01e06.avi")
        six_to = os.path.join(os.path.sep, self.folder, title, season, "Grey's.Anatomy.S01E06.avi")
        output = """Rename episodes using [TheTVDB]
Auto-detected query: [greys anatomy]
Fetching episode data for [{title}]
Skipped [{one}] because [{one_to}] already exists
Skipped [{two}] because [{two_to}] already exists
Skipped [{three}] because [{three_to}] already exists
[COPY] Rename [{four}] to [{four_to}]
[COPY] Rename [{five}] to [{five_to}]
[COPY] Rename [{six}] to [{six_to}]
Processed 6 files
Done ?(?????)?
""".format(one=one, one_to=one_to, two=two, two_to=two_to, three=three,
           three_to=three_to, four=four, four_to=four_to, five=five,
           five_to=five_to, six=six, six_to=six_to, title=title)
        (new_files, skipped) = self.episode._process_output(
            output, self.tmp_file)
        new_expected = [
            f"{title} (Season 1, Episode 4)",
            f"{title} (Season 1, Episode 5)",
            f"{title} (Season 1, Episode 6)",
        ]
        skip_expected = [os.path.basename(one), os.path.basename(two), os.path.basename(three)]
        self.assertEqual(new_files, new_expected)
        self.assertEqual(skipped, skip_expected)

    def test_tv_output_no_match(self):
        title = "Fake Show"
        one = os.path.join(os.path.sep, "Downloaded", "TV", "Fake.Show.S01E01.mkv")
        one_to = os.path.join(os.path.sep, "TV", title, "Fake.Show.S01E01.mkv")
        two = os.path.join(os.path.sep, "Downloaded", "TV", "Fake.Show.S01E02.mkv")
        two_to = os.path.join(os.path.sep, "TV", title, "Fake.Show.S01E02.mkv")
        output = """Rename episodes using [TheTVDB]
Auto-detected query: [{title}]
Fetching episode data for [{title}]
[COPY] Rename [{one}] to [{one_to}]
[COPY] Rename [{two}] to [{two_to}]
Processed 1 files
Done ?(?????)?
""".format(one=one, one_to=one_to, two=two, two_to=two_to, title=title)
        regex = r'.*Unable to match tv files: {0}, {1}'.format(
            escape(one_to.replace('.mkv', '')),
            escape(two_to.replace('.mkv', '')))
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.episode._process_output, output, self.tmp_file)

    def test_tv_output_skipped(self):
        title = "Archer"
        season = "Season 3"
        one = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "Archer.s03e01.avi")
        one_to = os.path.join(os.path.sep, self.folder, title, season, "Archer.S03E01.avi")
        two = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "Archer.s03e02.avi")
        two_to = os.path.join(os.path.sep, self.folder, title, season, "Archer.S03E02.avi")
        three = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "Archer.s03e03.avi")
        three_to = os.path.join(os.path.sep, self.folder, title, season, "Archer.S03E03.avi")
        four = os.path.join(os.path.sep, "Downloaded", f"{title} {season}", "Archer.s03e03.nfo")
        four_to = os.path.join(os.path.sep, self.folder, title, season, "Archer.S03E03.nfo")
        output = """Rename episodes using [TheTVDB]
Auto-detected query: [greys anatomy]
Fetching episode data for [Grey's Anatomy]
Skipped [{one}] because [{one_to}] already exists
Skipped [{two}] because [{two_to}] already exists
Skipped [{three}] because [{three_to}] already exists
[COPY] Rename [{four}] to [{four_to}]
Processed 3 files
Done ?(?????)?
""".format(one=one, one_to=one_to, two=two, two_to=two_to,
           three=three, three_to=three_to, four=four, four_to=four_to)
        (new_files, skipped) = self.episode._process_output(
            output, self.tmp_file)
        expected = [os.path.basename(one), os.path.basename(two), os.path.basename(three)]
        self.assertEqual(new_files, [])
        self.assertEqual(skipped, expected)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
