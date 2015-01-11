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

import _common
from _common import unittest

from test_media import MediaObjectTests

import mediahandler.types.movies as Movies


class MoviesMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(MoviesMediaObjectTests, self).setUp()
        # Make an object
        self.movies = Movies.Movie(self.settings, self.push)

    def test_new_movie_object(self):
        expected = '%s/{n} ({y})' % self.folder
        self.assertEqual(self.movies.filebot['db'], 'themoviedb')
        self.assertEqual(self.movies.filebot['format'], expected)

    def test_movie_output_good(self):
        output = '''Rename movies using [TheMovieDB]
Auto-detect movie from context: [/Downloaded/Movies/Snowpiercer.2013.1080p.BluRay.x264.mp4]
[COPY] Rename [/Downloaded/Movies/Snowpiercer.2013.1080p.BluRay.x264.mp4] to [%s/Snowpiercer (2013).mp4]
Processed 1 files
Done ?(?????)?
''' % self.folder
        (new_file, skipped) = self.movies.process_output(output, self.tmp_file)
        self.assertEqual(new_file, 'Snowpiercer (2013)')
        self.assertFalse(skipped)

    def test_movie_output_skipped(self):
        output = '''Rename movies using [TheMovieDB]
Auto-detect movie from context: [/Downloaded/Movies/Fake.Movie.avi]
[COPY] Rename [/Downloaded/Movies/Fake.Movie.avi] to [/Movies/Fake Movie.avi]
Processed 1 files
Done ?(?????)?
'''
        regex = r'Unable to match movie: /Movies/Fake Movie\.avi'
        self.assertRaisesRegexp(
            SystemExit, regex, self.movies.process_output, output, self.tmp_file)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)