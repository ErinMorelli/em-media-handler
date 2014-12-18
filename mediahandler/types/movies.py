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
import mediahandler.types
from os import path
from re import escape, search


# ======== MOVIE CLASS DECLARTION ======== #

class Movie(mediahandler.types.Media):
    '''Movie handler class'''

    # ======== MOVIE CONSTRUCTOR ======== #

    def __init__(self, settings, push):
        '''Movie class constuctor'''
        super(Movie, self).__init__(settings, push)
        # Specific
        self.dst_path = '%s/Media/Movies' % path.expanduser("~")
        # Filebot
        self.filebot['db'] = "themoviedb"
        self.filebot['format'] = "%s/{n} ({y})" % self.dst_path

    # ======== MOVIE OUTOUT PROCESSING ======== #

    def process_output(self, output, file_path):
        '''Movie class output processor'''
        info = super(Movie, self).process_output(output, file_path)
        (new_file, skip) = info
        # Set search query
        epath = escape(self.dst_path)
        mov_find = (r"%s\/(.*\(\d{4}\))\.\w{3}" % epath)
        logging.debug("Search query: %s", mov_find)
        # Extract info
        movie = search(mov_find, new_file)
        if movie is None:
            return self.__match_error(new_file)
        # Set title
        mov_title = movie.group(1)
        # Return Movie Title
        return mov_title, skip
