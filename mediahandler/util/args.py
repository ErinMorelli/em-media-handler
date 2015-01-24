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
import mediahandler.util.torrent as Torrent


# ======== CUSTOM ARGPARSE ACTIONS ======== #

class MHMediaAction(argparse.Action):
    '''Custom media validation action for argparse'''

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
        if not [i for i in ['-t', '--type'] if i in namespace.entered]:
            tmp_type = path.basename(parse_path)
            if tmp_type.lower() not in mh.__mediatypes__:
                err = "Detected media type '{0}' not recognized: {1}".format(
                    tmp_type, values)
                parser.error(err)
            # Convert type & set values
            convert_type(namespace, tmp_type)
            # Check for success
            if 'stype' not in namespace:
                error = 'Unable to detect media type from path: {0}'.format(
                    values)
                parser.error(error)
        # Set path value
        setattr(namespace, self.dest, values)


class MHFilesAction(argparse.Action):
    '''Custom files/folders validation action for argparse'''

    def __call__(self, parser, namespace, values, option_string=None):
        '''Check that file/folder provided exists'''
        file_path = path.abspath(values)
        if not path.exists(file_path):
            error = "File or directory provided for {0} {1} {2}".format(
                self.dest, 'does not exist:', values)
            parser.error(error)
        setattr(namespace, self.dest, values)


class MHTypeAction(argparse.Action):
    '''Custom type validation action for argparse'''

    def __call__(self, parser, namespace, values, option_string=None):
        '''Check that type provided is good and set string value'''
        if values not in mh.__mediakeys__:
            parser.error("Media type not valid: {0}".format(values))
        setattr(namespace, self.dest, values)
        setattr(namespace, 'stype', mh.__mediakeys__[values])


class MHParser(argparse.ArgumentParser):
    '''Custom ArgumentParser instance for needed overrides'''

    def parse_known_args(self, args=None, namespace=None):
        '''Save all inputs to namespace for custom media validation'''
        # args default to the system args
        if args is None:
            args = sys.argv[1:]
        # default Namespace built from parser defaults
        if namespace is None:
            namespace = argparse.Namespace()
        # Save args
        setattr(namespace, 'entered', args)
        # Call super
        (args, argv) = super(MHParser, self).parse_known_args(args, namespace)
        # Remove added attribute
        delattr(args, 'entered')
        # Return
        return args, argv

    def error(self, message):
        '''Show help with error messages'''
        sys.stdout.write('Use `addmedia --help` to view more options\n')
        sys.exit('addmedia: error: %s' % message)

    def print_help(self, files=None):
        '''Make the print help look prettier'''
        sys.stdout.write('\nEM Media Handler v{0} / by {1}\n\n'.format(
            mh.__version__, mh.__author__))
        super(MHParser, self).print_help(files)
        sys.stdout.write('\n')


# ======== CONVERT TYPE ======== #

def convert_type(namespace, raw_type):
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


# ======== GET ARGPARSER ======== #

def get_parser():
    '''Returns custom parser object'''
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
        help=(
            'REQUIRED. Set path to media files.\n' +
            'Assumes structure: /path/to/<media type>/<media>\n '),
        action=MHMediaAction,
    )
    options.add_argument(
        '-t', '--type',
        help=(
            'Force a specific media type (see below).\n' +
            'Default: <media type> derived from --files path\n '),
        type=int, choices=[1, 2, 3, 4],
        action=MHTypeAction
    )
    options.add_argument(
        '-c', '--config', default=Config.make_config(),
        help=(
            'Set a custom config file path.\n' +
            'Default: ~/.config/mediahandler/config.yml\n '),
        action=MHFilesAction,
    )
    options.add_argument(
        '-q', '--query',
        help=(
            'Set a custom query string for audiobooks.\n' +
            'Useful for fixing "Unable to match" errors.\n '),
    )
    options.add_argument(
        '-s', '--single', default=False,
        help=(
            'Force beets to import music as a single track.\n' +
            'Useful for fixing "items were skipped" errors.\n '),
        dest='single_track', action='store_true',
    )
    options.add_argument(
        '-n', '--nopush', default=False,
        help=(
            'Disable push notifications.\n' +
            'Overrides the "enabled" config file setting.\n '),
        dest='no_push', action='store_true',
    )
    options.add_argument(
        '-h', '--help',
        help='Show this help message and exit\n ',
        action='help'
    )
    return parser


# ======== GET DELUGE PARSER ======== #

def get_deluge_parser():
    '''Returns custom parser object for deluge input'''
    parser = MHParser(
        prog='addmedia-deluge',
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
        usage='%(prog)s [TORRENT ID] [TORRENT NAME] [TORRENT PATH]',
        epilog=(
            'For use with the "Torrent Complete" event ' +
            'in Deluge\'s "Execute" plugin.\nMore info: ' +
            'http://dev.deluge-torrent.org/wiki/Plugins/Execute'),
    )
    deluge_args = parser.add_argument_group('deluge options')
    deluge_args.add_argument(
        'hash', metavar='TORRENT ID',
        help="The torrent's unique, identifying hash.")
    deluge_args.add_argument(
        'name', metavar='TORRENT NAME',
        help='Name of the file or folder downloaded.')
    deluge_args.add_argument(
        'path', metavar='TORRENT PATH', action=MHFilesAction,
        help='Path to where file or folder was downloaded to.')
    return parser


# ======== GET DELUGE ARGUMENTS ======== #

def get_deluge_arguments():
    '''Process deluge args'''
    parser = get_deluge_parser()
    # If no args, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    # Get and return args
    new_args = parser.parse_args().__dict__
    # Use main parser
    all_args = get_parser().parse_args(
        args=[path.join(new_args['path'], new_args['name'])],
    ).__dict__
    # Remove torrent
    settings = Config.parse_config(all_args['config'])['Deluge']
    if settings['enabled'] and settings['remove']:
        Torrent.remove_deluge_torrent(settings, new_args['hash'])
    # Return args
    config = all_args.pop('config')
    return config, all_args


# ======== GET ARGUMENTS ======== #

def get_arguments(deluge):
    '''Get arguments'''
    # Check for deluge
    if deluge:
        return Torrent.get_deluge_arguments()
    # Get parser
    parser = get_parser()
    # If no args, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    # Get & return args
    new_args = parser.parse_args().__dict__
    config = new_args.pop('config')
    return config, new_args


# ======== GET ARGUMENTS ======== #

def get_add_media_args(media, **kwargs):
    '''Validate and return args from add_media function in handler'''
    args = [media]
    # Set up args from input
    for key, value in kwargs.items():
        if not value:
            continue
        flag = '--{0}'.format(key)
        args.append(flag)
        if type(value) is not bool:
            args.append(str(value))
    # Set up parser
    parser = get_parser()
    # Get & return args
    sys.argv[1:] = args
    new_args = parser.parse_args().__dict__
    new_args.pop('config')
    return new_args
