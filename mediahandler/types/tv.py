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
'''TV media type module'''

# ======== IMPORT MODULES ======== #

import logging
from os import path
from mediahandler.types import getinfo
from re import escape, search, sub


# ======== GET EPISODE ======== #

def get_episode(file_path, settings):
    '''Get TV episode information'''
    logging.info("Starting episode information handler")
    # Default TV path
    tv_path = '%s/Media/Television' % path.expanduser("~")
    # Check for custom path in settings
    if settings['folder'] != '':
        if path.exists(settings['folder']):
            tv_path = settings['folder']
            logging.debug("Using custom path: %s", tv_path)
    # Set Variables
    tv_form = ("%s/{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}"
               % tv_path)
    tv_db = "thetvdb"
    # Get info
    new_file = getinfo(tv_form, tv_db, file_path)
    logging.debug("New file: %s", new_file)
    # Check for failure
    if new_file is None:
        return None, None
    # Set search query
    epath = escape(tv_path)
    tv_find = (r"%s\/(.*)\/(.*)\/.*\.S\d{2,4}E(\d{2,3}).\w{3}" % epath)
    logging.debug("Search query: %s", tv_find)
    # Extract info
    episode = search(tv_find, new_file)
    if episode is None:
        return None, None
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
    # Return Show Name, Season, Episode (file)
    return ep_title, new_file
