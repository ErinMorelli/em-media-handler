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


# ======== IMPORT MODULES ======== #

import logging

from twisted.internet import reactor
from deluge.ui.client import client


# ======== REMOVE TORRENT ======== #

def removeTorrent(settings, torrentHash):
    logging.info("Removing torrent from Deluge")
    # Connect to Deluge daemon
    d = client.connect(
        host=settings['host'],
        port=int(settings['port']),
        username=settings['user'],
        password=settings['pass']
    )

    # We create a callback function to be called upon a successful connection
    def on_connect_success(result):
        logging.debug("Connection was successful!")

        def on_remove_torrent(success):
            if success:
                logging.debug("Torrent remove successful")
            else:
                logging.warning("Torrent remove unsuccessful")
            # Disconnect from the daemon & exit
            client.disconnect()
            reactor.stop()

        def on_get_session_state(torrents):
            found = False
            # Look for completed torrent in list
            for t in torrents:
                if t == torrentHash:
                    # Set as found and call remove function
                    logging.debug("Torrent found")
                    found = True
                    client.core.remove_torrent(
                        torrentHash,
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
    d.addCallback(on_connect_success)

    # To be called when an error is encountered
    def on_connect_fail(result):
        logging.error("Connection failed: %s", result)
    # We add the callback (in this case it's an errback, for error)
    d.addErrback(on_connect_fail)
    # Run the twisted main loop to make everything go
    reactor.run()
