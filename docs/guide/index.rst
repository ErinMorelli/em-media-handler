Getting Started
============================================

Welcome to EM Media Handler! This guide will help you get started with automating your media.

Requirements
***************

EM Media Handler supports Python <= 2.7 - there are plans to support 3.x in a future release.

Check out the :doc:`/configuration/requirements` for details on required python packages and 3rd party applications.

Make sure your system is ready before proceeding.


Quick Installation
******************

The easiest way to install is via `pip`: ::

    pip install mediahandler

To upgrade to the latest version: ::

    pip install -U mediahandler


Installing from Source
**********************

1. Download the source from either `GitHub <https://github.com/ErinMorelli/em-media-handler>`_ or `BitBucket <http://code.erinmorelli.com/em-media-handler>`_.

2. From inside the downloaded source folder, run the build command: ::

    sudo python setup.py build

   .. note:: If you have run the build before, ensure you have a clean build environment by using:  ``sudo python setup.py clean -a``

3. Install the package: ::

    sudo python setup.py install


User Settings
*************

The default user configuration is installed to: ::

    ~/.config/mediahandler/config.yml

Use any text editor to open and edit the file. Refer to the :doc:`/configuration/settings` article more details on the settings available.


Usage
*****

To get started type: ::

    addmedia --help

to view the available options. Read more about the :doc:`/configuration/commandline`.

It is also possible to integrate EM Media Handler with `Deluge <http://deluge-torrent.org/>`_ using the `Execute <http://dev.deluge-torrent.org/wiki/Plugins/Execute>`_ plugin. Read more about :doc:`/configuration/deluge`.

