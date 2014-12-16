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


# ======== MEDIA MODULE SHARED FUNCTIONS ======== #

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
    query = r"\[%s\] Rename \[.*\] to \[(.*)\]" % action
    file_info = search(query, output)
    if file_info is None:
        return None
    new_file = file_info.group(1)
    # Return new file
    return new_file
