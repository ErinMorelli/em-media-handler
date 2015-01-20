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
        types.append("{0} -- {1}".format(mtype, mtypes[mtype]))
    # Generate usage text
    usage_text = '''
EM Media Handler v{0} / by {1}

Usage:    
  addmedia --files /path/to/files --type [TYPE] [OPTIONS]

Options:
  -f, --files     Required. Set path to media files.
                  Assumes structure: /path/to/<media type>/<media>

  -t, --types     Force a specific media type for processing.
                  e.g. --type 1 for a TV Show
                  Default: <media type> derived from --files path

  -c, --config    Set a custom config file path.
                  Default: ~/.config/mediahandler/settings.conf

  -q, --query     Set a custom query string for audiobooks.
                  Useful for fixing "Unable to match" errors.

  -s, --single    Force beet to import music as a single track.
                  Useful for fixing "items were skipped" errors.

  -n, --nopush    Disable push notifications.
                  Overrides the "enabled" config file setting.

  -h, --help      Displays this usage message.

Types:
   {2}
'''.format(mh.__version__, mh.__author__, '\n   '.join(types))
    # Print error, if it exists
    if msg is not None:
        print "\nERROR: {0}\n".format(msg)
    # Output text
    print usage_text
    # Exit program
    sys.exit(int(code))


# ======== GET ARGUMENTS ======== #

def get_arguments():
    '''Get arguments'''
    # Parse args
    try:
        (optlist, get_args) = getopt(
            sys.argv[1:],
            'hf:c:t:q:sn',
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
    if len(optlist) == 0 and len(get_args) == 0:
        show_usage(2)
    # Send to parser
    return parse_arguments(optlist)


# ======== PARSE ARGUMENTS ======== #

def parse_arguments(optlist):
    '''Parse arguments'''
    # Set up base args
    new_args = {}
    new_args['no_push'] = False
    new_args['single_track'] = False
    # Parse args
    success = False
    for opt, arg in optlist:
        if opt in ("-h", "--help"):
            show_usage(1)
        # Then look for normal args
        elif opt in ("-f", "--files"):
            success = True
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
                show_usage(2, "Media type not valid: {0}".format(arg))
            new_args['type'] = mh.__mediakeys__[arg]
    # Check for failure
    if not success:
        show_usage(2, "Files not specified")
    return new_args
