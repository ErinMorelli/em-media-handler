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


# ======== IMPORT MODULES ======== #

import logging
from os import path
from mediahandler.types import getinfo
from re import escape, search


# ======== CLASS DECLARTION ======== #

class Movie:

    # ======== INIT MOVIE CLASS ======== #

    def __init__(self, settings):
        logging.info("Initializing renaming class")
        # Default TV path
        self.mov_path = '%s/Media/Movies' % path.expanduser("~")
        # Check for custom path in settings
        if settings['folder'] != '':
            if path.exists(settings['folder']):
                self.mov_path = settings['folder']
                logging.debug("Using custom path: %s" % self.tv_path)

    # ======== GET MOVIE ======== #

    def get_movie(self, file_path):
        logging.info("Starting movie information handler")
        # Set Variables
        mov_format = "%s/{n} ({y})" % self.mov_path
        mov_db = "themoviedb"
        # Get info
        new_file = getinfo(mov_format, mov_db, file_path)
        logging.debug("New file: %s", new_file)
        # Check for failure
        if new_file is None:
            return None
        # Set search query
        epath = escape(self.mov_path)
        mov_find = "%s\/(.*\(\d{4}\))\.\w{3}" % epath
        logging.debug("Search query: %s", mov_find)
        # Extract info
        movie = search(mov_find, new_file)
        if movie is None:
            return None
        # Set title
        mov_title = movie.group(1)
        # Return Movie Title
        return mov_title, new_file
