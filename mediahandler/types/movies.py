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
'''Movie media type module'''

# ======== IMPORT MODULES ======== #

import os
import logging
import mediahandler.types
from re import escape, search


# ======== MOVIE CLASS DECLARTION ======== #

class Movie(mediahandler.types.Media):
    '''Movie handler class'''

    # ======== MOVIE CONSTRUCTOR ======== #

    def __init__(self, settings, push):
        '''Movie class constuctor'''
        self.ptype = 'Movies'
        super(Movie, self).__init__(settings, push)
        # Filebot
        self.filebot['db'] = "themoviedb"
        self.filebot['format'] = os.path.join(self.dst_path, "{n} ({y})")

    # ======== MOVIE OUTOUT PROCESSING ======== #

    def process_output(self, output, file_path):
        '''Movie class output processor'''
        info = super(Movie, self).process_output(output, file_path)
        (added_files, skipped_files) = info
        # Check for no new files
        if len(added_files) == 0:
            return info
        # Set search query
        epath = escape(self.dst_path)
        mov_find = r"{0}\/(.*\(\d{{4}}\))".format(epath)
        logging.debug("Search query: %s", mov_find)
        # See what movies were added
        new_added_files = []
        for added_file in added_files:
            # Extract info
            movie = search(mov_find, added_file)
            if movie is None:
                continue
            # Set title
            mov_title = movie.group(1)
            # Append to new array
            new_added_files.append(mov_title)
        # Make sure we found movies
        if len(new_added_files) == 0:
            return self.match_error(', '.join(added_files))
        # Return movies & skips
        return new_added_files, skipped_files
