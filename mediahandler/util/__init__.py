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
Module: mediahandler.util

This module contains submodules which provide utility functions to the
main mediahandler object.

Submodules:

    - |mediahandler.util.args|
        Retrieves and parses argument input from the CLI.

    - |mediahandler.util.config|
        Retrieves and parses user settings from the configuration
        file provided.

    - |mediahandler.util.extract|
        Uses Filebot to extract compressed files for processing.

    - |mediahandler.util.notify|
        Sends push notifications out via 3rd party services.

    - |mediahandler.util.torrent|
        Removes torrents from Deluge upon completion.

'''
