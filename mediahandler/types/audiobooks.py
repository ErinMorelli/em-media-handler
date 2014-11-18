#!/usr/bin/python
#
# This file is a part of EM Media Handler
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

from apiclient.discovery import build
from mutagen.mp3 import MP3
from mutagen.ogg import OggFileType


# ======== BOOK CLASS DECLARTION ======== #

class Book:
    ''' Audiobook handler class'''
    # ======== SET GLOBAL CLASS OPTIONS ======== #

    def __init__(self, settings):
        '''Init book class'''
        logging.info("Starting audiobook handler class")
        # Set global bookinfo
        self.book_info = {}
        # Get blacklist path
        __list_path = path.dirname(__file__) + '/blacklist.txt'
        # Set up handler info
        self.handler = {
            'blacklist': __list_path,
            'regex': {
                "nc": r".(mp3|ogg|wav)$",
                "c": r".(m4b)$",
            },
            'audio': {
                'MP3': MP3,
                'OGG': OggFileType,
            },
        }
        # Default TV path
        self.handler['path'] = '%s/Media/Audiobooks' % path.expanduser("~")
        # Check for custom path in settings
        if settings['folder'] != '':
            if path.exists(settings['folder']):
                self.handler['path'] = settings['folder']
                logging.debug("Using custom path: %s", self.handler['path'])
        # Look for Google api key
        if settings['api_key'] != '':
            self.handler['api_key'] = settings['api_key']
            logging.debug("Found Google Books API key")
        else:
            logging.warning("Google Books API key not found")
            raise Warning("Google Books API key not found")
        # Default chapter length
        self.handler['max_length'] = 28800  # 8hrs (in seconds)
        # Look for custom chapter length
        if settings['chapter_length'] != '':
            # Convert hours to seconds
            custom_length = int(settings['chapter_length']) * 3600
            # Set new length
            self.handler['max_length'] = custom_length
            logging.debug("Using custom chapter length: %s",
                          self.handler['max_length'])
        if settings['make_chapters'] != '':
            self.handler['make_chapters'] = settings['make_chapters']

    # ======== CLEAN UP SEARCH STRING ======== #

    def __clean_string(self, str_path):
        '''Clean up path string'''
        logging.info("Cleaning up path string")
        # Get query from folder path
        find_book = re.search(r"^((.*)?\/(.*))$", str_path)
        string = find_book.group(3)
        logging.debug("Initial string: %s", string)
        # Save original path for later
        self.handler['orig_path'] = find_book.group(2)
        # Get blacklist items from file
        blacklist = [line.strip() for line in open(self.handler['blacklist'])]
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
                (string, count) = re.subn(regex, " ", string)
        # return cleaned up string
        return string

    # ======== SAVE COVER IMAGE ======== #

    def __save_cover(self, img_dir, img_url):
        '''Save cover image'''
        logging.info("Saving audiobook cover image")
        # Set new image file path
        img_path = img_dir + "/cover.jpg"
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

    def __calculate_chunks(self, file_path, file_array, file_type):
        '''Calculate chapter chunks'''
        # Defaults
        file_type = file_type.upper()
        total_length = 0
        book_parts = 0
        # Sum all the file durations
        for get_file in file_array:
            full_path = file_path + '/' + get_file
            audio_track = self.handler['audio'][file_type](full_path)
            total_length += audio_track.info.length
            logging.debug("%s:  %s", get_file, audio_track.info.length)
        logging.debug("Total book length: %s seconds", total_length)
        # Check against defined max part length
        if total_length <= self.handler['max_length']:
            book_parts = 1
            logging.debug("Parts: %s", book_parts)
            chunks = [file_array]
        else:
            # Determine how many parts should be made
            book_parts = int(ceil(total_length / self.handler['max_length']))
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

    def __get_chapters(self, file_path, file_array, file_type):
        '''Get audiobook chapter information'''
        logging.info("Determining book parts")
        # Calculate chunks
        book_chunks = []
        chunks = self.__calculate_chunks(file_path, file_array, file_type)
        # Create new subfolders for parts
        logging.info("Creating book part subfolders")
        for i, chunk in enumerate(chunks):
            # Create new folder for part
            part_path = file_path + '/Part ' + str(i+1)
            if not path.exists(part_path):
                makedirs(part_path)
            # Move files for part into new path
            for get_chunk in chunk:
                start_path = file_path + '/' + get_chunk
                end_path = part_path + '/' + get_chunk
                copy(start_path, end_path)
            # Copy over cover image
            copy(file_path+'/cover.jpg', part_path+'/cover.jpg')
            # Add new part folder to array
            book_chunks.append(part_path)
        # Return array of new part paths
        return book_chunks

    # ======== CHAPTERIZE FILES  ======== #

    def __chapterize_files(self, file_path, file_array):
        '''Chapterize audiobook files'''
        logging.info("Chapterizing audiobook files")
        new_files = []
        # Get chapter parts
        file_parts = self.__get_chapters(file_path,
                                         file_array, self.handler['file_type'])
        # Create m4b for each file part
        for i, file_part in enumerate(file_parts):
            part_path = file_path + '/Part ' + str(i+1)
            # Define chapter query
            b_cmd = ['/usr/bin/php', '-f', '/usr/bin/abc.php',
                     file_part,  # Path to book files
                     self.book_info['author'].encode("utf8"),  # artist
                     self.book_info['long_title'].encode("utf8"),  # album
                     self.book_info['short_title'].encode("utf8"),  # title
                     self.book_info['genre'].encode("utf8"),  # genre
                     self.book_info['year'].encode("utf8"),  # year
                     self.handler['file_type']]  # file type
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
            created_file = part_path + '/' + bfiles.group(1) + '.m4b'
            new_file_path = (file_path + '/' + bfiles.group(1)
                             + ' - ' + str(i+1) + '.m4b')
            # Remave file with part #
            move(created_file, new_file_path)
            logging.debug("New file path: %s", new_file_path)
            # Add to array
            new_files.append(new_file_path)
        # Return success with array of new file paths
        return True, new_files

    # ======== GET AUDIOBOOK FILES ======== #

    def __get_files(self, file_dir, make_chapters):
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
            good_file = re.search(self.handler['regex']['c'], item, re.I)
            if good_file:
                full_path = file_dir + '/' + item
                book_files.append(full_path)
            # Look for file types we can chapterize
            bad_file = re.search(self.handler['regex']['nc'], item, re.I)
            if bad_file:
                self.handler['file_type'] = bad_file.group(1)
                to_chapterize.append(item)
        # See if any files need chapterizing
        if make_chapters:
            logging.debug("Already chaptered file count: %s", len(book_files))
            logging.debug("To chapter file count: %s", len(to_chapterize))
            if len(to_chapterize) > 0 and len(book_files) == 0:
                (chapter_success, new_files) = self.__chapterize_files(
                    file_dir, to_chapterize)
                if chapter_success:
                    book_files = new_files
                else:
                    return False, new_files
        else:
            logging.debug("Not making chapters")
            book_files = to_chapterize
        # Make sure we have chapterized files to return
        logging.debug("Final book file count: %s", len(book_files))
        if len(book_files) > 0:
            is_chapterized = True
        # Return status and files
        return is_chapterized, book_files

    # ======== MOVE FILES ======== #

    def __move_files(self, file_array, has_chapters):
        '''Move audiobook files'''
        logging.info("Moving audiobook files")
        # Create folder-friendly title
        if self.book_info['subtitle'] is None:
            folder_title = self.book_info['short_title']
        else:
            folder_title = (self.book_info['short_title'] +
                            '_ ' + self.book_info['subtitle'])
        # Set new book directory path
        book_dir = (self.handler['path'] + '/' +
                    self.book_info['author'] + '/' + folder_title)
        logging.debug("New directory: %s", book_dir)
        # Create the folder
        if not path.exists(book_dir):
            makedirs(book_dir)
        # Sort files in order
        sorted_array = sorted(file_array)
        # Loop through files
        moved_files = []
        for i, book_file in enumerate(sorted_array):
            # Set new name
            new_name = self.book_info['short_title']
            # Use chapter naming for chapters
            if has_chapters:
                # Set start path
                start_path = book_file
                # Check for multiple parts
                if len(file_array) > 1:
                    book_part = ', Part %s' % str(i+1)
                    new_name = self.book_info['short_title'] + book_part
                # Set new file path
                new_path = book_dir + '/' + new_name + '.m4b'
                # Copy & rename the files
                copy(start_path, new_path)
            else:
                # Set non-chaptered file paths & formatting
                start_path = self.handler['orig_path'] + '/' + book_file
                new_path = ("%s/%02d - %s.%s" %
                            (book_dir, i+1, new_name,
                             self.handler['file_type']))
                # Copy the files
                copy(start_path, new_path)
            logging.debug("Start path: %s", start_path)
            logging.debug("New path: %s", new_path)
            # Add to moved file list
            moved_files.append(new_name)
        if len(moved_files) == 0:
            return False
        # return success and list of moved files
        return True

    # ======== DEAL WITH SINGLE FILES ======== #

    def __single_file(self, file_path, path_name):
        '''Move single file into its own folder'''
        logging.info("Handling as single file")
        # Set root path
        path_root = self.handler['orig_path']
        # Set new folder
        new_folder = path.join(path_root, path_name)
        logging.debug("New folder: %s", new_folder)
        # Create folder
        if not path.exists(new_folder):
            makedirs(new_folder)
        # Get file name
        name_query = r"^%s\/(.*)$" % re.escape(path_root)
        name_search = re.search(name_query, file_path)
        file_name = name_search.group(1)
        # Set new path
        new_path = new_folder + '/' + file_name
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
        service = build('books', 'v1', developerKey=self.handler['api_key'])
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
            if find_year is None:
                logging.error("No year found")
                year = '9999'
            else:
                year = find_year.group(1)
            # Check for categories
            if 'categories' in book['volumeInfo']:
                category = book['volumeInfo']['categories'][0]
            else:
                category = "Audiobook"
            if 'subtitle' in book['volumeInfo']:
                long_title = (book['volumeInfo']['title'] +
                              ': ' + book['volumeInfo']['subtitle'])
                subtitle = book['volumeInfo']['subtitle']
            else:
                long_title = book['volumeInfo']['title']
                subtitle = None
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

    def get_book(self, raw, custom_search=None):
        '''Main get book function'''
        logging.info("Getting audiobook")
        # Parse string & get query
        refined = self.__clean_string(raw)
        logging.debug("Cleaned search string: %s", refined)
        # Deal with single files
        if path.isfile(raw):
            raw = self.__single_file(raw, refined)
        # Use custom search string, if defined
        if custom_search is not None:
            logging.debug("Custom search query: %s", custom_search)
            refined = custom_search
        # Get book info from Google
        self.book_info = self.ask_google(refined)
        logging.debug(self.book_info)
        # Save cover image to file
        cover_file = self.__save_cover(raw, self.book_info['cover'])
        logging.debug("Cover image: %s", cover_file)
        # Get files and chapterize files, if enabled
        get_result = self.__get_files(raw, self.handler['make_chapters'])
        (is_chapterized, book_files) = get_result
        logging.debug(book_files)
        # Verify success
        if not is_chapterized:
            return None
        # Move & rename files
        move_success = self.__move_files(book_files,
                                         self.handler['make_chapters'])
        logging.debug("Move was successful: %s", move_success)
        # Verify success
        if not move_success:
            return None
        # format book title
        book_title = ('"' + self.book_info['long_title'] +
                      '" by ' + self.book_info['author'])
        logging.info("Book title: %s", book_title)
        # return new book title
        return book_title
