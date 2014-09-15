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

# ======== IMPORT MODULES ======== #

import logging
from re import search
from subprocess import Popen, PIPE


# ======== GET FILES ======== #

def getFiles(fileName):
    logging.info("Getting files from compressed folder")
    # Filebot path
    __filebot = "/usr/bin/filebot"
    # Set up query
    mCMD = [__filebot,
            "-extract",
            fileName]
    logging.debug("Query: %s", mCMD)
    # Process query
    p = Popen(mCMD, stdout=PIPE)
    # Get output
    (output, err) = p.communicate()
    logging.debug("Query output: %s", output)
    logging.debug("Query return errors: %s", err)
    # Process output
    fileInfo = search(r"Extracting files \[(.*)\]\n", output)
    if fileInfo is None:
        return None
    extracted = fileInfo.group(1)
    # Break into array
    newFiles = extracted.split(", ")
    # Return array of extracted files
    return newFiles
