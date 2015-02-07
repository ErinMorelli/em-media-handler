Command-line Interface
============================================

An overview of available options and usage of the EM Media Handler command-line interface.

This section is about the ``addmedia`` script, for information on the ``addmedia-deluge`` script, visit the :doc:`deluge` section.

.. contents::
    :local:

Usage
*****

``addmedia`` is the primary command-line interface for EM Media Handler.

**Basic invocation:** ::

    addmedia [MEDIA FILES] [OPTIONS...]

Use ``addmedia --help`` at any time to view information on the available options.

Options
********

These are the options available with the ``addmedia`` script.

.. contents::
    :local:
    :depth: 1

media
#####
**REQUIRED**. Specify media files to be added. Can be a single file or a folder.

Assumes media has an absolute path structure using this format: ::

    /path/to/<media type>/<media>

If you are not using this format, you will need to specify a :ref:`type_option` value.

.. _type_option:

-t / |--| type
###############
Force a specific media type for processing. Overrides the detected media type from `media`_.

By default, ``addmedia`` attempts to detect the media type based on the file path of the `media`_ provided. The assumed file path structure is: ::

    /path/to/<media type>/<media>

Allowed values:

+-------+-------------+
| Value | Media Type  |
+=======+=============+
| ``1`` | TV          |
+-------+-------------+
| ``2`` | Movies      |
+-------+-------------+
| ``3`` | Music       |
+-------+-------------+
| ``4`` | Audiobooks  |
+-------+-------------+

.. _config_option:

-c / |--| config
################
Specify a custom configuration file to use for processing media.

**Default:** ``~/.config/mediahandler/config.yml``

.. _query_option:

-q / |--| query
###############
Set a custom query string for audiobooks to pass to the Google Books API.

Useful for fixing "Unable to match" errors, which can occur when a book has a common title and no author name supplied in the file path.

.. _single_option:

-s / |--| single
################
Force beets to import music as in single track mode.

Useful for fixing "items were skipped" errors, especially when a folder contains multiple single tracks instead of an album.

.. _nopush_option:

-n / |--| nopush
################
Disable push notifications.

This flag overrides the ``enabled`` setting in the ``Notifications`` section of the user config file, but does not modify it.


Examples
********

**The most basic usage example:** ::

    addmedia /home/admin/downloads/movies/Finding\ Nemo

This would automatically detect the media type ``movies`` from the folder path name, then move and rename the movie file(s) from within the folder.

If your files are not in a folder named for the correct media type, use the :ref:`type_option` option to specify what type it is: ::

    addmedia /home/admin/downloads/House\ Season\ 1 --type 1

This will process the files in the folder as the ``1`` media type, TV Shows.

Add Audiobooks
##############

The audiobooks module utilizes Google's Books API. It sends a search request to the API based on the file name of the audiobook being added. Most of the time, Google is accurate with just a book name. However, for books with very common-sounding or similar titles, unless the file name contains both the book name and the author's name, we recommend using the :ref:`query_option` option to specify the exact book information to query Google with.

**Good book file name:** ::

    addmedia /home/admin/downloads/The\ Goldfinch\ Donna\ Tartt --type 4

Since the file name has the book title and author, this should match the book information correctly via Google.

**Bad book file name and fix:** ::

    addmedia /home/admin/downloads/Voices --type 4 --query "Voices Arnaldur Indridason"

If the ``--query`` option had not been set for this example, Google would've matched the filename "Voices" to a book called "Voices" by Richard Lortz, not to the book we wanted here, which was "Voices: An Inspector Erlendur Novel" by Arnaldur Indridason.


Fix Music 'Items were skipped' Errors
#####################################

By default, the Beets application will look for a full album of music to add to your library. It should process single files properly as well. However, for cases where you're trying to add multiple single tracks at once (i.e. a group of songs not from the album) sometimes Beets will throw a matching error or skip the file out of confusion. To fix this issue, use the :ref:`single_option` flag, which tells Beets to process the files individually, instead of as a group.

**For example:** ::

    addmedia /home/admin/shares/My\ Awesome\ Mixtape --type 3 --single

In this example, "My Awesome Mixtape" is a folder containing a bunch of my favorite songs from different artists and albums. The ``--single`` ensures that beet's processes each file with the correct metadata. 


Disable Push Notifications
##########################

If push notifications are enabled in your user settings file, the results of any ``addmedia`` process will create a new push notification. If you need to temporarily suppress these notifications, but don't want to disable them completely, use the :ref:`nopush_option` option.

**Example:** ::

    addmedia /home/admin/downloads/The\ Fountain --type 2 --nopush


Use a Different Configuration File
##################################

The configuration file used by EM Media Handler is dependent on the user running the ``addmedia`` script. By default it looks for ``~/.config/mediahandler/config.yml``. If you have a config file located elsewhere, or wish to use another user's config file, you can specify it with the :ref:`config_option` option.

**Example:** ::

    addmedia /home/admin/downloads/Orphan\ Black\ Season\ 2 --type 1 --config /home/johnsmith/documents/johns-config.yml


.. |--|  unicode:: U+0020 U+2010 U+2010 .. space hyphen hyphen
    :trim:
