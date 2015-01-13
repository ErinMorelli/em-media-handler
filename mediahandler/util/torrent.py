#!/usr/bin/python
#
# This file is a part of EM Media Handler
# Copyright (c) 2015 Erin Morelli
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
from os import path

import mediahandler as mh
import mediahandler.util.config as Config


# ======== COMMAND LINE USAGE ======== #

def show_deluge_usage(code, msg=None):
    '''Show command line usage'''
    # Generate usage text
    usage_text = '''
EM Media Handler v%s / by %s

Usage:
        addmedia-deluge [Torrent ID] [Torrent Name] [Torrent Path]

''' % (mh.__version__, mh.__author__)
    # Print error, if it exists
    if msg is not None:
        print "\nERROR: %s\n" % msg
    # Output text
    print usage_text
    # Exit program
    sys.exit(int(code))


# ======== GET DELUGE ARGUMENTS ======== #

def get_deluge_arguments():
    '''Get arguments from deluge'''
    # Parse args
    get_args = sys.argv[1:]
    # Check for failure conditions
    if len(get_args) == 0:
        show_deluge_usage(1)
    elif len(get_args) != 3:
        show_deluge_usage(2, "Deluge script requires 3 args")
    # Set args
    new_args = {
        'hash': get_args[0],
        'name': get_args[1],
        'path': get_args[2]
    }
    # Return processed args
    return _process_deluge(new_args)


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


# ======== PROCESS DELUGE ARGS ======== #

def _process_deluge(args):
    # Get settings
    config_file = Config.make_config()
    settings = Config.parse_config(config_file)
    # Set file path based on args
    logging.info("Processing from deluge")
    file_path = path.join(args['path'], args['name'])
    # Remove torrent
    if settings['Deluge']['enabled']:
        _remove_torrent(settings['Deluge'], args['hash'])
    # Set modified args
    new_args = {
        'media': file_path,
        'name': args['name'],
        'no_push': False,
        'single_track': False,
    }
    # Return handler-ready
    return new_args
