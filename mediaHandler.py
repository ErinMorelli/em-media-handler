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

import sys, re, os
import shutil, logging, getopt

from os import path, listdir, makedirs
from twisted.internet import reactor
from deluge.ui.client import client

import media.tv, media.movies, media.music, media.audiobooks
import notify.email, notify.pushover
import extras.extract, config


# ======== SET GLOBAL HANDLER OPTIONS ======== #

handler = {
	'rmFiles': False,
	'logging': {
		'file': 'logs/handler.log', # Path to debugging log
		'level': logging.DEBUG, # default: error (debug, info, warning, error, critical)
	}, 
	'deluge': {
		'host': '127.0.0.1',
		'port': 58846,
		'username': 'deluge',
		'password': 'deluge'
	},
}

typesList = ['TV', 'Television', 'Movies', 'Music', 'Books', 'Audiobooks']


# ======== COMMAND LINE USAGE ======== #

def __showUsage(code):
	usageText = '''
EM Media Handler v%s / by %s

Usage: 
	mediaHandler.py -f /path/to/file [..options]


Options:
	-f 	: (required) Set path to media files, assumes path structure /path/to/<media type>/<media name>
	-c 	: Set a custom config file path
	-t 	: Force a specific media type for processing


Media types:
	%s
	''' % (__version__, __author__, '\n\t'.join(typesList))
	# Output text
	print usageText
	# Exit program
	sys.exit(int(code))


# ======== NOTIFY ======== #

def Success(msg):
	logging.info("Notifying successful")
	n = notify.Notification(msg)
	n.notifySuccess()
	return

def Failure(msg):
	logging.error(msg)
	logging.info("Notifying failure")
	n = notify.Notification(msg)
	n.notifyFailure()
	return

# ======== MOVE ANY FILE ======== #

def move_file(src):
	logging.info("Moving file(s)")
	# Set metadata options
	metadata = {
		"TV" : get_episode_info,
		"Movies" : get_movie_info,
	}
	# Get paths
	fileinfo = metadata[ttype](src) 
	# Check for errors
	if fileinfo == None:
		return None
	# Extract info
	(new_name, dst) = fileinfo
	logging.debug("Name: %s", new_name)
	logging.debug("DST: %s", dst)
	# Check that new file exists
	if not path.isfile(dst):
		Failure("File failed to move %s" % dst)
		return None
	# Return destination path
	return dst, new_name


# ======== TELEVISION ======== #

# GET EPISODE INFO
def get_episode_info(raw):
	logging.info("Getting TV episode information")
	# Send info to handler
	r = naming.Rename(raw)
	epInfo = r.episodeHandler()
	if epInfo == None:
		Failure("Unable to match episode: %s" % raw)
		return None
	# Extract info
	(ep_title, new_file) = epInfo
	# return folder and file paths
	return ep_title, new_file


# ======== MOVIES ======== #

# GET MOVIE INFO
def get_movie_info(raw):
	logging.info("Getting movie information")
	# Send info to handler
	r = naming.Rename(raw)
	movInfo = r.movieHandler()
	if movInfo == None:
		Failure("Unable to match movie: %s" % raw)
		return None
	# Extract info
	(mov_title, new_file) = movInfo
	# return folder and file paths
	return mov_title, new_file


# ======== MUSIC ======== #

# ADD MUSIC TO COLLETION
def add_music(raw, isSingle=False):
	logging.info("Getting music information")
	r = naming.Rename(raw)
	(err, musicInfo) = r.musicHandler(isSingle)
	if err:
		Failure("Unable to match music: %s\n%s" % (raw, musicInfo))
		return None
	# return album info
	return musicInfo


# ======== AUDIOBOOKS ======== #

# GET BOOK INFO
def add_book(raw):
	logging.info("Getting audiobook information")
	b = audiobooks.Book()
	bookInfo = b.getBook(raw)
	if bookInfo == None:
		Failure("Unable to match book: %s\n%s" % raw, bookInfo)
		return None
	# return book info
	return bookInfo


