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
'''Movie media type module'''

# ======== IMPORT MODULES ======== #

import logging
from os import path
from mediahandler.types import getinfo
from re import escape, search


# ======== GET MOVIE ======== #

def get_movie(file_path, settings):
    '''Get movie information'''
    logging.info("Starting movie information handler")
    # Default TV path
    mov_path = '%s/Media/Movies' % path.expanduser("~")
    # Check for custom path in settings
    if settings['folder'] != '':
        if path.exists(settings['folder']):
            mov_path = settings['folder']
            logging.debug("Using custom path: %s", mov_path)
    # Set Variables
    mov_format = "%s/{n} ({y})" % mov_path
    mov_db = "themoviedb"
    # Get info
    new_file = getinfo(mov_format, mov_db, file_path)
    logging.debug("New file: %s", new_file)
    # Check for failure
    if new_file is None:
        return None, None
    # Set search query
    epath = escape(mov_path)
    mov_find = (r"%s\/(.*\(\d{4}\))\.\w{3}" % epath)
    logging.debug("Search query: %s", mov_find)
    # Extract info
    movie = search(mov_find, new_file)
    if movie is None:
        return None, None
    # Set title
    mov_title = movie.group(1)
    # Return Movie Title
    return mov_title, new_file
