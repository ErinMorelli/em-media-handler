#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is a part of EM Media Handler
# Copyright (c) 2014-2021 Erin Morelli
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
"""
Module: mediahandler.types.movies

Module contains:

    - |MHMovie|
        Child class of MHMediaType for the movies media type.

"""

import os
import logging
from re import escape, search
import ntpath

import mediahandler.types


class MHMovie(mediahandler.types.MHMediaType):
    """Child class of MHMediaType for the movies media type.

    Required arguments:
        - settings
            Dict or MHSettings object.
        - push
            MHPush object.

    Public method:
        - |add()|
            inherited from parent MHMediaType.
    """

    def __init__(self, settings, push):
        """Initialize the MHMovie class.

        Required arguments:
            - settings
                Dict or MHSettings object.
            - push
                MHPush object.
        """

        # Set ptype and call super
        self.ptype = 'Movies'
        super(MHMovie, self).__init__(settings, push)

        # Run setup for video media types
        self._video_settings()

        # Set media type-specifc filebot db
        self.cmd.db = "themoviedb"

    def _process_output(self, output, file_path):
        """Parses response from _media_info() query.

        Returns good results and any skipped files.

        Extends MHMediaType function to specifically parse movie
        information from Filebot output.
        """

        info = super(MHMovie, self)._process_output(output, file_path)
        (added_files, skipped_files) = info

        # Check for no new files
        if not added_files:
            return info

        # Set destination path for query
        dst_path = self.dst_path
        if self.dst_path.endswith(os.path.sep):
            dst_path = self.dst_path[:-1]

        # Set search query
        epath = escape(dst_path)
        mov_find = r'{0}{1}(.*\(\d{{4}}\))'.format(
            epath, escape(os.path.sep))
        logging.debug('Search query: %s', mov_find)

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
        if not new_added_files:
            return self._match_error(', '.join(added_files))

        return new_added_files, skipped_files
