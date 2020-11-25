#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is a part of EM Media Handler
# Copyright (c) 2014-2019 Erin Morelli
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
"""
Module: mediahandler.util.torrent

Module contains:
    - |remove_deluge_torrent()|
        Removes a torrent from Deluge.

"""

import random
import logging
import requests


def remove_deluge_torrent(settings, torrent_hash):
    """Removes a torrent from Deluge.

    Required arguments:
        - settings
            Dict or MHSettings object for Deluge info.
        - torrent_hash
            Valid hash of active torrent to be removed.

    Makes an API request to the Deluge client.
    """

    logging.info("Removing torrent from Deluge")

    # Set up request URL
    url = '{ssl}://{host}{endpoint}'.format(
        ssl='https' if settings['ssl'] else 'http',
        host=settings['host'],
        endpoint=settings['endpoint']
    )

    # Get a unique request ID
    req_id = random.getrandbits(10)

    # Make the request
    try:
        res = requests.post(
            url=url,
            json={
                'id': req_id,
                'method': 'core.remove_torrent',
                'params': [torrent_hash, False]
            }
        )
        res.raise_for_status()
    except requests.RequestException as exc:
        logging.warning("Torrent remove unsuccessful: %s", exc)
        return
    else:
        # Check result
        if res.status_code == 200:
            logging.warning("Torrent remove successful: %s", res.json())
        else:
            logging.debug("Torrent remove unsuccessful")
