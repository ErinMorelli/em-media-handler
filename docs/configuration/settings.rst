User Settings
============================================

An overview of all available user settings available in the user config file, which can be found here: ::

    ~/.config/mediahandler/config.yml

The configuration file uses yaml formatting, and does not require that every option is present in the file. Sections and options may be left blank or completely removed -- the application will use default values in their place.

.. contents::
    :local:

General
*******
General mediahandler script functionality options.

Default section and values: ::

    General:
        keep_files: no
        keep_if_skips: yes


keep_files
##########
Enable or disable mediahandler's removal of the originally downloaded files upon script completion.

Valid options:
    - ``no`` (default)
    - ``yes``  

keep_if_skips
#############
Enable or disable mediahandler's removal of the originally downloaded files in a situation where some of files were skipped during the script's processing.

Valid options:
    - ``no``
    - ``yes`` (default)


Deluge
******
Deluge server integration options.

Default section and values: ::

    Deluge:
        enabled: no
        host: 127.0.0.1
        port: 58846
        user: 
        pass: 

enabled
#######
Enable or disable mediahandler's ability to automatically remove a torrent from the Deluge UI when the script is executed on torrent completion.

See :doc:`/configuration/deluge` for more information on this integration.

Values
    - ``no`` (default)
    - ``yes``

host
####
The host IP/address of the running Deluge server.

Default: ``127.0.0.1``

port
####
The port number of the running Deluge server.

Default: ``58846``

user
####
The user running Deluge server (set Deluge ``auth`` file).

pass
####
The password of the user running Deluge server (set Deluge ``auth`` file).


Logging
*******
Logging output options.

Default section and values: ::

    Logging:
        enabled: yes
        level: 30
        log_file: 

enabled
#######
Enable or disable event logging of the mediahandler script.

Values:
    - ``no``
    - ``yes`` (default)

level
#####
Specify a level threshold for events logged. See `this table <https://docs.python.org/2/library/logging.html#logging-levels>`_ for possible values.

Default: ``30``

log_file
########
Specify a file path (including file name) to a custom log file destination.

Default: ``~/logs/mediahandler.log``


Notifications
*************
Options for push notification via 3rd party services. Multiple services may be used side-by-side.

Default section and values: ::

    Notifications:
        enabled: no
        notify_name: 
        pushover:
            api_key: 
            user_key: 
        pushbullet:
            token:

enabled
#######
Enable or disable push notifications upon script completion.

Values:
    - ``no`` (default)
    - ``yes``

notify_name
###########
Specify a name for notifications to use in message titles, e.g. "EM Media Handler: Media Added".

Default: ``EM Media Handler``

pushover
########
To enable Pushover integration, simple set both the ``api_key`` and ``user_key`` settings with valid credentials: ::

    Notifications:
        enabled: yes
        notify_name: My Custom Name
        pushover:
            api_key: SNAczveGbbyzUmASUljL
            user_key: AkdmliUzQZofvoYVLskG

Your ``user_key`` can be found on your `Pushover <https://pushover.net/>`_ dashboard.

Your ``api_key`` is specific to the Pushover application you would like to have the script send the notification through. Click on the application's settings to retrieve the key.


pushbullet
##########
To enable Pushbullet integration, simple set the ``token`` setting with valid credentials: ::

    Notifications:
        enabled: yes
        notify_name: My Custom Name
        pushbullet:
            token: gNJccqGqISParIqHcvRy

Your ``token`` can be found in your `Pushbullet account settings <https://www.pushbullet.com/account>`_.

EM Media Handler does not *yet* support specifying a device or channel to send Pushbullet notifications to. 


TV and Movies
*************
TV and Movies both use `Filebot <http://www.filebot.net/>`_ and are the only media type modules enabled "out of the box". Their settings are identical in function, which is why they are grouped together in this guide, but they are unique in execution to their respective type.

Default sections and values: ::

    TV:
        enabled: yes
        folder: 
        ignore_subs: yes
        format: "{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}"
        log_file:

    Movies:
        enabled: yes
        folder: 
        ignore_subs: yes
        format: "{n} ({y})"
        log_file:

