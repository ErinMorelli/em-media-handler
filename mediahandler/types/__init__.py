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
'''Media types module'''


# ======== IMPORT MODULES ======== #

import logging
from re import search
from subprocess import Popen, PIPE


# ======== GET MEDIA INFO FROM FILEBOT ======== #

def getinfo(m_format, m_db, file_path):
    '''Get video info from filebot'''
    logging.info("Getting video media information")
    # Filebot Options
    filebot = "/usr/bin/filebot"
    action = "COPY"
    strict = "-non-strict"
    analytics = "-no-analytics"
    # Set up query
    m_cmd = [filebot,
             "-rename", file_path,
             "--db", m_db,
             "--format", m_format,
             "--action", action.lower(),
             strict, analytics]
    logging.debug("Query: %s", m_cmd)
    # Process query
    m_open = Popen(m_cmd, stdout=PIPE)
    # Get output
    (output, err) = m_open.communicate()
    logging.debug("Query output: %s", output)
    logging.debug("Query return errors: %s", err)
    # Process output
    (new_file, skips) = __process_output(output, action)
    # Return new file
    return new_file, skips


# ======== PROCESS FILEBOT OUTPUT ======== #

def __process_output(output, action):
    '''Check for good response or skipped content'''
    logging.info("Processing query output")
    new_file = None
    skipped = False
    # Set up regexes
    good_query = r"\[%s\] Rename \[.*\] to \[(.*)\]" % action
    skip_query = r"Skipped \[(.*)\] because \[(.*)\] already exists"
    # Look for content
    get_good = search(good_query, output)
    get_skip = search(skip_query, output)
    # Check return
    if get_good is not None:
        new_file = get_good.group(1)
    elif get_skip is not None:
        skipped = True
        new_file = get_skip.group(2)
        logging.warning("Duplicate file was skipped: %s", new_file)
    # Return info
    return new_file, skipped
