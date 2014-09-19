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

__version__ = '1.0'
__author__ = 'Erin Morelli <erin@erinmorelli.com>'


# ======== IMPORT MODULES ======== #

import logging
from re import search
from subprocess import Popen, PIPE


# ======== MEDIA MODULE SHARED FUNCTIONS ======== #

def getinfo(m_format, m_db, file_path):
    logging.info("Getting video media information")
    # Filebot Options
    __filebot = "/usr/bin/filebot"
    __action = "COPY"
    __strict = "-non-strict"
    __analytics = "-no-analytics"
    # Set up query
    m_cmd = [__filebot,
            "-rename", file_path,
            "--db", m_db,
            "--format", m_format,
            "--action", __action.lower(),
            __strict, __analytics]
    logging.debug("Query: %s", m_cmd)
    # Process query
    p = Popen(m_cmd, stdout=PIPE)
    # Get output
    (output, err) = p.communicate()
    logging.debug("Query output: %s", output)
    logging.debug("Query return errors: %s", err)
    # Process output
    query = r"\[%s\] Rename \[.*\] to \[(.*)\]" % __action
    file_info = search(query, output)
    if file_info is None:
        return None
    new_file = file_info.group(1)
    # Return new file
    return new_file
