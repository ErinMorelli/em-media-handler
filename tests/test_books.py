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
import shutil
from mutagen.mp3 import MP3

import _common
from _common import unittest

from test_media import MediaObjectTests

import mediahandler.types.audiobooks as Books


class BookMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(BookMediaObjectTests, self).setUp()
        # Book-specific settings
        self.settings['api_key'] = _common.get_google_api()
        self.settings['chapter_length'] = None
        self.settings['make_chapters'] = False
        # Make an object
        self.book = Books.Book(self.settings, self.push)

    def test_bad_google_api(self):
        self.settings['api_key'] = None
        regex = r'Google Books API key not found'
        self.assertRaisesRegexp(
            Warning, regex, Books.Book, self.settings, self.push)

    def test_custom_chapter_length(self):
        self.settings['chapter_length'] = 10
        self.book = Books.Book(self.settings, self.push)
        self.assertEqual(self.book.handler['max_length'], 36000)

    def test_custom_search_string(self):
        search = 'Gone Girl Gillian Flynn'
        self.settings['custom_search'] = search
        self.book = Books.Book(self.settings, self.push)
        self.assertEqual(self.book.handler['custom_search'], search)


class BookCleanStringTests(BookMediaObjectTests):

    def test_blacklist_string(self):
        string = '%s/Yes Please iTunes Audiobook Unabridged' % self.folder
        expected = 'Yes Please'
        self.assertEqual(self.book._clean_string(string), expected)

    def test_bracket_string(self):
        string = '%s/The Lovely Bones [A Novel] (Mp3) {TKP}' % self.folder
        expected = 'The Lovely Bones'
        self.assertEqual(self.book._clean_string(string), expected)

    def test_non_alphanum_string(self):
        string = '%s/Jar City - A Novel - 2000' % self.folder
        expected = 'Jar City A Novel'
        self.assertEqual(self.book._clean_string(string), expected)

    def test_whitespace_string(self):
        string = '%s/The   Goldfinch  ' % self.folder
        expected = 'The Goldfinch'
        self.assertEqual(self.book._clean_string(string), expected)

    def test_extras_string(self):
        string = '%s/Black Skies CPK MP3 ENG YIFY' % self.folder
        expected = 'Black Skies'
        self.assertEqual(self.book._clean_string(string), expected)


class BookSaveCoverTests(BookMediaObjectTests):

    def test_save_cover_new(self):
        img_url = 'http://books.google.com/books/content?id=4lYZAwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'
        expected = '%s/cover.jpg' % self.folder
        self.assertFalse(os.path.exists(expected))
        result = self.book._save_cover(self.folder, img_url)
        self.assertEqual(result, expected)
        self.assertEqual(self.book.book_info['cover_image'], expected)
        self.assertTrue(os.path.exists(expected))

    def test_save_cover_exists(self):
        img_url = 'http://books.google.com/books/content?id=4lYZAwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'
        expected = '%s/cover.jpg' % self.folder
        # Make file
        with open(expected, 'w'):
            pass
        # Run test
        self.assertTrue(os.path.exists(expected))
        result = self.book._save_cover(self.folder, img_url)
        self.assertEqual(result, expected)
        self.assertNotIn('cover_image', self.book.book_info.keys())


class BookCalculateChunkTests(BookMediaObjectTests):

    def test_chunks_mulipart(self):
        # Set max length to 30 mins
        self.book.handler['max_length'] = 1800
        audio_file = '%s/extra/test_mp3_file.mp3' % os.path.dirname(__file__)
        # Copy files into folder
        for x in range(0, 6):
            dst = '%s/0%s-track.mp3' % (self.folder, str(x+1))
            shutil.copy(audio_file, dst)
        # Set up query
        file_array = os.listdir(self.folder)
        expected = [
            ['01-track.mp3', '02-track.mp3'],
            ['03-track.mp3', '04-track.mp3'],
            ['05-track.mp3', '06-track.mp3']
        ]
        # Run test
        result = self.book._calculate_chunks(self.folder, file_array, 'mp3')
        # Check results
        self.assertEqual(len(result), 3)
        self.assertListEqual(result, expected)

    def test_chunks_single(self):
        # Set max length to 15 mins
        self.book.handler['max_length'] = 900
        audio_file = '%s/extra/test_mp3_file.mp3' % os.path.dirname(__file__)
        # Copy file into folder
        dst = '%s/01-track.mp3' % self.folder
        shutil.copy(audio_file, dst)
        # Set up query
        file_array = os.listdir(self.folder)
        expected = [['01-track.mp3']]
        # Run test
        result = self.book._calculate_chunks(self.folder, file_array, 'mp3')
        # Check results
        self.assertEqual(len(result), 1)
        self.assertListEqual(result, expected)

    def test_chunks_single_parts(self):
        # Set max length to 10 mins
        self.book.handler['max_length'] = 600
        audio_file = '%s/extra/test_mp3_file.mp3' % os.path.dirname(__file__)
        # Copy file into folder
        dst = '%s/01-track.mp3' % self.folder
        shutil.copy(audio_file, dst)
        # Set up query
        file_array = os.listdir(self.folder)
        expected = [['01-track.mp3']]
        # Run test
        result = self.book._calculate_chunks(self.folder, file_array, 'mp3')
        # Check results
        self.assertEqual(len(result), 1)
        self.assertListEqual(result, expected)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2) #, buffer=True)