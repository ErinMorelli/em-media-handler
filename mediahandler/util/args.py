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


# ======== COMMAND LINE USAGE ======== #

def __show_usage(code):
    '''Show command line usage'''
    mtypes = mh.__mediakeys__
    types = []
    # Get list of types
    for mtype in mtypes:
        types.append( "%s : %s" % (mtype, mtypes[mtype]) )
    # Generate usage text
    usage_text = '''
EM Media Handler v%s / by %s

Usage:
        addmedia --files=/path/to/files --type=1 [..options]


Options:
        -f / --files=     : (required) Set path to media files
                            Assumes path structure /path/to/<media type>/<media name>
        -c / --config=    : Set a custom config file path
        -t / --type=      : Force a specific media type for processing


Media types:
        %s
    ''' % (mh.__version__, mh.__author__, '\n\t'.join(types))
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
        (optlist, get_args) = getopt(sys.argv[1:], 'hf:c:t:', ["help", "files=", "config=", "type="])
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
        f_flag = False
        for opt, arg in optlist:
            if opt in ( "-f", "--files" ):
                f_flag = True
                new_args['media'] = arg
            if opt in ( "-c", "--config" ):
                new_args['config'] = arg
            if opt in ( "-t", "--type" ):
                if arg not in mh.__mediakeys__:
                    print '\nERROR: Media type not valid: %s' % arg
                    __show_usage(2)
                new_args['type'] = mh.__mediakeys__[arg]
        if not f_flag:
            print '\nERROR: Files not specified'
            __show_usage(2)
    return use_deluge, new_args
