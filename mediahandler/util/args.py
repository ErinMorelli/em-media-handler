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
from os import path
from getopt import getopt, GetoptError


# ======== COMMAND LINE USAGE ======== #

def show_usage(code, msg=None):
    '''Show command line usage'''
    mtypes = mh.__mediakeys__
    types = []
    # Get list of types
    for mtype in sorted(mtypes):
        types.append("%s : %s" % (mtype, mtypes[mtype]))
    # Generate usage text
    usage_text = '''
EM Media Handler v%s / by %s

USAGE:
        addmedia --files /path/to/files --type [TYPE] [OPTIONS]


OPTIONS:
        -h / --help        : Displays this help info
        -f / --files=      : (required) Set path to media files
                              Assumes structure /path/to/<type name>/<media>
        -t / --type=       : Force a specific media type for processing
                              e.g. --type 1 for a TV Show
        -c / --config=     : Set a custom config file path
        -q / --query=      : Set a custom query string for audiobooks
                              Useful for for fixing "Unable to match" errors
        -s / --single      : Force beet to import music as a single track
        -n / --nopush      : Disable push notifications
                              Overrides the "enabled" config file setting

TYPES:
        %s

    ''' % (mh.__version__, mh.__author__, '\n\t'.join(types))
    # Print error, if it exists
    if msg is not None:
        print "\nERROR: %s\n" % msg
    # Output text
    print usage_text
    # Exit program
    sys.exit(int(code))


# ======== GET ARGUMENTS ======== #

def get_arguments():
    '''Get arguments'''
    use_deluge = False
    # Parse args
    try:
        (optlist, get_args) = getopt(
            sys.argv[1:],
            'hf:c:t:q:sdn',
            ["help",
             "files=",
             "config=",
             "type=",
             "query=",
             "single",
             "nopush"]
        )
    except GetoptError as err:
        show_usage(2, str(err))
    # Check for failure conditions
    if len(optlist) > 0 and len(get_args) > 0:
        show_usage(2)
    if len(optlist) == 0 and len(get_args) == 0:
        show_usage(2)
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
        show_usage(2)
    # Check for CLI
    if len(optlist) > 0:
        new_args = parse_arguments(optlist)
    new_args['use_deluge'] = use_deluge
    return new_args


# ======== PARSE ARGUMENTS ======== #

def parse_arguments(optlist):
    '''Parse arguments'''
    new_args = {}
    f_flag = False
    for opt, arg in optlist:
        if opt in ("-h", "--help"):
            show_usage(1)
        elif opt in ("-f", "--files"):
            f_flag = True
            new_args['media'] = path.abspath(arg)
        elif opt in ("-c", "--config"):
            new_args['config'] = arg
        elif opt in ("-q", "--query"):
            new_args['search'] = arg
        elif opt in ("-s", "--single"):
            new_args['single_track'] = True
        elif opt in ("-n", "--nopush"):
            new_args['no_push'] = True
        elif opt in ("-t", "--type"):
            if arg not in mh.__mediakeys__:
                show_usage(2, ("Media type not valid: %s" % arg))
            new_args['type'] = mh.__mediakeys__[arg]
    if not f_flag:
        show_usage(2, "Files not specified")
    return new_args
