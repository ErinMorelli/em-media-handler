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
Module: mediahandler.util.extract

Module contains:
    - |get_files()|
        extracts compressed files via Filebot.

'''

import logging
from re import search
from subprocess import Popen, PIPE


def get_files(filebot, file_name):
    '''Extracts compressed files via Filebot.

    Required arguments:
        - filebot
            Path to valid Filebot application script.
        - file_name
            Path to valid compressed file for extraction.
    '''

    logging.info("Getting files from compressed folder")

    # Set up query
    m_cmd = [filebot,
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

    return new_files
