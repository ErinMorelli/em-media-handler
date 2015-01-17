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
from mutagen.mp3 import MP3

import _common
from _common import unittest
from _common import MHTestSuite

from test_media import MediaObjectTests

import mediahandler.types.audiobooks as Books


class BookMediaObjectTests(MediaObjectTests):

    def setUp(self):
        # Call Super
        super(BookMediaObjectTests, self).setUp()
        # Real audio file for testing
        self.audio_file = ('%s/extra/test_mp3_file.mp3'
                            % os.path.dirname(__file__))
        # Book-specific settings
        self.settings['api_key'] = _common.get_google_api()
        self.settings['chapter_length'] = None
        self.settings['make_chapters'] = False
        # Make an object
        self.book = Books.Book(self.settings, self.push)


class BaseBookObjectTests(BookMediaObjectTests):

    def test_bad_google_api(self):
        self.settings['api_key'] = None
        regex = r'Google Books API key not found'
        self.assertRaisesRegexp(
            Warning, regex, Books.Book, self.settings, self.push)

    def test_custom_chapter_length(self):
        self.settings['chapter_length'] = 10
        self.book = Books.Book(self.settings, self.push)
        self.assertEqual(self.book.settings['max_length'], 36000)

    def test_custom_search_string(self):
        search = 'Gone Girl Gillian Flynn'
        self.settings['custom_search'] = search
        self.book = Books.Book(self.settings, self.push)
        self.assertEqual(self.book.settings['custom_search'], search)


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
        self.book.settings['max_length'] = 1800
        # Copy files into folder
        for x in range(0, 6):
            dst = '%s/0%s-track.mp3' % (self.folder, str(x+1))
            shutil.copy(self.audio_file, dst)
        # Set up query
        file_array = sorted(os.listdir(self.folder))
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
        self.book.settings['max_length'] = 900
        # Copy file into folder
        dst = '%s/01-track.mp3' % self.folder
        shutil.copy(self.audio_file, dst)
        # Set up query
        file_array = sorted(os.listdir(self.folder))
        expected = [['01-track.mp3']]
        # Run test
        result = self.book._calculate_chunks(self.folder, file_array, 'mp3')
        # Check results
        self.assertEqual(len(result), 1)
        self.assertListEqual(result, expected)

    def test_chunks_single_parts(self):
        # Set max length to 10 mins
        self.book.settings['max_length'] = 600
        # Copy file into folder
        dst = '%s/01-track.mp3' % self.folder
        shutil.copy(self.audio_file, dst)
        # Set up query
        file_array = sorted(os.listdir(self.folder))
        expected = [['01-track.mp3']]
        # Run test
        result = self.book._calculate_chunks(self.folder, file_array, 'mp3')
        # Check results
        self.assertEqual(len(result), 1)
        self.assertListEqual(result, expected)


class GetChaptersTests(BookMediaObjectTests):

    def make_cover(self):
        # Make dummy cover image
        tmp_img = _common.make_tmp_file('.jpg')
        cover_img = '%s/cover.jpg' % self.folder
        shutil.move(tmp_img, cover_img)

    def test_chapters_mulipart(self):
        # Set max length to 30 mins
        self.book.settings['max_length'] = 1800
        # Copy files into folder
        for x in range(0, 6):
            dst = '%s/0%s-track.mp3' % (self.folder, str(x+1))
            shutil.copy(self.audio_file, dst)
        # Set up query
        file_array = sorted(os.listdir(self.folder))
        # Make cover
        self.make_cover()
        expected = [
            ('%s/Part 1' % self.folder),
            ('%s/Part 2' % self.folder),
            ('%s/Part 3' % self.folder),
        ]
        # Run test
        result = self.book._get_chapters(self.folder, file_array, 'mp3')
        # Check results
        self.assertEqual(len(result), 3)
        self.assertListEqual(result, expected)

    def test_chunks_single(self):
        # Set max length to 15 mins
        self.book.settings['max_length'] = 900
        # Copy file into folder
        dst = '%s/01-track.mp3' % self.folder
        shutil.copy(self.audio_file, dst)
        # Set up query
        file_array = sorted(os.listdir(self.folder))
        # Make cover
        self.make_cover()
        expected = [('%s/Part 1' % self.folder)]
        # Run test
        result = self.book._get_chapters(self.folder, file_array, 'mp3')
        # Check results
        self.assertEqual(len(result), 1)
        self.assertListEqual(result, expected)