# ======== EXTRACTION FUNCTION ======== #

def extract_files(raw):
	logging.info("Extracting files from compressed file")
	# Send info to handler
	e = naming.Extract(file)
	extracted = e.fileHandler()
	if extracted == None:
		Failure("Unable to extract files: %s" % raw)
		return None
	# Send files back to handler
	return extracted


# ======== MAIN FILE FUNCTION ======== #

def __fileHandler(files):
	logging.info("Starting files handler")
	added_files = []
	# Process books first
	if ttype == "Books":
		added_file = add_book(files)
		added_files.append(added_file)
	# Then check for folders/files
	elif path.isfile(files):
		# Single file, treat differently
		logging.debug("Proecessing as a single file")
		# Look for zipped file first
		if re.search(r".(zip|rar|7z)$", files, re.I):
			logging.debug("Zipped file type detected")
			# Send to extractor
			get_files = extract_files(src)
			# Check for failure
			if get_files == None:
				return None
			# Rescan files
			file_handler(get_files)
		# otherwise treat like other files
		if ttype == "Music":
			added_file = add_music(files, True)
			added_files.append(added_file)
		else: 
			# Set single file as source
			src = files
			# Move file
			moveinfo = move_file(src)
			# Check for problems 
			if moveinfo == None:
				return
			(dst, added_file) = moveinfo
			added_files.append(added_file)
	else:
		# Otherwise process as folder
		logging.debug("Proecessing as a folder")
		if ttype == "Music":
			added_file = add_music(files)
			added_files.append(added_file)
		else: 
			# Get a list of files
			file_list = listdir(files)
			# Locate video file in folder
			for f in file_list:
				# Look for file types we want
				if re.search(r"\.(mkv|avi|m4v|mp4)$", f, re.I):
					# Set info
					filename = f
					src = files+'/'+filename
					# Move file
					moveinfo = move_file(src)
					# Check for problems 
					if moveinfo == None:
						return
					(dst, added_file) = moveinfo
					added_files.append(added_file)
	# Remove old files
	if handler['rmFiles']:
		if path.exists(files):
			logging.debug("Removing extra files")
			shutil.rmtree(files)
	# Send notification
	Success(added_files)
	# Finish
	return added_files


# ======== REMOVE TORRENT ======== #

def __removeTorrent():
	logging.info("Removing torrent from Deluge")
	# Connect to Deluge daemon
	d = client.connect(
		host = handler['deluge']['host'],
		port = handler['deluge']['port'],
		username = handler['deluge']['username'],
		password = handler['deluge']['password']
	)
	# We create a callback function to be called upon a successful connection
	def on_connect_success(result):
		logging.debug("Connection was successful!")
		def on_remove_torrent(success):
			if success:
				logging.debug("Remove successful: %s", tname)
			else:
				logging.warning("Remove unsuccessful: %s", tname)
			# Disconnect from the daemon & exit
			client.disconnect()
			reactor.stop()
		def on_get_session_state(torrents):
			found = False
			# Look for completed torrent in list
			for t in torrents:
				if t == thash:
					# Set as found and call remove function
					logging.debug("Torrent found: %s", tname)
					found = True
					client.core.remove_torrent(thash, False).addCallback(on_remove_torrent)
					break
			if not found:
				logging.warning("Torrent not found: %s", tname)
				# Disconnect from the daemon & exit
				client.disconnect()
				reactor.stop()
		# Get list of current torrent hashes
		client.core.get_session_state().addCallback(on_get_session_state)
	# We add the callback to the Deferred object we got from connect()
	d.addCallback(on_connect_success)
	# We create another callback function to be called when an error is encountered
	def on_connect_fail(result):
		logging.error("Connection failed: %s", result)
	# We add the callback (in this case it's an errback, for error)
	d.addErrback(on_connect_fail)
	# Run the twisted main loop to make everything go
	reactor.run()


