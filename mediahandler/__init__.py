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
'''Initialize module'''

from os.path import join, dirname

__version__ = '0.5.1'
__author__ = 'Erin Morelli <erin@erinmorelli.com>'


# Globally acceptable media types & their CLI keys
__mediakeys__ = {
    "1": "TV",
    "2": "Movies",
    "3": "Music",
    "4": "Audiobooks"
}

# Globally acceptable media type names
__mediatypes__ = [
    'tv',
    'tv shows',
    'television',
    'movies',
    'music',
    'books',
    'audiobooks'
]

__mediaextras__ = join(dirname(__file__), 'extras')
