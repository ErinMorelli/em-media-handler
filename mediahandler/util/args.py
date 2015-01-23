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
import argparse
from os import path
from re import match, I
import mediahandler as mh
import mediahandler.util.config as Config


# ======== CUSTOM ARGPARSE ACTIONS ======== #

class MHMediaAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        '''Parse input directory structure'''
        rawpath = path.abspath(values)
        # Check for files existence
        if not path.exists(rawpath):
            error = "File or directory provided for {0} {1} {2}".format(
                self.dest, 'does not exist:', values)
            parser.error(error)
        # Extract info from path
        parse_name = path.basename(rawpath)
        parse_path = path.dirname(rawpath)
        # Set name
        setattr(namespace, 'name', parse_name)
        # Look for custom type
        if not [i for i in ['-t', '--type'] if i in sys.argv[1:]]:
            tmp_type = path.basename(parse_path)
            if tmp_type.lower() not in mh.__mediatypes__:
                err = "Detected media type '{0}' not recognized: {1}".format(
                    tmp_type, values)
                parser.error(err)
            # Convert type & set values
            self.convert_type(namespace, tmp_type)
            # Check for success
            if 'stype' not in namespace:
                error = 'Unable to detect media type from path: {0}'.format(values)
                parser.error(error)
        # Set path value
        setattr(namespace, self.dest, values)

    def convert_type(self, namespace, raw_type):
        '''Convert string type to int'''
        # Make lowercase for comparison
        stype = ''
        xtype = raw_type.lower()
        # Convert values
        if xtype in ['tv shows', 'television']:
            xtype = 'tv'
        elif xtype == 'books':
            xtype = 'audiobooks'
        # Look for int
        for key, value in mh.__mediakeys__.items():
            if match(value, xtype, I):
                stype = value
                xtype = int(key)
                break
        # Store string & int values
        setattr(namespace, 'type', xtype)
        setattr(namespace, 'stype', stype)


class MHFilesAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        '''Check that file/folder provided exists'''
        file_path = path.abspath(values)
        if not path.exists(file_path):
            error = "File or directory provided for {0} {1} {2}".format(
                option_string, 'does not exist:', values)
            parser.error(error)
        setattr(namespace, self.dest, values)


class MHTypeAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        '''Check that type provided is good and set string value'''
        if values not in mh.__mediakeys__:
            parser.error("Media type not valid: {0}".format(values))
        setattr(namespace, self.dest, values)
        setattr(namespace, 'stype', mh.__mediakeys__[values])


class MHParser(argparse.ArgumentParser):

    def error(self, message):
        '''Show help with error messages'''
        sys.stdout.write('Use `addmedia --help` to view more options\n')
        sys.exit('addmedia: error: %s' % message)

    def print_help(self):
        sys.stdout.write('\nEM Media Handler v{0} / by {1}\n\n'.format(
            mh.__version__, mh.__author__))
        super(MHParser, self).print_help()
        sys.stdout.write('\n')


# ======== GET ARGPARSER ======== #

def get_parser():
    mtypes = mh.__mediakeys__
    types = []
    # Get list of types
    for mtype in sorted(mtypes):
        types.append("{0} -- {1}".format(mtype, mtypes[mtype]))
    # Initialize parser
    parser = MHParser(
        prog='addmedia',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='type options:\n   {0}'.format('\n   '.join(types)),
        add_help=False,
        usage='%(prog)s MEDIA [--type TYPE] [OPTIONS]',
    )
    # Add options
    options = parser.add_argument_group('options')
    options.add_argument(
        'media',
        help=('REQUIRED. Set path to media files.\n' +
            'Assumes structure: /path/to/<media type>/<media>\n '),
        action=MHMediaAction,
    )
    options.add_argument(
        '-t', '--type',
        help=('Force a specific media type (see below).\n' +
            'Default: <media type> derived from --files path\n '),
        type=int, choices=[1, 2, 3, 4],
        action=MHTypeAction
    )
    options.add_argument(
        '-c', '--config', default=Config.make_config(),
        help=('Set a custom config file path.\n' +
            'Default: ~/.config/mediahandler/config.yml\n '),
        action=MHFilesAction,
    )
    options.add_argument(
        '-q', '--query',
        help=('Set a custom query string for audiobooks.\n' +
            'Useful for fixing "Unable to match" errors.\n '),
    )
    options.add_argument(
        '-s', '--single', default=False,
        help=('Force beets to import music as a single track.\n' +
            'Useful for fixing "items were skipped" errors.\n '),
        dest='single_track', action='store_true',
    )
    options.add_argument(
        '-n', '--nopush', default=False,
        help=('Disable push notifications.\n' +
            'Overrides the "enabled" config file setting.\n '),
        dest='no_push', action='store_true',
    )
    options.add_argument(
        '-h', '--help',
        help='Show this help message and exit\n ',
        action='help'
    )
    return parser


# ======== GET ARGUMENTS ======== #

def get_arguments():
    '''Get arguments'''
    parser = get_parser()
    # If no args, show help
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    # Get and return args
    new_args = parser.parse_args()
    return vars(new_args)
