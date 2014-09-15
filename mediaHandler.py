#!/usr/bin/python
#
# EM MEDIA HANDLER
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

__version__ = '1.0'
__author__ = 'Erin Morelli <erin@erinmorelli.com>'


# ======== IMPORT MODULES ======== #

import sys
import logging
from re import search, I
from shutil import rmtree
from os import path, listdir
from getopt import getopt, GetoptError
from config import getConfig, makeConfig
import extras.notify as Notify


# ======== DEFINE HANDLER CLASS ======== #

class Handler:

    # ======== INIT CLASS ======== #

    def __init__(self):
        # Set global variables
        self.typesList = ['TV',
                          'Television',
                          'Movies',
                          'Music',
                          'Books',
                          'Audiobooks']
        self.args = {}
        self.settings = {}
        self.Push = ''

    # ======== COMMAND LINE USAGE ======== #

    def __showUsage(self, code):
        usageText = '''
EM Media Handler v%s / by %s

Usage:
        mediaHandler.py -f /path/to/file [..options]


Options:
        -f     : (required) Set path to media files
                  Assumes path structure /path/to/<media type>/<media name>
        -c     : Set a custom config file path
        -t     : Force a specific media type for processing


Media types:
        %s
        ''' % (__version__, __author__, '\n\t'.join(self.typesList))
        # Output text
        print usageText
        # Exit program
        sys.exit(int(code))

    # ======== MOVE VIDEO FILES ======== #

    def __addVideo(self, src):
        logging.info("Moving file(s)")
        # Set metadata options
        metadata = {
            "TV": self.__addEpisode,
            "Television": self.__addEpisode,
            "Movies": self.__addMovie,
        }
        # Get paths
        fileInfo = metadata[self.args['type']](src)
        # Check for errors
        if fileInfo is None:
            return None
        # Extract info
        (newName, dst) = fileInfo
        logging.debug("Name: %s", newName)
        logging.debug("DST: %s", dst)
        # Check that new file exists
        if not path.isfile(dst):
            self.Push.Failure("File failed to move %s" % dst)
        # Return new file name
        return newName

    # ======== ADD TV EPISODE ======== #

    def __addEpisode(self, raw):
        logging.info("Getting TV episode information")
        # Check that TV is enabled
        if not self.settings['TV']['enabled']:
            self.Push.Failure("TV type is not enabled")
        # Import TV module
        import media.tv as TV
        # Send info to handler
        e = TV.Episode(self.settings['TV'])
        epInfo = e.getEpisode(raw)
        if epInfo is None:
            self.Push.Failure("Unable to match episode: %s" % raw)
        # Extract info
        (epTitle, newFile) = epInfo
        # return folder and file paths
        return epTitle, newFile

    # ======== ADD MOVIE ======== #

    def __addMovie(self, raw):
        logging.info("Getting movie information")
        # Check that Movies are enabled
        if not self.settings['Movies']['enabled']:
            self.Push.Failure("Movies type is not enabled")
        # Import movie module
        import media.movies as Movies
        # Send info to handler
        m = Movies.Movie(self.settings['Movies'])
        movInfo = m.getMovie(raw)
        if movInfo is None:
            self.Push.Failure("Unable to match movie: %s" % raw)
        # Extract info
        (movTitle, newFile) = movInfo
        # return folder and file paths
        return movTitle, newFile

    # ======== ADD MUSIC ======== #

    def __addMusic(self, raw, isSingle=False):
        logging.info("Getting music information")
        # Check that Movies are enabled
        if not self.settings['Movies']['enabled']:
            self.Push.Failure("Movies type is not enabled")
        # Import music module
        import media.music as Music
        # Send info to handler
        m = Music.newMusic(self.settings['Music'])
        musicInfo = m.addMusic(raw, isSingle)
        if musicInfo is None:
            self.Push.Failure(
                "Unable to match music: %s\n%s" % (raw, musicInfo))
        # return album info
        return musicInfo

    # ======== ADD AUDIOBOOK ======== #

    def __addBook(self, raw):
        logging.info("Getting audiobook information")
        # Check that Movies are enabled
        if not self.settings['Audiobooks']['enabled']:
            self.Push.Failure("Audiobooks type is not enabled")
        # Import audiobooks module
        import media.audiobooks as Audiobooks
        # Send to handler
        b = Audiobooks.Book(self.settings['Audiobooks'])
        bookInfo = b.getBook(raw)
        if bookInfo is None:
            self.Push.Failure("Unable to match book: %s\n%s" % raw, bookInfo)
            return None
        # return book info
        return bookInfo

    # ======== EXTRACT FILES ======== #

    def __extractFiles(self, raw):
        logging.info("Extracting files from compressed file")
        # Import extract module
        import extras.extract as Extract
        # Send to handler
        extracted = Extract.getFiles(raw)
        if extracted is None:
            self.Push.Failure("Unable to extract files: %s" % raw)
            return None
        # Send files back to handler
        return extracted

    # ======== MAIN FILE HANDLER ======== #

    def __fileHandler(self, files):
        logging.info("Starting files handler")
        addedFiles = []
        # Process books first
        if self.args['type'] == "Books" or self.args['type'] == "Audiobooks":
            addedFile = self.__addBook(files)
            addedFiles.append(addedFile)
        # Then check for folders/files
        elif path.isfile(files):
            # Single file, treat differently
            logging.debug("Proecessing as a single file")
            # Look for zipped file first
            if search(r".(zip|rar|7z)$", files, I):
                logging.debug("Zipped file type detected")
                # Send to extractor
                if (self.settings['TV']['enabled'] or
                   self.settings['Movies']['enabled']):
                    getFiles = self.__extractFiles(files)
                    # Check for failure
                    if getFiles is None:
                        return None
                    # Rescan files
                    self.__fileHandler(getFiles)
            # otherwise treat like other files
            if self.args['type'] == "Music":
                addedFile = self.__addMusic(files, True)
                addedFiles.append(addedFile)
            else:
                # Set single file as source
                src = files
                # Move file
                videoInfo = self.__addVideo(src)
                # Check for problems
                if videoInfo is None:
                    return
                addedFile = videoInfo
                addedFiles.append(addedFile)
        else:
            # Otherwise process as folder
            logging.debug("Proecessing as a folder")
            if self.args['type'] == "Music":
                addedFile = self.__addMusic(files)
                addedFiles.append(addedFile)
            else:
                # Get a list of files
                fileList = listdir(files)
                # Locate video file in folder
                for f in fileList:
                    # Look for file types we want
                    if search(r"\.(mkv|avi|m4v|mp4)$", f, I):
                        # Set info
                        fileName = f
                        src = files+'/'+fileName
                        # Move file
                        videoInfo = self.__addVideo(src)
                        # Check for problems
                        if videoInfo is None:
                            return
                        addedFile = videoInfo
                        addedFiles.append(addedFile)
        # Remove old files
        if not self.settings['General']['keep_files']:
            if path.exists(files):
                logging.debug("Removing extra files")
                rmtree(files)
        # Send success notification
        self.Push.Success(addedFiles)
        # Finish
        return addedFiles

    # ======== GET ARGUMENTS ======== #

    def __getArguments(self):
        useDeluge = False
        # Parse args
        try:
            (optlist, getArgs) = getopt(sys.argv[1:], 'f:c:t:')
        except GetoptError as err:
            print str(err)
            self.__showUsage(2)
        # Check for failure conditions
        if len(optlist) > 0 and len(getArgs) > 0:
            self.__showUsage(2)
        if len(optlist) == 0 and len(getArgs) == 0:
            self.__showUsage(2)
        # Check for deluge
        if len(getArgs) == 3:
            # Treat like deluge
            useDeluge = True
            newArgs = {
                'hash': getArgs[0],
                'name': getArgs[1],
                'path': getArgs[2]
            }
        elif len(getArgs) > 0:
            self.__showUsage(2)
        # Check for CLI
        if len(optlist) > 0:
            newArgs = {}
            f = False
            for o, a in optlist:
                if o == '-f':
                    f = True
                    newArgs['media'] = a
                if o == '-c':
                    newArgs['config'] = a
                if o == '-t':
                    if a not in self.typesList:
                        self.Push.Failure('Media type %s not recognized' % a)
                    newArgs['type'] = a
            if not f:
                print 'option -f not specified'
                self.__showUsage(2)
        return useDeluge, newArgs

    # ======== HANDLE MEDIA ======== #

    def __handleMedia(self, useDeluge):
        logging.debug("Inputs: %s", self.args)
        # Determing if using deluge or not
        if useDeluge:
            logging.info("Processing from deluge")
            # Extract media type from path
            findType = search(r"^(.*)?\/(.*)$", self.args['path'], I)
            if findType:
                self.args['type'] = findType.group(2)
                logging.debug("Type detected: %s", self.args['type'])
            else:
                if self.settings['Deluge']['enabled']:
                    # Remove torrent
                    import extras.torrent
                    extras.torrent.removeTorrent(
                        self.settings['Deluge'],
                        self.args['hash'])
                # Notify about failure
                self.Push.Failure(
                    "No type specified for download: %s" % self.args['name'])
        else:
            logging.info("Processing from command line")
            # Extract info from path
            parsePath = search(r"^((.*)?\/(.*))\/(.*)$",
                               self.args['media'], I)
            if parsePath:
                self.args['path'] = parsePath.group(1)
                self.args['name'] = parsePath.group(4)
                # Look for custom type
                if 'type' not in self.args.keys():
                    self.args['type'] = parsePath.group(3)
                    if self.args['type'] not in self.typesList:
                            self.Push.Failure(
                                'Media type %s not recognized' %
                                self.args['type'])
                logging.debug("Detected: %s", self.args)
            else:
                # Notify about failure
                self.Push.Failure(
                    "No type or name specified for media: %s" %
                    self.args['name'])
        # Check that file was downloaded
        filePath = self.args['path'] + "/" + self.args['name']
        if path.exists(filePath):
            if self.settings['Deluge']['enabled']:
                # Remove torrent
                import extras.torrent as Torrent
                Torrent.removeTorrent(
                    self.settings['Deluge'],
                    self.args['hash'])
            # Send to handler
            newFiles = self.__fileHandler(self.args['media'])
        else:
            # There was a problem, no files found
            self.Push.Failure("No media files found: %s" % self.args['name'])
        return newFiles

    # ======== MAIN ADD MEDIA FUNCTION ======== #

    def addMedia(self):
        # Get arguments
        (useDeluge, self.args) = self.__getArguments()
        # User-provided path 
        __newPath = None
        # Check for user-specified config
        if 'config' in self.args.keys():
            __newPath = self.args['config']
        # Set paths
        __configPath = makeConfig(__newPath)
        # Get settings from config
        self.settings = getConfig(__configPath)
        # Set up notify instance
        self.Push = Notify.Push(self.settings['Pushover'])
        # Start main function
        newFiles = self.__handleMedia(useDeluge)
        # Exit
        return newFiles


# ======== COMMAND LINE ======== #

if __name__ == '__main__':
    h = Handler()
    addedFiles = h.addMedia()
    if len(addedFiles) > 0:
        print "\nMedia successfully added!\n"
        for a in addedFiles:
            print "\t%s" % str(a)
        print "\n"
    else:
        raise Warning("No media added")