enabled
#######
Enable or disable processing of media type by mediahandler.

Values:
    - ``no``
    - ``yes`` (default)

folder
######
Specify a destination folder for added media files.

TV Default: ``~/Media/TV``

Movies Default: ``~/Media/Movies``

ignore_subs
###########
Tell Filebot whether or not to process subtitle files along with video files or ignore them.

Values:
    - ``no``
    - ``yes`` (default)

format
######
Specify a Filebot naming format. During mediahandler, it will be appended to the media type's ``folder`` value to form a complete path. See Filebot's `format expressions documentation <https://www.filebot.net/naming.html>`_ for more details.

TV Default: ``"{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}"``

Movies Default: ``"{n} ({y})"``

log_file
########
Specify a log file to use for Filebot's logging feature.

Default: ``None`` (logging disabled)


Music
*****
The Music media type is integrated with `Beets <http://beets.radbox.org/>`_.

Default sections and values: ::

    Music:
        enabled: no
        log_file: 

enabled
#######
Enable or disable processing of the music media type by mediahandler.

Values:
    - ``no`` (default)
    - ``yes``

log_file
########
Specify a log file to use for Beets' logging feature.

Default: ``~/logs/beets.log``


Audiobooks
**********
The Audiobook media type makes use of the Google Books API for processing. Additionally, creation of chaptered audiobook files (.m4b) is available via integration with the `ABC <http://www.ausge.de/ausge-download/abc-info-english>`_ application for Linux.

EM Media Handler does not *yet* support creation of chaptered audiobook files on OS X.

Default sections and values: ::

    Audiobooks:
        enabled: no
        folder: 
        api_key: 
        make_chapters: off
        chapter_length: 8

enabled
#######
Enable or disable processing of the audiobooks media type by mediahandler.

Values:
    - ``no`` (default)
    - ``yes``

folder
######
Specify a destination folder for added audiobooks.

Default: ``~/Media/Audiobooks``

api_key
#######
A valid Google API key. To obtain one, you will need to:

1. Visit the `Google API Console <https://console.developers.google.com/>`_.
2. Create a new project (you can keep the default values that Google provides).
3. When your project is created, click on the "Enable an API" button on the Project Dashboard.
4. Scroll to the "Books API" and click on the "Off" button next to it on the right to activate.
5. In the left-hand menu, click on the "Credentials" option under "APIs & auth"
6. Click on the "Create new Key" button under "Public API access".
7. Select "Server key".
8. (Optional) Specify your server's IP for greater security.
9. Copy & paste the generated "API KEY" into the ``api_key`` setting in your config file, e.g. ::

        Audiobooks:
            enabled: yes
            folder: /my/path/to/books
            api_key: kKCRCNNsbrfWkohKpxwq
            make_chapters: on
            chapter_length: 8

make_chapters
#############
Enable or disable creation of chaptered audiobook files (.m4b) using the `ABC <http://www.ausge.de/ausge-download/abc-info-english>`_ application for Linux. Visit the :doc:`requirements` section for information on installation.

EM Media Handler does not *yet* support creation of chaptered audiobook files on OS X.

Values:
    - ``off`` (default)
    - ``on``

chapter_length
##############
Specify, in *hours*, the maximum length each audiobook file (.m4b) created by `ABC <http://www.ausge.de/ausge-download/abc-info-english>`_ should be. For audiobooks that have a running time longer than the specified length, multiple parts will be created, e.g. ::

    ~/Media/Audiobooks/Donna Tartt/The Goldfinch_ A Novel/The Goldfinch, Part 1.m4b
    ~/Media/Audiobooks/Donna Tartt/The Goldfinch_ A Novel/The Goldfinch, Part 2.m4b
    ~/Media/Audiobooks/Donna Tartt/The Goldfinch_ A Novel/The Goldfinch, Part 3.m4b

Default: ``8`` (hours)