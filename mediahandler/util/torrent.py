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
'''Deluge-specific functions'''

import sys
import logging
import argparse
from os import path

import mediahandler as mh
import mediahandler.util.args as Args
import mediahandler.util.config as Config


# ======== GET DELUGE PARSER ======== #

def get_deluge_parser():
    parser = Args.MHParser(
        prog='addmedia-deluge',
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
        usage='%(prog)s [TORRENT ID] [TORRENT NAME] [TORRENT PATH]',
        epilog=('For use with the "Torrent Complete" event ' +
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
        'path', metavar='TORRENT PATH', action=Args.MHFilesAction,
        help='Path to where file or folder was downloaded to.')
    return parser


# ======== GET DELUGE ARGUMENTS ======== #

def get_deluge_arguments(): 
    parser = get_deluge_parser()
    # If no args, show help
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    # Get and return args
    get_args = parser.parse_args()
    new_args = vars(get_args)
    # Use main parser
    get_all_args = Args.get_parser().parse_args(
        args=['-f', path.join(new_args['path'], new_args['name'])],
    )
    all_args = vars(get_all_args)
    # Remove torrent
    settings = Config.parse_config(all_args['config'])['Deluge']
    if settings['enabled'] and settings['remove']:
        _remove_torrent(settings, new_args['hash'])
    # Return args
    return all_args


# ======== REMOVE TORRENT ======== #

def _remove_torrent(settings, torrent_hash):
    '''Remove torrent'''
    logging.info("Removing torrent from Deluge")
    # Import modules
    from twisted.internet import reactor
    from deluge.ui.client import client
    # Connect to Deluge daemon
    deluge = client.connect(
        host=settings['host'],
        port=settings['port'],
        username=settings['user'],
        password=settings['pass']
    )

    # We create a callback function to be called upon a successful connection
    def on_connect_success(result):
        '''Connect success callback'''
        logging.debug("Connection was successful: %s", result)

        def on_remove_torrent(success):
            '''On remove callback'''
            if success:
                logging.debug("Torrent remove successful")
            else:
                logging.warning("Torrent remove unsuccessful")
            # Disconnect from the daemon & exit
            client.disconnect()
            reactor.stop()

        def on_get_session_state(torrents):
            '''On session state callback'''
            found = False
            # Look for completed torrent in list
            for tor in torrents:
                if tor == torrent_hash:
                    # Set as found and call remove function
                    logging.debug("Torrent found")
                    found = True
                    client.core.remove_torrent(
                        torrent_hash,
                        False).addCallback(
                            on_remove_torrent)
                    break
            if not found:
                logging.warning("Torrent not found")
                # Disconnect from the daemon & exit
                client.disconnect()
                reactor.stop()
        # Get list of current torrent hashes
        client.core.get_session_state().addCallback(on_get_session_state)
    # We add the callback to the Deferred object we got from connect()
    deluge.addCallback(on_connect_success)

    # To be called when an error is encountered
    def on_connect_fail(result):
        '''Connect fail callback'''
        logging.error("Connection failed: %s", result)
        reactor.stop()
    # We add the callback (in this case it's an errback, for error)
    deluge.addErrback(on_connect_fail)
    # Run the twisted main loop to make everything go
    reactor.run()
