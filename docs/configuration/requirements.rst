Installation Requirements
============================================

This is a list of required python packages and 3rd party applications needed by the various parts of EM Media Handler. They are broken down by which configuration section needs them when enabled:

General
*******
* `PyYAML <http://pyyaml.org/>`_ (automatically installed) ::

    pip install pyyaml

TV and Movies
*************
* `Filebot <http://www.filebot.net/>`_


Music
*****
* `Beets <http://beets.radbox.org/>`_ ::

    pip install beets


Audiobooks
**********
* `Google API Python Client <https://developers.google.com/api-client-library/python/>`_ (automatically installed) ::

    pip install google-api-python-client

* Mutagen (automatically installed) ::

    pip install mutagen

* `ABC <http://www.ausge.de/ausge-download/abc-info-english>`_ (for when ``make_chapters`` is enabled)
   Detailed installation instructions can be `found here <http://www.ausge.de/ausge-download/abc-info-english>`_.


Notifications
**************
* `Requests <http://docs.python-requests.org/en/latest>`_ (automatically installed) ::

    pip install requests


Deluge
*******
* Twisted ::

    pip install twisted

* `Deluge <http://deluge-torrent.org>`_
   Needs to be installed from source using the directions you can `find here <http://dev.deluge-torrent.org/wiki/Installing/Source>`_.

