#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is a part of EM Media Handler Testing Module
# Copyright (c) 2014-2019 Erin Morelli
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

import tests.common as common
from tests.common import unittest
from tests.common import MHTestSuite

from tests.test_media import MediaObjectTests

import mediahandler.types.movies as Movies


class MoviesMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(MoviesMediaObjectTests, self).setUp()
        # Use Movie settings
        self.settings = common.get_settings()['Movies']
        self.settings['folder'] = self.folder
        # Make an object
        self.movies = Movies.MHMovie(self.settings, self.push)

    def test_new_movie_object(self):
        expected = os.path.join(self.folder, '{n} ({y})')
        self.assertEqual(self.movies.cmd.db, 'themoviedb')
        self.assertEqual(self.movies.cmd.format, expected)

    def test_movie_output_good(self):
        fro = os.path.join(os.path.sep, 'Downloaded', 'Movies', 'Snowpiercer.2013.1080p.BluRay.x264.mp4')
        output = """Rename movies using [TheMovieDB]
Auto-detect movie from context: [{fro}]
[COPY] Rename [{fro}] to [{to}]
Processed 1 files
Done ?(?????)?
""" .format(fro=fro, to=os.path.join(os.path.sep, self.folder, 'Snowpiercer (2013).mp4'))
        (new_file, skipped) = self.movies._process_output(output, self.tmp_file)
        self.assertEqual(new_file, ['Snowpiercer (2013)'])
        self.assertEqual(skipped, [])

    def test_movie_output_only_skips(self):
        one = os.path.join(os.path.sep, 'Downloaded', 'Movies', 'Snowpiercer.2013.1080p.BluRay.x264.mp4')
        output = """Rename movies using [TheMovieDB]
Auto-detect movie from context: [{one}]
Skipped [{one}] because [{f}Snowpiercer (2013).mp4] already exists
Processed 1 files
Done ?(?????)?
""".format(one=one, f=os.path.join(os.path.sep, self.folder, ''))
        (new_file, skipped) = self.movies._process_output(output, self.tmp_file)
        self.assertEqual(new_file, [])
        self.assertEqual(skipped, [os.path.basename(one)])

    def test_movie_output_multi(self):
        one = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.a.new.hope.1977.avi')
        two = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.return.of.the.jedi.1983.avi')
        three = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.the.empire.strikes.back.1980.avi')
        output = """Rename movies using [TheMovieDB]
Auto-detect movie from context: [{one}]
Auto-detect movie from context: [{two}]
Auto-detect movie from context: [{three}]
Stripping invalid characters from new path: {f}Star Wars: Episode V - The Empire Strikes Back (1980)
Stripping invalid characters from new path: {f}Star Wars: Episode VI - Return of the Jedi (1983)
Stripping invalid characters from new path: {f}Star Wars: Episode IV - A New Hope (1977)
[COPY] Rename [{one}] to [{f}Star Wars Episode V - The Empire Strikes Back (1980).avi]
[COPY] Rename [{two}] to [{f}Star Wars Episode VI - Return of the Jedi (1983).avi]
[COPY] Rename [{three}] to [{f}Star Wars Episode IV - A New Hope (1977).avi]
Processed 3 files
Done ?(?????)?
""".format(one=one, two=two, three=three, f=os.path.join(os.path.sep, self.folder, ''))
        (new_files, skipped) = self.movies._process_output(
            output, self.tmp_file)
        expected = [
            'Star Wars Episode V - The Empire Strikes Back (1980)',
            'Star Wars Episode VI - Return of the Jedi (1983)',
            'Star Wars Episode IV - A New Hope (1977)',
        ]
        self.assertEqual(new_files, expected)
        self.assertEqual(skipped, [])

    def test_movie_output_no_match(self):
        one = os.path.join(os.path.sep, 'Downloaded', 'Movies', 'Fake.Movie.avi')
        two = os.path.join(os.path.sep, 'Downloaded', 'Movies', 'Another.Fake.Movie.avi')
        output = """Rename movies using [TheMovieDB]
Auto-detect movie from context: [{one}]
[COPY] Rename [{one}] to [{f}Fake Movie.avi]
[COPY] Rename [{two}] to [{f}Another.Fake.Movie.avi]
Processed 1 files
Done ?(?????)?
""".format(one=one, two=two, f=os.path.join(os.path.sep, 'Movies', ''))
        regex = r'Unable to match movie files: {f}{one}, {f}{two}'.format(
            f=escape(os.path.join(os.path.sep, 'Movies', '')),
            one='Fake Movie', two='Another.Fake.Movie')
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.movies._process_output, output, self.tmp_file)

    def test_movie_output_skips(self):
        one = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.a.new.hope.1977.avi')
        two = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.attack.of.the.clones.2002.avi')
        three = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.return.of.the.jedi.1983.avi')
        four = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.revenge.of.the.sith.2005.avi')
        five = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.the.empire.strikes.back.1980.avi')
        six = os.path.join(os.path.sep, 'Downloaded', 'Star Wars', 'star.wars.the.phantom.menace.1999.avi')
        output = """Rename movies using [TheMovieDB]
Auto-detect movie from context: [{one}]
Auto-detect movie from context: [{two}]
Auto-detect movie from context: [{three}]
Auto-detect movie from context: [{four}]
Auto-detect movie from context: [{five}]
Auto-detect movie from context: [{six}]
Stripping invalid characters from new path: {f}Star Wars: Episode V - The Empire Strikes Back (1980)
Stripping invalid characters from new path: {f}Star Wars: Episode VI - Return of the Jedi (1983)
Stripping invalid characters from new path: {f}Star Wars: Episode I - The Phantom Menace (1999)
Stripping invalid characters from new path: {f}Star Wars: Episode II - Attack of the Clones (2002)
Stripping invalid characters from new path: {f}Star Wars: Episode III - Revenge of the Sith (2005)
Stripping invalid characters from new path: {f}Star Wars: Episode IV - A New Hope (1977)
Skipped [{five}] because [{f}Star Wars Episode V - The Empire Strikes Back (1980).avi] already exists
Skipped [{three}] because [{f}Star Wars Episode VI - Return of the Jedi (1983).avi] already exists
[COPY] Rename [{six}] to [{f}Star Wars Episode I - The Phantom Menace (1999).avi]
[COPY] Rename [{two}] to [{f}Star Wars Episode II - Attack of the Clones (2002).avi]
[COPY] Rename [{four}] to [{f}Star Wars Episode III - Revenge of the Sith (2005).avi]
Skipped [{one}] because [{f}Star Wars Episode IV - A New Hope (1977).avi] already exists
Processed 6 files
Done ?(?????)?
""".format(one=one, two=two, three=three, four=four, five=five, six=six,
           f=os.path.join(os.path.sep, self.folder, ''))
        (new_files, skipped) = self.movies._process_output(
            output, self.tmp_file)
        new_expected = [
            'Star Wars Episode I - The Phantom Menace (1999)',
            'Star Wars Episode II - Attack of the Clones (2002)',
            'Star Wars Episode III - Revenge of the Sith (2005)',
        ]
        skip_expected = [os.path.basename(five), os.path.basename(three), os.path.basename(one)]
        self.assertEqual(new_files, new_expected)
        self.assertEqual(skipped, skip_expected)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
