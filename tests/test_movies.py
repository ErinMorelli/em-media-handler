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

import _common
from _common import unittest
from _common import MHTestSuite

from test_media import MediaObjectTests

import mediahandler.types.movies as Movies


class MoviesMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(MoviesMediaObjectTests, self).setUp()
        # Use Movie settings
        self.settings = _common.get_settings()['Movies']
        self.settings['folder'] = self.folder
        # Make an object
        self.movies = Movies.MHMovie(self.settings, self.push)

    def test_new_movie_object(self):
        expected = os.path.join(self.folder, '{n} ({y})')
        self.assertEqual(self.movies.cmd.db, 'themoviedb')
        self.assertEqual(self.movies.cmd.format, expected)

    def test_movie_output_good(self):
        output = '''Rename movies using [TheMovieDB]
Auto-detect movie from context: [/Downloaded/Movies/Snowpiercer.2013.1080p.BluRay.x264.mp4]
[COPY] Rename [/Downloaded/Movies/Snowpiercer.2013.1080p.BluRay.x264.mp4] to [{0}]
Processed 1 files
Done ?(?????)?
''' .format(os.path.join(self.folder, 'Snowpiercer (2013).mp4'))
        (new_file, skipped) = self.movies._process_output(output, self.tmp_file)
        self.assertEqual(new_file, ['Snowpiercer (2013)'])
        self.assertEqual(skipped, [])

    def test_movie_output_only_skips(self):
        output = '''Rename movies using [TheMovieDB]
Auto-detect movie from context: [/Downloaded/Movies/Snowpiercer.2013.1080p.BluRay.x264.mp4]
Skipped [/Downloaded/Movies/Snowpiercer.2013.1080p.BluRay.x264.mp4] because [{0}/Snowpiercer (2013).mp4] already exists
Processed 1 files
Done ?(?????)?
'''.format(self.folder)
        (new_file, skipped) = self.movies._process_output(output, self.tmp_file)
        self.assertEqual(new_file, [])
        self.assertEqual(
            skipped,
            ['/Downloaded/Movies/Snowpiercer.2013.1080p.BluRay.x264.mp4'])

    def test_movie_output_multi(self):
        output = '''Rename movies using [TheMovieDB]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.a.new.hope.1977.avi]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.return.of.the.jedi.1983.avi]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.the.empire.strikes.back.1980.avi]
Stripping invalid characters from new path: {0}/Star Wars: Episode V - The Empire Strikes Back (1980)
Stripping invalid characters from new path: {0}/Star Wars: Episode VI - Return of the Jedi (1983)
Stripping invalid characters from new path: {0}/Star Wars: Episode IV - A New Hope (1977)
[COPY] Rename [/Downloaded/Star Wars/star.wars.the.empire.strikes.back.1980.avi] to [{0}/Star Wars Episode V - The Empire Strikes Back (1980).avi]
[COPY] Rename [/Downloaded/Star Wars/star.wars.return.of.the.jedi.1983.avi] to [{0}/Star Wars Episode VI - Return of the Jedi (1983).avi]
[COPY] Rename [/Downloaded/Star Wars/star.wars.a.new.hope.1977.avi] to [{0}/Star Wars Episode IV - A New Hope (1977).avi]
Processed 3 files
Done ?(?????)?
'''.format(self.folder)
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
        output = '''Rename movies using [TheMovieDB]
Auto-detect movie from context: [/Downloaded/Movies/Fake.Movie.avi]
[COPY] Rename [/Downloaded/Movies/Fake.Movie.avi] to [/Movies/Fake Movie.avi]
[COPY] Rename [/Downloaded/Movies/Another.Fake.Movie.avi] to [/Movies/Another.Fake.Movie.avi]
Processed 1 files
Done ?(?????)?
'''
        regex = r'Unable to match movie files: {0}. {1}'.format(
            '/Movies/Fake Movie', '/Movies/Another.Fake.Movie')
        self.assertRaisesRegexp(
            SystemExit, regex,
            self.movies._process_output, output, self.tmp_file)

    def test_movie_output_skips(self):
        output = '''Rename movies using [TheMovieDB]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.a.new.hope.1977.avi]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.attack.of.the.clones.2002.avi]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.return.of.the.jedi.1983.avi]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.revenge.of.the.sith.2005.avi]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.the.empire.strikes.back.1980.avi]
Auto-detect movie from context: [/Downloaded/Star Wars/star.wars.the.phantom.menace.1999.avi]
Stripping invalid characters from new path: {0}/Star Wars: Episode V - The Empire Strikes Back (1980)
Stripping invalid characters from new path: {0}/Star Wars: Episode VI - Return of the Jedi (1983)
Stripping invalid characters from new path: {0}/Star Wars: Episode I - The Phantom Menace (1999)
Stripping invalid characters from new path: {0}/Star Wars: Episode II - Attack of the Clones (2002)
Stripping invalid characters from new path: {0}/Star Wars: Episode III - Revenge of the Sith (2005)
Stripping invalid characters from new path: {0}/Star Wars: Episode IV - A New Hope (1977)
Skipped [/Downloaded/Star Wars/star.wars.the.empire.strikes.back.1980.avi] because [{0}/Star Wars Episode V - The Empire Strikes Back (1980).avi] already exists
Skipped [/Downloaded/Star Wars/star.wars.return.of.the.jedi.1983.avi] because [{0}/Star Wars Episode VI - Return of the Jedi (1983).avi] already exists
[COPY] Rename [/Downloaded/Star Wars/star.wars.the.phantom.menace.1999.avi] to [{0}/Star Wars Episode I - The Phantom Menace (1999).avi]
[COPY] Rename [/Downloaded/Star Wars/star.wars.attack.of.the.clones.2002.avi] to [{0}/Star Wars Episode II - Attack of the Clones (2002).avi]
[COPY] Rename [/Downloaded/Star Wars/star.wars.revenge.of.the.sith.2005.avi] to [{0}/Star Wars Episode III - Revenge of the Sith (2005).avi]
Skipped [/Downloaded/Star Wars/star.wars.a.new.hope.1977.avi] because [{0}/Star Wars Episode IV - A New Hope (1977).avi] already exists
Processed 6 files
Done ?(?????)?
'''.format(self.folder)
        (new_files, skipped) = self.movies._process_output(
            output, self.tmp_file)
        new_expected = [
            'Star Wars Episode I - The Phantom Menace (1999)',
            'Star Wars Episode II - Attack of the Clones (2002)',
            'Star Wars Episode III - Revenge of the Sith (2005)',
        ]
        skip_expected = [
            '/Downloaded/Star Wars/star.wars.the.empire.strikes.back.1980.avi',
            '/Downloaded/Star Wars/star.wars.return.of.the.jedi.1983.avi',
            '/Downloaded/Star Wars/star.wars.a.new.hope.1977.avi'
        ]
        self.assertEqual(new_files, new_expected)
        self.assertEqual(skipped, skip_expected)


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
