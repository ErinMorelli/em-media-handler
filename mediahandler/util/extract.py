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
'''File extraction module'''


# ======== IMPORT MODULES ======== #

import logging
from re import search
from subprocess import Popen, PIPE


# ======== GET FILES ======== #

def get_files(file_name):
    '''Extract files'''
    logging.info("Getting files from compressed folder")
    # Filebot path
    __filebot = "/usr/bin/filebot"
    # Set up query
    m_cmd = [__filebot,
             "-extract",
             file_name]
    logging.debug("Query: %s", m_cmd)
    # Process query
    m_open = Popen(m_cmd, stdout=PIPE)
    # Get output
    (output, err) = m_open.communicate()
    logging.debug("Filebot output: %s", output)
    logging.debug("Filebot return errors: %s", err)
    # Process output
    file_info = search(r"extract to \[(.*)\]\n", output)
    if file_info is None:
        return None
    # Set new files
    new_files = file_info.group(1)
    logging.debug("Extracted files: %s", new_files)
    # Return path of extracted files
    return new_files
