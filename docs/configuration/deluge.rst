Deluge Integration
============================================

An overview of EM Media Handler's Deluge integration options.

This section is about the ``addmedia-deluge`` script, for information on the ``addmedia`` script, visit the :doc:`commandline` section.

.. contents::
    :local:


Basic Set-up
************

To utilize the ``addmedia-deluge`` script, you must have Deluge's `Execute plugin <http://dev.deluge-torrent.org/wiki/Plugins/Execute>`_ installed.

The script is designed to be used with the "Torrent Complete" event.

.. note:: This is the basic set up and usage of the script. However, using this method, it is assumed that your media is using the EM Media Handler `Folder Naming Structure`_. Read on to the `Advanced Set-up`_ section for how to automate this by using an additional Deluge plugin.

To set up the event, all you will need the full path to ``addmedia-deluge`` script, which can be found by entering the following from the command-line: ::

    which addmedia-deluge

Which should print something similar to ``/usr/local/bin/addmedia-deluge``. Copy and paste this path value into the "Command" text box when adding a new "Torrent Complete" event, save it, and you're done!

.. admonition:: Using Deluge on Windows

    The ``addmedia-deluge.exe`` script will not work with Deluge on Windows. Instead, use the ``addmedia-deluge.bat`` file in your Deluge preferences.

    Run this command in a Windows command prompt or PowerShell to find the full path: ::

        Get-Command addmedia-deluge.bat


Advanced Set-up
***************

The `LabelsPlus plugin <http://forum.deluge-torrent.org/viewtopic.php?f=9&t=42629>`_ for Deluge is a great companion to the ``addmedia-deluge`` script. 

The recommended setup:

- Create a label for each media types you intend to use, e.g. "TV", "Movies", etc.
- Under the "Label Defaults" settings set the following:
    - Enable the "Enable download settings" option
    - Set "Move Completed" to "Label based sub-folder"

You can stop here and manually set each newly added torrent's label, or you can continue on and use the plugin's "Autolabel" settings to create regular expressions that match the various media types and automatically apply labels.


Folder Naming Structure
***********************

EM Media Handler's Deluge integration requires that your media download paths follow a certain naming structure so that the correct media type can be detected for processing. The structure is: ::

    /path/to/<media type>/<downloaded media>

Currently accepted media type values and their case-insensitive variations are:

+------------+--------------------------+
| Type       | Allowed Variations       |
+============+==========================+
| TV         | TV, TV Shows, Television |
+------------+--------------------------+
| Movies     | Movies                   |
+------------+--------------------------+
| Music      | Music                    |
+------------+--------------------------+
| Audiobooks | Audiobooks, Books        |
+------------+--------------------------+