# ======== GET ARGUMENTS ======== #

def __getArguments():
	useDeluge = False
	# Parse args
	try:
		(optlist, args) = getopt.getopt(sys.argv[1:], 'f:c:t:')
	except getopt.GetoptError as err:
		print str(err)
		__showUsage(2)
	# Check for failure conditions
	if len(optlist) > 0 and len(args) > 0:
		__showUsage(2)
	if len(optlist) == 0 and len(args) == 0:
		__showUsage(2)
	# Check for deluge
	if len(args) == 3:
		# Treat like deluge
		useDeluge = True
		args = {
			'hash' : args[0],
			'name' : args[1],
			'path' : args[2]
		}
	elif len(args) > 0:
		__showUsage(2)
	# Check for CLI
	if len(optlist) > 0:
		args = {}
		f = False
		for o,a in optlist:
			if o == '-f':
				f = True
				args['media'] = a 
			if o == '-c':
				args['config'] = a 
			if o == '-t':
				if a not in typesList:
					raise Warning('Media type %s not recognized' % a)
				args['type'] = a
		if not f:
			print 'option -f not specified'
			__showUsage(2)
	return useDeluge, args


# ======== HANDLE CLI MEDIA ======== #

def __handleMedia():
	logging.info("Processing from command line")
	logging.debug("Inputs: %s, %s, %s", args)
	# Extract info from path
	parsePath = re.search(r"^((.*)?\/(.*))\/(.*)$", args['media'], re.I)
	if parsePath:
		args['path'] = parsePath.group(1)
		args['name'] = parsePath.group(4)
		# Look for custom type
		if 'type' not in args.keys():
			args['type'] = parsePath.group(3)
			if args['type'] not in typesList:
					raise Warning('Media type %s not recognized' % args['type'])
		logging.debug("Detected: %s", args)
	else:
		# Notify about failure
		raise Warning("No type or name specified for media")
	print args
	return
	# Check that file was downloaded
	if path.exists(args['media']):
		# Send to handler
		newFiles = __fileHandler(args['media'])
	else:
		# There was a problem, no files found
		raise Warning("No media files found")
	return newFiles


# ======== HANDLE DELUGE MEDIA ======== #

def __handleDeluge():
	logging.info("Processing from deluge")
	logging.debug("Inputs: %s", args)
	# Extract media type from path
	findType = re.search(r"^\/([a-z]+)$", args['path'], re.I)
	if findType and findType.group(1):
		args['type'] = findType.group(1)
		logging.debug("Type detected: %s", args['type'])
	else:
		# Remove torrent
		__removeTorrent()
		# Notify about failure
		raise Warning("No type specified for download: %s" % args['name'])
	# Check that file was downloaded
	filePath = args['path']+"/"+args['name']
	if path.exists(filePath):
		# Remove torrent
		__removeTorrent()
		# Send to handler
		newFiles = __fileHandler(filePath)
	else:
		# There was a problem, no files found
		raise Warning("No downloaded files found: %s" % args['name'])
	return newFiles


# ======== MAIN FUNCTION WRAPPER ======== #

def main():
	logging.info("Starting main function")
	# Get arguments
	global args
	(useDeluge, args) = __getArguments()
	# Set paths
	__userHome = path.expanduser("~")
	__configPath = '%s/.config/mediaHandler/mediaHandler.conf' % __userHome
	# Check for user-specified config
	if 'config' in args.keys():
		__configPath = args['config']
	# Check that config exists
	if not os.path.isfile(__configPath):
		raise Warning('Configuration file does not exist')
	# Check config file permissions
	if not os.access(__configPath, os.R_OK):
		raise Warning('Configuration file cannot be opened')
	# Get settings from config
	global settings
	settings = config.getConfig(__configPath)
	# If deluge, start processor
	if useDeluge:
		__handleDeluge()
	# Start main function
	else: 
		__handleMedia()
	return


# ======== COMMAND LINE ======== #

if __name__=='__main__':
	main()
