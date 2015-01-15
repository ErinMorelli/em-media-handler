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
'''TV media type module'''

# ======== IMPORT MODULES ======== #

import logging
import mediahandler.types
from re import escape, search, sub


# ======== EPISODE CLASS DECLARTION ======== #

class Episode(mediahandler.types.Media):
    '''Episode handler class'''

    # ======== EPISODE CONSTRUCTOR ======== #

    def __init__(self, settings, push):
        '''Episode class constuctor'''
        self.ptype = 'TV'
        super(Episode, self).__init__(settings, push)
        # Filebot
        self.filebot['db'] = "thetvdb"
        form = "/{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}"
        self.filebot['format'] = self.dst_path + form

    # ======== EPISODE OUTOUT PROCESSING ======== #

    def process_output(self, output, file_path):
        '''Episode class output processor'''
        info = super(Episode, self).process_output(output, file_path)
        (added_files, skipped_files) = info
        # Check for no new files
        if len(added_files) == 0:
            return info
        # Set search query
        epath = escape(self.dst_path)
        tv_find = (r"%s\/(.*)\/(.*)\/.*\.S\d{2,4}E(\d{2,3})" % epath)
        logging.debug("Search query: %s", tv_find)
        # See what TV files were added
        new_added_files = []
        for added_file in added_files:
            # Extract info
            episode = search(tv_find, added_file)
            if episode is None:
                continue
            # Show title
            show_name = episode.group(1)
            # Season
            season = episode.group(2)
            # Episode
            ep_num = episode.group(3)
            ep_num_fix = sub('^0', '', ep_num)
            episode = "Episode %s" % ep_num_fix
            # Set title
            ep_title = "%s (%s, %s)" % (show_name, season, episode)
            # Append to new array
            new_added_files.append(ep_title)
        # Make sure we found episodes
        if len(new_added_files) == 0:
            return self.match_error(', '.join(added_files))
        # Return episodes & skips
        return new_added_files, skipped_files
