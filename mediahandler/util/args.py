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
Module: mediahandler.util.args

Module contains:

    - |MHParser|
        Custom argparse.ArgumentParser child object.
          - |get_parser()|
              Retrieves full parser object for CLI args.
          - |get_deluge_parser|
              Retrieves abbreviated parser for Deluge args.

    - Custom argparse.Action validation objects
        - |MHMediaAction|
            For parsing media path structure.
        - |MHFilesAction|
            For checking if files or folders exist.
        - |MHTypeAction|
            For validating media type.

    - Argument validation wrapper functions:
        - |get_arguments()|
            Wrapper for the 'addmedia' CLI.
        - |get_deluge_arguments()|
            Wrapper for the 'addmedia-deluge' CLI.
        - |get_add_media_args()|
            Wrapper for the mediahandler.handler.add_media() function.

'''

import sys
import argparse
from os import path
from re import match, I

import mediahandler as mh
import mediahandler.util.config as Config
import mediahandler.util.torrent as Torrent


# Custom argparse validation

class MHMediaAction(argparse.Action):
    '''Custom media validation action for argparse.

    A child object of argparse.Action().
    '''

    def __call__(self, parser, namespace, values, option_string=None):
        '''Parses the directory structure of the media files submitted to
        detect the media type and name. Sets the 'name' and 'media' values
        into the argparse.Namespace() object.

        Assumes directory structure: ::

            /path/to/<media type>/<media name>

        '''

        # Retrieve full absolute file path
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

            # Make sure type provided is a valid one
            if tmp_type.lower() not in mh.__mediatypes__:
                err = "Detected media type '{0}' not recognized: {1}".format(
                    tmp_type, values)
                parser.error(err)

            # Convert type & set values
            _convert_type(namespace, tmp_type)

            # Check for success
            if 'stype' not in namespace:
                error = 'Unable to detect media type from path: {0}'.format(
                    values)
                parser.error(error)

        # Set path value
        setattr(namespace, self.dest, values)

        return


class MHFilesAction(argparse.Action):
    '''Custom files and folders validation action for argparse.

    A child object of argparse.Action().
    '''

    def __call__(self, parser, namespace, values, option_string=None):
        '''Checks that file or folder provided exists.
        '''

        # Retrieve full absolute file path
        file_path = path.abspath(values)

        # Check that the path exists
        if not path.exists(file_path):
            error = "File or directory provided for {0} {1} {2}".format(
                self.dest, 'does not exist:', values)
            parser.error(error)

        # Set value in namespace object
        setattr(namespace, self.dest, values)

        return


class MHTypeAction(argparse.Action):
    '''Custom media type validation action for argparse.

    A child object of argparse.Action().
    '''

    def __call__(self, parser, namespace, values, option_string=None):
        '''Check that media type provided is valid. Retrieves the string
        value of the media type based on the int provided. Sets the 'type'
        and 'stype' values into the argparse.Namespace() object.
        '''

        # Check that types provided is valid
        if values not in mh.__mediakeys__:
            parser.error("Media type not valid: {0}".format(values))

        # Set values in namespace object
        setattr(namespace, self.dest, values)
        setattr(namespace, 'stype', mh.__mediakeys__[values])

        return


def _convert_type(namespace, raw_type):
    '''Parses a media type string. Retrieves the correct 'stype' and 'type'
    values and adds them to an argparse.Namespace() object.

    Required arguments:
        - namespace
            The argparse.Namespace() object to updated.
        - raw_type
            The raw media type string to be parsed.
    '''

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

    return


# Custom argparse objects

class MHParser(argparse.ArgumentParser):
    '''A child object of argparse.ArgumentParser().

    Extends the following methods:
        - parse_known_args()
        - error()
        - print_help()
    '''

    def parse_known_args(self, args=None, namespace=None):
        '''Saves  the array of args as 'entered' to the argparse.Namespace()
        object for use in the MHMediaAction() object. Removes the added values
        before returning the validated args.

        Extends the argparse.ArgumentParser() method.
        '''

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

        return args, argv

    def error(self, message):
        '''Displays a simple help message via stdout before error messages.

        Overrides the argparse.ArgumentParser() method.
        '''

        # Print simple help message
        sys.stdout.write('Use `addmedia --help` to view more options\n')

        sys.exit('addmedia: error: {0}'.format(message))

    def print_help(self, files=None):
        '''Makes the printed help message look nicer by adding padding before
        and after the text and by adding the program's title and version
        information in the header.

        Extends the argparse.ArgumentParser() method.
        '''

        # Print header before help ouput
        sys.stdout.write('\nEM Media Handler v{0} / by {1}\n\n'.format(
            mh.__version__, mh.__author__))

        # Call super
        super(MHParser, self).print_help(files)

        # Add another line of padding
        sys.stdout.write('\n')

        return


def get_parser():
    '''Returns the custom MHParser object for mediahandler usage.

    Sets up the MHParser object details and adds all of the arguments used
    by the mediahandler CLI 'addmedia' script.
    '''

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

    # Create main options group
    options = parser.add_argument_group('options')

    # Required media option
    options.add_argument(
        'media',
        help=(
            'REQUIRED. Set path to media files.\n' +
            'Assumes structure: /path/to/<media type>/<media>\n '),
        action=MHMediaAction,
    )

    # Type option
    options.add_argument(
        '-t', '--type',
        help=(
            'Force a specific media type (see below).\n' +
            'Default: <media type> derived from --files path\n '),
        type=int, choices=[1, 2, 3, 4],
        action=MHTypeAction
    )

    # Custom config file option
    options.add_argument(
        '-c', '--config', default=Config.make_config(),
        help=(
            'Set a custom config file path.\n' +
            'Default: ~/.config/mediahandler/config.yml\n '),
        action=MHFilesAction,
    )

    # Audiobook query option
    options.add_argument(
        '-q', '--query',
        help=(
            'Set a custom query string for audiobooks.\n' +
            'Useful for fixing "Unable to match" errors.\n '),
    )

    # Single track processing option
    options.add_argument(
        '-s', '--single', default=False,
        help=(
            'Force beets to import music as a single track.\n' +
            'Useful for fixing "items were skipped" errors.\n '),
        dest='single_track', action='store_true',
    )

    # Disable push notification option
    options.add_argument(
        '-n', '--nopush', default=False,
        help=(
            'Disable push notifications.\n' +
            'Overrides the "enabled" config file setting.\n '),
        dest='no_push', action='store_true',
    )

    # Show help option
    options.add_argument(
        '-h', '--help',
        help='Show this help message and exit\n ',
        action='help'
    )

    return parser


def get_deluge_parser():
    '''Returns the custom MHParser object for mediahandler usage.

    Sets up the MHParser object details and adds all of the arguments used
    by the mediahandler CLI 'addmedia-deluge' script.
    '''

    # Initialize deluge parser
    parser = MHParser(
        prog='addmedia-deluge',
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
        usage='%(prog)s [TORRENT ID] [TORRENT NAME] [TORRENT PATH]',
        epilog=(
            'For use with the "Torrent Complete" event ' +
            'in Deluge\'s "Execute" plugin.\nMore info: ' +
            'http://em-media-handler.rtfd.org/en/latest/' +
            'configuration/deluge.html'),
    )

    # Create main options group
    deluge_args = parser.add_argument_group('deluge options')

    # Torrent ID
    deluge_args.add_argument(
        'hash', metavar='TORRENT ID',
        help="The torrent's unique, identifying hash.")

    # Torrent Name
    deluge_args.add_argument(
        'name', metavar='TORRENT NAME',
        help='Name of the file or folder downloaded.')

    # Torrent Path
    deluge_args.add_argument(
        'path', metavar='TORRENT PATH', action=MHFilesAction,
        help='Path to where file or folder was downloaded to.')

    return parser


# Argument parser wrapper functions

def get_deluge_arguments():
    '''Retrieves CLI arguments from the 'addmedia-deluge' script and uses
    get_deluge_parser() to validate them.

    Returns the full file path to the config file in use and a dict of
    validated arguments from the MHParser object. Also removes the torrent
    from Deluge, if the user's settings allow it.
    '''

    # Retreive full parser
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

    # Remove config to return separately
    config = all_args.pop('config')

    # Remove torrent
    settings = Config.parse_config(config)['Deluge']
    if settings['enabled']:
        Torrent.remove_deluge_torrent(settings, new_args['hash'])

    return config, all_args


def get_arguments(deluge=False):
    '''Retrieves CLI arguments from the 'addmedia' script and uses
    get_parser() to validate them.

    Returns the full file path to the config file in use and a dict of
    validated arguments from the MHParser object.
    '''

    # Check for deluge
    if deluge:
        return get_deluge_arguments()

    # Get parser
    parser = get_parser()

    # If no args, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Get validated args from parser
    new_args = parser.parse_args().__dict__

    # Remove config to return separately
    config = new_args.pop('config')

    return config, new_args


def get_add_media_args(media, **kwargs):
    '''Takes arguments passed in from the mediahandler.handler.add_media()
    function, formats them into an array, and sends them to get_parser()
    for validation.

    Returns a dict of validated arguments from the MHParser object.
    '''

    # Set up args from input
    args = [media]
    for key, value in kwargs.items():

        # Skip if value is null
        if not value:
            continue

        # Set up flag & append to args array
        flag = '--{0}'.format(key)
        args.append(flag)

        #
        if type(value) is not bool:
            args.append(str(value))

    # Set up parser
    parser = get_parser()

    # Get validated args from parser
    new_args = parser.parse_args(args).__dict__

    # Remove config to return separately
    new_args.pop('config')

    return new_args
