Command-line Interface
============================================

An overview of available options and usage of the EM Media Handler command-line interface.

This section is about the ``addmedia`` script, for information on the ``addmedia-deluge`` script, visit the :doc:`deluge` section.

.. contents::
    :local:

Usage
*****

``addmedia`` is the primary command-line interface for EM Media Handler.

Basic invocation: ::

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
REQUIRED. Specify media files to be added. Can be a single file or a folder.

Assumes media has an absolute path structure using this format: ::

    /path/to/<media type>/<media>

If you are not using this format, you will need to specify a `-t / --type`_ value.

-t / --type
###########
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

-c / --config
#############
Specify a custom configuration file to use for processing media.

Default: ``~/.config/mediahandler/config.yml``

-q / --query
############
Set a custom query string for audiobooks to pass to the Google Books API.

Useful for fixing "Unable to match" errors, which can occur when a book has a common title and no author name supplied in the file path.

-s / --single
#############
Force beets to import music as in single track mode.

Useful for fixing "items were skipped" errors, especially when a folder contains multiple single tracks instead of an album.

-n / --nopush
#############
Disable push notifications.

This flag overrides the ``enabled`` setting in the ``Notifications`` section of the user config file, but does not modify it.


Examples
********

The most basic
