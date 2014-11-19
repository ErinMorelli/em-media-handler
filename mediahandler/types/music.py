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
'''Music media type module'''

# ======== IMPORT MODULES ======== #

import re
import logging
from os import path, makedirs
from subprocess import Popen, PIPE


# ======== ADD MUSIC ======== #

def get_music(file_path, settings, is_single=False):
    '''Add music to beets library'''
    logging.info("Starting music information handler")
    # Beet Options
    beet = "/usr/local/bin/beet"
    beetslog = '%s/logs/beets.log' % path.expanduser("~")
    # Check for custom path in settings
    if settings['log_file'] != '':
        beetslog = settings['log_file']
        logging.debug("Using custom beets log: %s", beetslog)
    # Check that log file path exists
    beetslog_dir = path.dirname(beetslog)
    if not path.exists(beetslog_dir):
        makedirs(beetslog_dir)
    # Set Variables
    if is_single:
        m_tags = "-sql"
        m_query = r"Tagging track\:\s(.*)\nURL\:\n\s{1,4}(.*)\n"
    else:
        m_tags = "-ql"
        m_query = r"(Tagging|To)\:\n\s{1,4}(.*)\nURL\:\n\s{1,4}(.*)\n"
    # Set up query
    m_cmd = [beet,
             "import", file_path,
             m_tags, beetslog]
    logging.debug("Query: %s", m_cmd)
    # Process query
    m_open = Popen(m_cmd, stdout=PIPE, stderr=PIPE)
    # Get output
    (output, err) = m_open.communicate()
    logging.debug("Query output: %s", output)
    logging.debug("Query return errors: %s", err)
    # Check for skip
    skips = re.findall(r"(Skipping\.)\n", output)
    logging.info("Beets skipped %s items", len(skips))
    # Extract Info
    music_find = re.compile(m_query)
    logging.debug("Search query: %s", m_query)
    # Format data
    music_data = music_find.findall(output)
    logging.info("Additions detected: %s", music_data)
    # Get results
    results = ''
    has_skips = False
    if len(music_data) > 0:
        for music_item in music_data:
            results = results + ("%s\n\t" % music_item[0])
    if len(skips) > 0:
        has_skips = True
        results = results + ("\n%s items were skipped (see beets log)"
                             % len(skips))
    # Return error if nothing found
    if len(skips) == 0 and len(music_data) == 0:
        return None
    # Return results
    return has_skips, results
