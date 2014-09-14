#!/usr/bin/python
#
# This file is a part of EM Media Handler
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


# ======== IMPORT MODULES ======== #

import urllib2, logging
import re, shutil, math

from subprocess import Popen, PIPE
from os import path, listdir, makedirs
from apiclient.discovery import build

from mutagen.mp3 import MP3
from mutagen.ogg import OggFileType


# ======== BOOK CLASS DECLARTION ======== #

class Book:

	# ======== SET GLOBAL CLASS OPTIONS ======== #

	def __init__(self, settings):
		logging.info("Starting audiobook handler class")
		# Get blacklist path
		__listPath = re.sub(r'media$', 'extras/', path.dirname(__file__))
		# Set up handler info
		self.handler = {
			'blacklist': __listPath + 'blacklist.txt',
			'regex' : {
				"nc" : r".(mp3|ogg|wav)$",
				"c" : r".(m4b)$",
			},
			'audio' : {
				'MP3' : MP3,
				'OGG' : OggFileType,
			},
		}
		# Default TV path
		self.handler['path'] = '%s/Media/Audiobooks' % path.expanduser("~")
		# Check for custom path in settings
		if 'folder' in settings.keys():
			if path.exists(settings['folder']):
				self.handler['path'] = settings['folder']
				logging.debug("Using custom path: %s" % self.handler['path'])
		# Look for Google api key	
		if 'api_key' in settings.keys():
			self.handler['apiKey'] = settings['api_key']
			logging.debug("Found Google Books API key")
		else:
			logging.warning("Google Books API key not found")
			raise Warning("Google Books API key not found")
		# Default chapter length
		self.handler['maxLength'] = 25200 #28800, # 8hrs (in seconds)
		# Look for custom chapter length 
		if 'chapter_length' in settings.keys():
			# Convert hours to seconds
			customLength = int(settings['chapter_length']) * 3600
			# Set new length
			self.handler['maxLength'] = customLength
			logging.debug("Using custom chapter length: %s" % self.handler['maxLength'])
		if 'make_chapters' in settings.keys():
			self.handler['makeChapters'] = settings['make_chapters']


	# ======== CLEAN UP SEARCH STRING ======== #

	def __cleanString(self, strPath):
		logging.info("Cleaning up path string")
		# Get query from folder path
		findBook = re.search(r"^((.*)?\/(Books|Audiobooks)\/(.*))$", strPath)
		string = findBook.group(4)
		logging.debug("Initial string: %s" % string)
		# Save original path for later
		self.handler['origPath'] = findBook.group(1)
		# Get blacklist items from file
		blacklist = [line.strip() for line in open(self.handler['blacklist'])]
		# Convert blacklist array to regex string
		blacklist = "|".join(blacklist)
		# setup order of regexes
		regex = [
			blacklist,
			"\(.*\)",
			"[[\(\[\{].*[\)\]\}]",
			"[^a-zA-Z ]",
			"\s{2,10}",
		]
		# Loop through regexes
		for r in regex:
			count = 1
			while count > 0:
				(string, count) = re.subn(r, " ", string)
		# return cleaned up string
		return string


	# ======== SAVE COVER IMAGE ======== #

	def __saveCover(self, imgDir, imgUrl):
		logging.info("Saving audiobook cover image")
		# Set new image file path
		imgPath = imgDir + "/cover.jpg"
		# Check to see if file exists
		if path.isfile(imgPath):
			logging.warning("Cover image already exists")
			# If so, return none
			return imgPath
		# Clean up image url 
		noCurl = re.sub(r"(\&edge=curl)", "", imgUrl)
		logging.debug("Cleaned cover url: %s" % noCurl)
		# Set image request headers
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		# Get image info from web
		response = opener.open(noCurl)
		# Open destination file
		output = open(imgPath,"wb")
		# Write image contents to file
		output.write(response.read())
		# Close open file
		output.close()
		# Return new image path
		return imgPath


	# ======== CHAPTERIZE FILES  ======== #

	def __getChapters(self, filePath, fileArray, fileType):
		logging.info("Determining book parts")
		# Defaults
		fileType = fileType.upper()
		totaLength = 0
		bookParts = 0
		bookChunks = []
		# Sum all the file durations
		for f in fileArray:
			fullPath = filePath + '/' + f
			audioTrack = self.handler['audio'][fileType](fullPath)
			totaLength += audioTrack.info.length
			logging.debug("%s:  %s" % (f, audioTrack.info.length))
		logging.debug("Total book length: %s seconds" % totaLength)
		# Check against defined max part length
		if totaLength <= self.handler['maxLength']:
			bookParts = 1
			logging.debug("Parts: %s" % bookParts)
			chunks = [fileArray]
		else:
			# Determine how many parts should be made
			bookParts = int( math.ceil( totaLength / self.handler['maxLength'] ) )
			logging.debug("Parts: %s" % bookParts)
			# Count files
			fileCount = len(fileArray)
			logging.debug("File count: %s" % fileCount)
			# Calculate array chunk size
			arrayChunk = int( math.ceil( fileCount / bookParts ) )
			logging.debug("Array chunks: %s" % arrayChunk)
			# Create array chunks
			chunks = [fileArray[x:x+arrayChunk] for x in xrange(0, len(fileArray), arrayChunk)]
		logging.info("Creating book part subfolders")
		# Create new subfolders for parts
		for i, chunk in enumerate(chunks):
			# Create new folder for part
			partPath = filePath + '/Part ' + str(i+1)
			if not path.exists(partPath):
				makedirs(partPath)
			# Move files for part into new path
			for j, c in enumerate(chunk):
				startPath = filePath + '/' + c
				endPath = partPath + '/' + c
				shutil.copy(startPath, endPath)
			# Copy over cover image
			shutil.copy(filePath+'/cover.jpg', partPath+'/cover.jpg')
			# Add new part folder to array
			bookChunks.append(partPath)
		# Return array of new part paths
		return bookChunks


	# ======== CHAPTERIZE FILES  ======== #

	def __chapterizeFiles(self, filePath, fileArray):
		logging.info("Chapterizing audiobook files")
		newFiles = []
		# Get chapter parts
		fileParts = self.__getChapters(filePath, fileArray, args['fileType'])
		# Set defaults
		php = '/usr/bin/php'
		abc = '/usr/bin/abc.php'
		# Create m4b for each file part
		for i, filePart in enumerate(fileParts):
			partPath = filePath + '/Part ' + str(i+1)
			# Define chapter query
			bCMD = [php, '-f', abc,
				filePart, # Path to book files
				bookInfo['author'].encode('ascii','ignore'), # artist
				bookInfo['longTitle'].encode('ascii','ignore'), # album
				bookInfo['shortTitle'].encode('ascii','ignore'), # title
				bookInfo['genre'].encode('ascii','ignore'), # genre
				bookInfo['year'].encode('ascii','ignore'), # year
				self.handler['fileType'] # filetype
			]
			logging.debug("ABC query:\n%s" % bCMD)
			# Process query
			p = Popen(bCMD, stdout=PIPE, stderr=PIPE)
			# Get output
			(output, err) = p.communicate()
			logging.debug("ABC output: %s" % output)
			logging.debug("ABC err: %s" % err)
			# Set new file regex search
			findFiles = r"Audiobook \'(.*)\.m4b\' created succsessfully!"
			# Find file names in output
			bookFiles = re.search(findFiles, output)
			if bookFiles == None:
				return False, output
			# Set full file path
			createdFile =  partPath + '/' + bookFiles.group(1) + '.m4b'
			newFilePath = filePath + '/' + bookFiles.group(1) + ' - ' + str(i+1) + '.m4b'
			# Remave file with part #
			shutil.move(createdFile, newFilePath)
			logging.debug("New file path: %s" % newFilePath)
			# Add to array
			newFiles.append(newFilePath)
		# Return success with array of new file paths
		return True, newFiles


	# ======== GET AUDIOBOOK FILES ======== #

	def __getFiles(self, fileDir, makeChapters):
		logging.info("Retrieving audiobook files")
		# default values
		isChapterized = False
		toChapterize = []
		bookFiles = []
		# loop through all the files in dir
		fileList = listdir(fileDir)
		for f in sorted(fileList):
			# Look for file types we want
			goodFile = re.search(self.handler['regex']['c'], f, re.I)
			if goodFile:
				fullPath = fileDir + '/' + f
				bookFiles.append(fullPath)
			# Look for file types we can chapterize
			badFile = re.search(self.handler['regex']['nc'], f, re.I)
			if badFile:
				self.handler['fileType'] = badFile.group(1)
				toChapterize.append(f)
		# See if any files need chapterizing
		if makeChapters:
			logging.debug("Already chaptered file count: %s" % len(bookFiles))
			logging.debug("To chapter file count: %s" % len(toChapterize))
			if len(toChapterize) > 0 and len(bookFiles) == 0:
				(chapterSuccess, newFiles) = self.__chapterizeFiles(fileDir, toChapterize)
				if chapterSuccess:
					bookFiles = newFiles
				else:
					return False, newFiles
		else:
			logging.debug("Not making chapters")
			bookFiles = toChapterize
		# Make sure we have chapterized files to return
		logging.debug("Final book file count: %s" % len(bookFiles))
		if len(bookFiles) > 0:
			isChapterized = True
		# Return status and files
		return isChapterized, bookFiles


	# ======== MOVE FILES ======== #

	def __moveFiles(self, fileArray, hasChapters):
		logging.info("Moving audiobook files")
		# Create folder-friendly title
		if bookInfo['subtitle'] == None:
			folderTitle = bookInfo['shortTitle']
		else: 
			folderTitle = bookInfo['shortTitle'] + '_ ' + bookInfo['subtitle']
		# Set new book directory path
		bookDir = self.handler['path'] + '/' + bookInfo['author'] + '/' + folderTitle
		logging.debug("New directory: %s" % bookDir)
		# Create the folder
		if not path.exists(bookDir):
			makedirs(bookDir)
		# Sort files in order
		sortedArray = sorted(fileArray)
		# Loop through files
		movedFiles = []
		for i, bookFile in enumerate(sortedArray):
			# Set new name
			newName = bookInfo['shortTitle']
			# Use chapter naming for chapters
			if hasChapters:
				# Set start path
				startPath = bookFile
				# Check for multiple parts
				if len(fileArray) > 1:
					bookPart = ', Part %s' % str(i+1)
					newName = bookInfo['shortTitle'] + bookPart
				# Set new file path
				newPath = bookDir + '/' + newName + '.m4b'
				# Move & rename the files
				shutil.move(startPath, newPath)
			else:	
				# Set non-chaptered file paths & formatting
				startPath = self.handler['origPath'] + '/' + bookFile
				newPath = "%s/%02d - %s.%s" % (bookDir, i+1, newName, self.handler['fileType'])
				# Copy the files
				shutil.copy(startPath, newPath)
			logging.debug("Start path: %s" % startPath)
			logging.debug("New path: %s" % newPath)
			# Add to moved file list
			movedFiles.append(newName)
		if len(movedFiles) == 0:
			return False
		# return success and list of moved files
		return True


	# ======== GET BOOK INFO FROM GOOGLE ======== #

	def __askGoogle(self, query):
		logging.info("Querying Google Books")
		# Connect to Google Books API
		service = build('books', 'v1', developerKey=self.handler['apiKey'])
		# Make API request
		request = service.volumes().list(
			q=query,
			orderBy="relevance",
			printType="books",
			maxResults=5
		)
		# Get response
		response = request.execute()
		logging.debug("Google response:\n%s" % response)
		# Get the top response
		for book in response.get('items', []):
			# Get publication date
			published = book['volumeInfo']['publishedDate']
			logging.debug("Published date: %s" % published)
			# Extract just the year
			findYear = re.match(r"(\d{4})", published)
			if findYear == None:
				logging.error("No year found")
				year = '9999'
			else:
				year = findYear.group(1)
			# Check for categories
			if 'categories' in book['volumeInfo']:
				category = book['volumeInfo']['categories'][0]
			else:
				category = "Audiobook"
			if 'subtitle' in book['volumeInfo']:
				longTitle = book['volumeInfo']['title'] + ': ' + book['volumeInfo']['subtitle']
				subtitle = book['volumeInfo']['subtitle']
			else:
				longTitle = book['volumeInfo']['title']
				subtitle = None
			# Set book information file structure
			logging.info("Google Book ID: %s" % book['id'])
			bookInfo = {
				'id' : book['id'],
				'shortTitle' : book['volumeInfo']['title'],
				'longTitle' : longTitle,
				'subtitle' : subtitle,
				'year' : year,
				'genre' : category,
				'author' : ", ".join(book['volumeInfo']['authors']),
				'cover' : book['volumeInfo']['imageLinks']['thumbnail'],
			}
			break
		# Return info
		return bookInfo


	# ======== MAIN BOOK FUNCTION (public) ======== #

	def getBook(self, raw):
		logging.info("Getting audiobook")
		# Parse string & get query
		refined = self.__cleanString(raw)
		logging.debug("Cleaned search string: %s" % refined)
		# Get book info from Google
		global bookInfo
		bookInfo = self.__askGoogle(refined)
		logging.debug(bookInfo)
		# Save cover image to file
		coverFile = self.__saveCover(raw, bookInfo['cover'])
		logging.debug("Cover image: %s" % coverFile)
		# Get files and chapterize files, if enabled
		(isChapterized, bookFiles) = self.__getFiles(raw, self.handler['makeChapters'])
		logging.debug(bookFiles)
		# Verify success
		if not isChapterized:
			return None
		# Move & rename files
		moveSuccess = self.__moveFiles(bookFiles, self.handler['makeChapters'])
		logging.debug(moveSuccess)
		# Verify success
		if not moveSuccess:
			return None
		# format book title
		bookTitle = '"' + bookInfo['longTitle'] + '" by ' + bookInfo['author']
		logging.info("Book title: %s" % bookTitle)
		# return new book title
		return bookTitle