@unittest.skipUnless(sys.platform.startswith("linux"), "requires Ubuntu")
class AddBookTest(BookMediaObjectTests):
    
    def test_add_book(self):
        # Set up abc path
        self.book.settings['has_abc'] = '/usr/local/bin/abc.php'
        if not os.path.exists(self.book.settings['has_abc']):
            self.book.settings['has_abc'] = '/usr/bin/abc.php'
        # Set max length to 30 mins
        self.book.settings['max_length'] = 1800
        self.book.settings['make_chapters'] = True
        self.book.settings['custom_search'] = 'Paul Doiron Bone Orchard'
        # Copy files into folder
        for x in range(0, 2):
            dst = '%s/0%s-track.mp3' % (self.folder, str(x+1))
            shutil.copy(self.audio_file, dst)
        # Run test
        (result, skips) = self.book.add(self.folder)
        # Check results
        regex = r'"The Bone Orchard: A Novel" by Paul Doiron'
        self.assertRegexpMatches(result, regex)
        self.assertFalse(skips)
        # Check that file was made
        created = ('%s/Paul Doiron/The Bone Orchard_ A Novel/The Bone Orchard.m4b'
                  % self.folder)
        self.assertTrue(os.path.exists(created))


class GetFilesTests(BookMediaObjectTests):

    def test_get_files_mixed(self):
        # Set up folder
        book_file1 = _common.make_tmp_file('.m4b', self.folder)
        book_file2 = _common.make_tmp_file('.m4b', self.folder)
        book_file3 = _common.make_tmp_file('.mp3', self.folder)
        # Set up test
        expected = [book_file1, book_file2]
        # Run test
        (success, result) = self.book._get_files(self.folder, False)
        # Check results
        self.assertTrue(success)
        self.assertListEqual(sorted(expected), sorted(result))

    def test_get_files_good(self):
        # Set up folder
        book_file1 = _common.make_tmp_file('.m4b', self.folder)
        book_file2 = _common.make_tmp_file('.m4b', self.folder)
        # Set up test
        expected = [book_file1, book_file2]
        # Run test
        (success, result) = self.book._get_files(self.folder, False)
        # Check results
        self.assertTrue(success)
        self.assertListEqual(sorted(expected), sorted(result))

    def test_get_files_bad(self):
        # Set up folder
        book_file1 = _common.make_tmp_file('.mp3', self.folder)
        book_file2 = _common.make_tmp_file('.mp3', self.folder)
        # Set up test
        expected = [
            os.path.basename(book_file1),
            os.path.basename(book_file2)
        ]
        # Run test
        (success, result) = self.book._get_files(self.folder, False)
        # Check results
        self.assertTrue(success)
        self.assertListEqual(sorted(expected), sorted(result))
        self.assertEqual(self.book.settings['file_type'], 'mp3')

    @_common.skipUnlessHasMod('mutagen', 'mp3')
    def test_get_files_bad_chaptered(self):
        # Set up folder
        book_file1 = _common.make_tmp_file('.mp3', self.folder)
        book_file2 = _common.make_tmp_file('.mp3', self.folder)
        # Set up test
        import mutagen.mp3
        # Run test
        regex = r''
        self.assertRaisesRegexp(mutagen.mp3.HeaderNotFoundError,
            regex, self.book._get_files, self.folder, True)

    def test_get_files_none(self):
        # Set up folder
        book_file1 = _common.make_tmp_file('.m4a', self.folder)
        book_file2 = _common.make_tmp_file('.m4a', self.folder)
        # Set up test
        expected = []
        # Run test
        (success, result) = self.book._get_files(self.folder, False)
        # Check results
        self.assertFalse(success)
        self.assertListEqual(expected, result)

# TO DO:
#  - only book files
#  - only bad files
#      + with/without chaptering
#  - no files


def suite():
    s = MHTestSuite()
    tests = unittest.TestLoader().loadTestsFromName(__name__)
    s.addTest(tests)
    return s


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2) #, buffer=True)