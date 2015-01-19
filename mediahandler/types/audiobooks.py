#!/usr/bin/python
#
# This file is a part of EM Media Handler
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
'''Audiobook media type module'''


# ======== IMPORT MODULES ======== #

import re
import logging
from re import search
from math import ceil
from shutil import copy, move
from urllib2 import build_opener
from subprocess import Popen, PIPE
from os import path, listdir, makedirs

import mediahandler as mh

from googleapiclient.discovery import build
from mutagen.mp3 import MP3
from mutagen.ogg import OggFileType


# ======== BOOK CLASS DECLARTION ======== #

class Book(object):
    ''' Audiobook handler class'''
    # ======== SET GLOBAL CLASS OPTIONS ======== #

    def __init__(self, settings, push):
        '''Init book class'''
        logging.info("Starting audiobook handler class")
        # Set globals
        self.type = 'book'
        self.book_info = {}
        self.push = push
        # Set up book settings
        self.settings = dict(settings.items() + {
            'regex': {
                "nc": r"\.(mp3|ogg|wav)$",
                "c": r"\.(m4b)$",
            },
            'audio': {
                'MP3': MP3,
                'OGG': OggFileType,
            },
        }.items())
        # Check for null path in settings
        if self.settings['folder'] is None:
            self.settings['folder'] = path.join(
                path.expanduser("~"), 'Media', 'Audiobooks')
            logging.debug("Using default path: %s", self.settings['folder'])
        # Check destination exists
        if not path.exists(self.settings['folder']):
            self.push.failure("Folder for Audiobooks not found: {0}".format(
                self.settings['folder']))
        # Look for Google api key
        if settings['api_key'] is None:
            logging.warning("Google Books API key not found")
            raise Warning("Google Books API key not found")
        # Default chapter length
        self.settings['max_length'] = 28800  # 8hrs (in seconds)
        # Look for custom chapter length
        if self.settings['chapter_length'] is not None:
            # Convert hours to seconds
            custom_length = self.settings['chapter_length'] * 3600
            # Set new length
            self.settings['max_length'] = custom_length
            logging.debug("Using custom chapter length: %s",
                          self.settings['max_length'])

    # ======== CLEAN UP SEARCH STRING ======== #

    def _clean_string(self, str_path):
        '''Clean up path string'''
        logging.info("Cleaning up path string")
        # Get query from folder path
        find_book = re.search(r"^((.*)?\/(.*))$", str_path)
        string = find_book.group(3)
        logging.debug("Initial string: %s", string)
        # Save original path for later
        self.settings['orig_path'] = find_book.group(2)
        # Get blacklist items from file
        blacklist_file = path.join(mh.__mediaextras__, 'blacklist.txt')
        blacklist = [line.strip() for line in open(blacklist_file)]
        # Convert blacklist array to regex string
        blacklist = "|".join(blacklist)
        # Remove blacklist words
        count = 1
        while count > 0:
            (string, count) = re.subn(blacklist, " ", string, 0, re.I)
        # setup order of regexes
        regexes = [
            r"[\(\[\{].*[\)\]\}]",
            r"[^a-zA-Z ]",
            r"[A-Z]{3,4}",
            r"\s{2,10}",
        ]
        # Loop through regexes
        for regex in regexes:
            count = 1
            while count > 0:
                (string, count) = re.subn(regex, ' ', string)
        # Remove trailing or start whitespace
        count = 1
        while count > 0:
            (string, count) = re.subn(r'(^\s|\s$)', '', string)
        # return cleaned up string
        return string

    # ======== SAVE COVER IMAGE ======== #

    def _save_cover(self, img_dir, img_url):
        '''Save cover image'''
        logging.info("Saving audiobook cover image")
        # Set new image file path
        img_path = path.join(img_dir, 'cover.jpg')
        logging.debug("Image URL: %s", img_url)
        logging.debug("Image Path: %s", img_path)
        # Check to see if file exists
        if path.isfile(img_path):
            logging.warning("Cover image already exists")
            # If so, return none
            return img_path
        # Clean up image url
        no_curl = re.sub(r"(\&edge=curl)", "", img_url)
        logging.debug("Cleaned cover url: %s", no_curl)
        # Set image request headers
        opener = build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        # Get image info from web
        response = opener.open(no_curl)
        # Open destination file
        output = open(img_path, "wb")
        # Write image contents to file
        output.write(response.read())
        # Close open file
        output.close()
        # Add image to book info
        self.book_info['cover_image'] = img_path
        # Return new image path
        return img_path

    # ======== CALCULATE CHUNKS  ======== #

    def _calculate_chunks(self, file_path, file_array, file_type):
        '''Calculate chapter chunks'''
        # Defaults
        file_type = file_type.upper()
        total_length = 0
        book_parts = 0
        # Sum all the file durations
        for get_file in file_array:
            full_path = path.join(file_path, get_file)
            audio_track = self.settings['audio'][file_type](full_path)
            total_length += audio_track.info.length
            logging.debug("%s:  %s", get_file, audio_track.info.length)
        logging.debug("Total book length: %s seconds", total_length)
        # Check against defined max part length
        if total_length <= self.settings['max_length']:
            book_parts = 1
            logging.debug("Parts: %s", book_parts)
            chunks = [file_array]
        else:
            # Determine how many parts should be made
            book_parts = int(ceil(total_length / self.settings['max_length']))
            logging.debug("Parts: %s", book_parts)
            # Count files
            logging.debug("File count: %s", len(file_array))
            # Calculate array chunk size
            array_chunk = int(ceil(len(file_array) / book_parts))
            logging.debug("Array chunks: %s", array_chunk)
            # Create array chunks
            if array_chunk > 0:
                chunks = [file_array[x:x+array_chunk]
                          for x in xrange(0, len(file_array), array_chunk)]
            else:
                chunks = [file_array]
        return chunks

    # ======== CHAPTERIZE FILES  ======== #

    def _get_chapters(self, file_path, file_array, file_type):
        '''Get audiobook chapter information'''
        logging.info("Determining book parts")
        # Calculate chunks
        book_chunks = []
        chunks = self._calculate_chunks(file_path, file_array, file_type)
        # Create new subfolders for parts
        logging.info("Creating book part subfolders")
        for i, chunk in enumerate(chunks):
            # Create new folder for part
            part_path = path.join(file_path, 'Part {0}'.format(str(i+1)))
            if not path.exists(part_path):
                makedirs(part_path)
            # Move files for part into new path
            for get_chunk in chunk:
                start_path = path.join(file_path, get_chunk)
                end_path = path.join(part_path, get_chunk)
                copy(start_path, end_path)
            # Copy over cover image
            cover_start = path.join(file_path, 'cover.jpg')
            cover_end = path.join(part_path, 'cover.jpg')
            copy(cover_start, cover_end)
            # Add new part folder to array
            book_chunks.append(part_path)
        # Return array of new part paths
        return book_chunks

    # ======== CHAPTERIZE FILES  ======== #

    def _chapterize_files(self, file_path, file_array):
        '''Chapterize audiobook files'''
        logging.info("Chapterizing audiobook files")
        new_files = []
        # Get chapter parts
        file_parts = self._get_chapters(file_path, file_array,
                                        self.settings['file_type'])
        # Create m4b for each file part
        for i, file_part in enumerate(file_parts):
            part_path = path.join(file_path, 'Part {0}'.format(str(i+1)))
            # Define chapter query
            b_cmd = ['/usr/bin/php', '-f', self.settings['has_abc'],
                     file_part,  # Path to book files
                     self.book_info['author'].encode("utf8"),  # artist
                     self.book_info['long_title'].encode("utf8"),  # album
                     self.book_info['short_title'].encode("utf8"),  # title
                     self.book_info['genre'].encode("utf8"),  # genre
                     self.book_info['year'].encode("utf8"),  # year
                     self.settings['file_type']]  # file type
            logging.debug("ABC query:\n%s", b_cmd)
            # Process query
            b_open = Popen(b_cmd, stdout=PIPE, stderr=PIPE)
            # Get output
            (output, err) = b_open.communicate()
            logging.debug("ABC output: %s", output)
            logging.debug("ABC err: %s", err)
            # Find file names in output
            bfiles = search(r"Audiobook \'(.*)\.m4b\' created succsessfully!",
                            output)
            if bfiles is None:
                return False, output
            # Set full file path
            created_file = path.join(
                part_path, '{0}.m4b'.format(bfiles.group(1)))
            new_file_path = path.join(file_path, '{0} - {1}.m4b'.format(
                bfiles.group(1), str(i+1)))
            # Rename file with part #
            move(created_file, new_file_path)
            logging.debug("New file path: %s", new_file_path)
            # Add to array
            new_files.append(new_file_path)
        # Return success with array of new file paths
        return True, new_files

    # ======== GET AUDIOBOOK FILES ======== #

    def _get_files(self, file_dir, make_chapters):
        '''Retrieve audiobook files'''
        logging.info("Retrieving audiobook files")
        # default values
        is_chapterized = False
        to_chapterize = []
        book_files = []
        file_list = []
        # Get list of files
        file_list = listdir(file_dir)
        # loop through all the files in dir
        for item in sorted(file_list):
            # Look for file types we want
            good_file = re.search(self.settings['regex']['c'], item, re.I)
            if good_file:
                full_path = path.join(file_dir, item)
                book_files.append(full_path)
            # Look for file types we can chapterize
            bad_file = re.search(self.settings['regex']['nc'], item, re.I)
            if bad_file:
                self.settings['file_type'] = bad_file.group(1)
                to_chapterize.append(item)
        # See if any files need chapterizing
        if make_chapters:
            logging.debug("Already chaptered file count: %s", len(book_files))
            logging.debug("To chapter file count: %s", len(to_chapterize))
            if len(to_chapterize) > 0 and len(book_files) == 0:
                (chapter_success, new_files) = self._chapterize_files(
                    file_dir, to_chapterize)
                if chapter_success:
                    book_files = new_files
                else:
                    return False, new_files
        elif len(book_files) == 0 and len(to_chapterize) > 0:
            logging.debug("Not making chapters")
            book_files = to_chapterize
        elif len(book_files) > 0 and len(to_chapterize):
            logging.warning('Non-chaptered files were found and ignored: %s',
                            ', '.join(to_chapterize))
        # Make sure we have chapterized files to return
        logging.debug("Final book file count: %s", len(book_files))
        if len(book_files) > 0:
            is_chapterized = True
        # Return status and files
        return is_chapterized, book_files

    # ======== MOVE FILES ======== #

    def _move_files(self, file_array, has_chapters):
        '''Move audiobook files'''
        logging.info("Moving audiobook files")
        # Create folder-friendly title
        if self.book_info['subtitle'] is None:
            folder_title = self.book_info['short_title']
        else:
            folder_title = '{0}_ {1}'.format(self.book_info['short_title'],
                                             self.book_info['subtitle'])
        # Set new book directory path
        book_dir = path.join(self.settings['folder'],
                             self.book_info['author'], folder_title)
        logging.debug("New directory: %s", book_dir)
        # Create the folder
        if not path.exists(book_dir):
            makedirs(book_dir)
        # Sort files in order
        sorted_array = sorted(file_array)
        # Loop through files
        moved_files = []
        skipped_files = []
        for i, book_file in enumerate(sorted_array):
            # Set new name
            new_name = self.book_info['short_title']
            new_path = ''
            # Use chapter naming for chapters
            if has_chapters:
                # Set start path
                start_path = book_file
                # Check for multiple parts
                if len(file_array) > 1:
                    book_part = ', Part {0}'.format(str(i+1))
                    new_name = self.book_info['short_title'] + book_part
                # Set new file path
                new_path = path.join(book_dir, '{0}.m4b'.format(new_name))
            else:
                # Set non-chaptered file paths & formatting
                start_path = path.join(self.settings['orig_path'], book_file)
                new_name = '{0:02d} - {1}.{2}'.format(
                    i+1, new_name, self.settings['file_type'])
                new_path = path.join(book_dir, new_name)
            logging.debug("Start path: %s", start_path)
            logging.debug("New path: %s", new_path)
            # Check for duplicate
            if path.isfile(new_path):
                # Add to skipped file list
                skipped_files.append(new_path)
                logging.warning("Duplicate file was skipped: %s", new_path)
            else:
                # Copy the file
                copy(start_path, new_path)
                # Add to moved file list
                moved_files.append(new_name)
        # Return moved & skipped files
        return moved_files, skipped_files

    # ======== DEAL WITH SINGLE FILES ======== #

    def _single_file(self, file_path, path_name):
        '''Move single file into its own folder'''
        logging.info("Handling as single file")
        # Set root path
        path_root = self.settings['orig_path']
        # Set new folder
        new_folder = path.join(path_root, path_name)
        logging.debug("New folder: %s", new_folder)
        # Create folder
        if not path.exists(new_folder):
            makedirs(new_folder)
        # Get file name
        # name_query = r"^{0}\/(.*)$".format(re.escape(path_root))
        # name_search = re.search(name_query, file_path)
        file_name = path.basename(file_path)
        # Set new path
        new_path = path.join(new_folder, file_name)
        logging.debug("New path: %s", new_path)
        # Move file
        move(file_path, new_path)
        # Return new file folder
        return new_folder

    # ======== GET BOOK INFO FROM GOOGLE ======== #

    def ask_google(self, query):
        '''Get metadata from google books api '''
        logging.info("Querying Google Books")
        # Connect to Google Books API
        service = build('books', 'v1', developerKey=self.settings['api_key'])
        # Make API request
        request = service.volumes().list(
            q=query,
            orderBy="relevance",
            printType="books",
            maxResults=5
        )
        # Get response
        response = request.execute()
        logging.debug("Google response:\n%s", response)
        # Get the top response
        for book in response.get('items', []):
            # Get publication date
            published = book['volumeInfo']['publishedDate']
            logging.debug("Published date: %s", published)
            # Extract just the year
            find_year = re.match(r"(\d{4})", published)
            year = ''
            if find_year is not None:
                year = find_year.group(1)
            # Check for categories
            category = "Audiobook"
            if 'categories' in book['volumeInfo']:
                category = book['volumeInfo']['categories'][0]
            # look for titles
            long_title = book['volumeInfo']['title']
            subtitle = None
            if 'subtitle' in book['volumeInfo']:
                long_title = '{0}: {1}'.format(book['volumeInfo']['title'],
                                               book['volumeInfo']['subtitle'])
                subtitle = book['volumeInfo']['subtitle']
            # Set book information file structure
            logging.info("Google Book ID: %s", book['id'])
            new_book_info = {
                'id': book['id'],
                'short_title': book['volumeInfo']['title'],
                'long_title': long_title,
                'subtitle': subtitle,
                'year': year,
                'genre': category,
                'author': ", ".join(book['volumeInfo']['authors']),
                'cover': book['volumeInfo']['imageLinks']['thumbnail'],
            }
            break
        # Return info
        return new_book_info

    # ======== MAIN BOOK FUNCTION (public) ======== #

    def add(self, raw):
        '''Main get book function'''
        logging.info("Getting audiobook")
        # Parse string & get query
        refined = self._clean_string(raw)
        logging.debug("Cleaned search string: %s", refined)
        # Use custom search string, if defined
        if 'custom_search' in self.settings.keys():
            refined = self.settings['custom_search']
            logging.debug("Custom search query: %s", refined)
        # Get book info from Google
        self.book_info = self.ask_google(refined)
        logging.debug(self.book_info)
        # Deal with single files
        if path.isfile(raw):
            raw = self._single_file(raw, self.book_info['short_title'])
        # Save cover image to file
        cover_file = self._save_cover(raw, self.book_info['cover'])
        logging.debug("Cover image: %s", cover_file)
        # Get files and chapterize files, if enabled
        get_result = self._get_files(raw, self.settings['make_chapters'])
        (is_chapterized, book_files) = get_result
        logging.debug(book_files)
        # Verify success
        if not is_chapterized:
            self.push.failure("Unable to chapterize book: {0}".format(raw))
        # Move & rename files
        (move_files, skipped) = self._move_files(
            book_files, self.settings['make_chapters'])
        logging.debug("Move was successful: %s", move_files)
        # Verify success
        if move_files is None:
            return self.push.failure(
                "Unable to move book files: {0}".format(raw))
        # format book title
        book_title = '"{0}" by {1}'.format(self.book_info['long_title'],
                                           self.book_info['author'])
        logging.info("Book title: %s", book_title)
        # return new book title
        return [book_title], skipped
