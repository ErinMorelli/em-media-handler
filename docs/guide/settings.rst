User Settings
============================================

An overview of all available user settings available in the user config file, which can be found here: ::

    ~/.config/mediahandler/config.yml

The configuration file uses yaml formatting, and does not require that every option is present in the file. Sections and options may be left blank or completely removed -- the application will use default values in their place.

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

See :doc:`deluge` for more information on this integration.

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
Default: yes

folder
######

ignore_subs
###########
Default: yes

format
######
TV default: "{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}"
Movies default: "{n} ({y})"

log_file
########


Music
*****

Default sections and values: ::

    Music:
        enabled: no
        log_file: 

enabled
#######
Default: no

log_file
########


Audiobooks
**********

Default sections and values: ::

    Audiobooks:
        enabled: no
        folder: 
        api_key: 
        make_chapters: off
        chapter_length: 8

enabled
#######
Default: no

folder
######

api_key
#######

make_chapters
#############
Default: off

chapter_length
##############
Default: 8