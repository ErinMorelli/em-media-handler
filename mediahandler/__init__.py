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
Module: mediahandler

Module contains:

    - |MHObject|
        Basic object structure for all module and submodule
        classes. Contains the MHSettings object, which serves as a simple
        structure for storing data as attributes.

    - Global constants for the module and submodules.

'''

from os.path import join, dirname

__version__ = '1.0b2'
__author__ = 'Erin Morelli <erin@erinmorelli.com>'


# Globally acceptable media types & their CLI keys
__mediakeys__ = {
    1: "TV",
    2: "Movies",
    3: "Music",
    4: "Audiobooks"
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

# Set relative path to extras folder
__mediaextras__ = join(dirname(__file__), 'extras')


class MHObject(object):
    '''Base object for the mediahandler module and submodules.

    Converts arguments in the form of dict into object attributes for easier
    data manipulation.
    '''

    def __init__(self, *kwargs):
        '''Initializes MHObject class by taking in all arguments.

        Converts dicts and MHSettings into object attributes.
        '''

        # Iterate through arguments
        for kwarg in kwargs:

            # If this is a dict, send as-is to set settings
            if type(kwarg) is dict:
                self.set_settings(kwarg)

            # If this is a MHSettings object, send object vars
            if type(kwarg) is self.MHSettings:
                self.set_settings(kwarg.__dict__)

    class MHSettings(object):
        '''Object which serves as a simple structure for storing data
        as attributes.
        '''

        def __init__(self, adict):
            '''Converts a dict into object attributes.
            '''
            self.__dict__.update(adict)

    def set_settings(self, adict):
        '''Iteratively converts a dict into MHSettings objects and
        subsequently into object attributes.
        '''

        # Iterate through dict's key and value pairs
        new_dict = {}
        for key, value in adict.items():

            # If the dict has a sub dict, make a new MHSettings object
            if type(value) is dict:
                new_dict[key.lower()] = self.MHSettings(value)

            # Else keep as-is
            else:
                new_dict[key.lower()] = value

        # Make updated dicts object members
        self.__dict__.update(new_dict)
