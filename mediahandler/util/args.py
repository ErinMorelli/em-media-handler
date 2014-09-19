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
'''Get command line args'''


# ======== IMPORT MODULES ======== #

import sys
import mediahandler as mh
from getopt import getopt, GetoptError
from mediahandler.util.notify import push


# ======== COMMAND LINE USAGE ======== #

def __show_usage(code):
    '''Show command line usage'''
    usage_text = '''
EM Media Handler v%s / by %s

Usage:
        mediaHandler.py -f /path/to/file [..options]


Options:
        -f     : (required) Set path to media files
                  Assumes path structure /path/to/<media type>/<media name>
        -c     : Set a custom config file path
        -t     : Force a specific media type for processing


Media types:
        %s
    ''' % (mh.__version__, mh.__author__, '\n\t'.join(mh.typeslist))
    # Output text
    print usage_text
    # Exit program
    sys.exit(int(code))


# ======== GET ARGUMENTS ======== #

def get_arguments():
    '''Parse arguments'''
    use_deluge = False
    # Parse args
    try:
        (optlist, get_args) = getopt(sys.argv[1:], 'f:c:t:')
    except GetoptError as err:
        print str(err)
        __show_usage(2)
    # Check for failure conditions
    if len(optlist) > 0 and len(get_args) > 0:
        __show_usage(2)
    if len(optlist) == 0 and len(get_args) == 0:
        __show_usage(2)
    # Check for deluge
    if len(get_args) == 3:
        # Treat like deluge
        use_deluge = True
        new_args = {
            'hash': get_args[0],
            'name': get_args[1],
            'path': get_args[2]
        }
    elif len(get_args) > 0:
        __show_usage(2)
    # Check for CLI
    if len(optlist) > 0:
        new_args = {}
        f = False
        for o, a in optlist:
            if o == '-f':
                f = True
                new_args['media'] = a
            if o == '-c':
                new_args['config'] = a
            if o == '-t':
                if a not in mh.typeslist:
                    push.failure('Media type %s not recognized' % a)
                new_args['type'] = a
        if not f:
            print 'option -f not specified'
            __show_usage(2)
    return use_deluge, new_args
