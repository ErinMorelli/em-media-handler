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
'''
Module: mediahandler.types.tv

Module contains:

    - |MHTv|
        Child class of MHMediaType for the TV media type.

'''

import logging
import mediahandler.types
from re import escape, search, sub


class MHTv(mediahandler.types.MHMediaType):
    '''Child class of MHMediaType for the TV media type.

    Required arguments:
        - settings
            Dict or MHSettings object.
        - push
            MHPush object.

    Public method:
        - |add()|
            inherited from parent MHMediaType.
    '''

    def __init__(self, settings, push):
        '''Initialize the MHTv class.

        Required arguments:
            - settings
                Dict or MHSettings object.
            - push
                MHPush object.
        '''

        # Set ptype and call super
        self.ptype = 'TV'
        super(MHTv, self).__init__(settings, push)

        # Run setup for video media types
        self._video_settings()

        # Set media type-specifc filebot db
        self.cmd.db = "thetvdb"

    def _process_output(self, output, file_path):
        '''Parses response from _media_info() query.

        Returns good results and any skipped files.

        Extends MHMediaType function to specifically parse TV Show
        and episode information from Filebot output.
        '''

        info = super(MHTv, self)._process_output(output, file_path)
        (added_files, skipped_files) = info

        # Check for no new files
        if len(added_files) == 0:
            return info

        # Set search query
        epath = escape(self.dst_path)
        tv_find = r"{0}\/(.*)\/(.*)\/.*\.S\d{{2,4}}E(\d{{2,3}})".format(epath)
        logging.debug("Search query: %s", tv_find)

        # See what TV files were added
        new_added_files = []
        for added_file in added_files:

            # Extract info
            ep_info = search(tv_find, added_file)
            if ep_info is None:
                continue

            # Episode
            ep_num = ep_info.group(3)
            ep_num_fix = sub('^0', '', ep_num)
            episode = "Episode %s" % ep_num_fix

            # Set title
            ep_title = "{0} ({1}, {2})".format(
                ep_info.group(1), ep_info.group(2), episode)

            # Append to new array
            new_added_files.append(ep_title)

        # Make sure we found episodes
        if len(new_added_files) == 0:
            return self._match_error(', '.join(added_files))

        return new_added_files, skipped_files
