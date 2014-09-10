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

from smtplib import SMTP
import datetime, base64
import httplib, urllib, logging


# ======== CLASS DECLARTION ======== #

class Notification:
	def __init__(self, filearray):
		logging.info("Initializing notification class")
		self.files = filearray
		self.pwf = '.pwd'

	def __decode(self, key, string):
		logging.info("Decrypting")
	        decoded_chars = []
	        string = base64.urlsafe_b64decode(string)
	        for i in xrange(len(string)):
	                key_c = key[i % len(key)]
	                encoded_c = chr(abs(ord(string[i]) - ord(key_c) % 256))
	                decoded_chars.append(encoded_c)
	        decoded_string = "".join(decoded_chars)
	        return decoded_string


	def __get_pw(self):
		logging.info("Getting password")
		store = open(self.pwf,'r')
		key = store.readline()
		pw = store.readline()
		store.close()
		return self.__decode(key, pw)

	def notifySuccess(self):
		logging.info("Starting success notifications")
		debuglevel = 0

		media_list = '\n    '.join(self.files)

		# Send notification email
		logging.debug("Before SMTP send")
		smtp = SMTP()
		smtp.set_debuglevel(debuglevel)
		smtp.connect('smtp.email.com', 587)
		smtp.login('user@email.com', self.__get_pw())

		from_addr = "Media Handler <user@email.com>"
		to_addr = "user@email.com"

		subj = "[EM Media Handler] Media Successfully Added" 
		date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )

		message_text = '''Hello,

The following media was successfully downloaded to your server:

    %s

Thanks,

        EM Media Handler

                ''' % media_list

		msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( from_addr, to_addr, subj, date, message_text )

		smtp.sendmail(from_addr, to_addr, msg)
		logging.debug("After SMTP send")

		# Send push notification
		logging.debug("Before push notification send")
		conn = httplib.HTTPSConnection("api.pushover.net:443")

		conn_text = '''Media was successfully added to your server:
%s
		''' % media_list

		conn_url = urllib.urlencode({
			"token": "",
			"user": "",
			"title": "EM Media Handler",
			"message": conn_text,
		})
		logging.debug("API call: %s", conn_url)

		conn.request(
			"POST", 
			"/1/messages.json",
			conn_url, 
			{ "Content-type": "application/x-www-form-urlencoded" }
		)
		conn_resp = conn.getresponse()
		if conn_resp != 200:
			logging.error("API Response: %s %s", conn_resp.status, conn_resp.reason)
		else:
			logging.info("API Response: %s %s", conn_resp.status, conn_resp.reason)

		logging.debug("After push notification send")

		smtp.quit()


	def notifyFailure(self):
		logging.info("Starting failure notifications")
		debuglevel = 0

		# Send notification email
		logging.debug("Before SMTP send")
		smtp = SMTP()
		smtp.set_debuglevel(debuglevel)
		smtp.connect('smtp.email.com', 587)
		smtp.login('user@email.com', self.__get_pw())

		from_addr = "Media Handler <user@email.com>"
		to_addr = "user@email.com"

		subj = "[EM Media Handler] Add Media Error" 
		date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )

		message_text = '''Hello,

The following error was reported when attempting to add media to your server:

    %s

Thanks,

        EM Media Handler

                ''' % self.files

		msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( from_addr, to_addr, subj, date, message_text )

		smtp.sendmail(from_addr, to_addr, msg)
		logging.debug("After SMTP send")

		# Send push notification
		logging.debug("Before push notification send")
		conn = httplib.HTTPSConnection("api.pushover.net:443")

		conn_text = '''There was an error reported:
%s
		''' % self.files

		conn_url = urllib.urlencode({
			"token": "",
			"user": "",
			"title": "EM Media Handler",
			"message": conn_text,
		})
		logging.debug("API call: %s", conn_url)

		conn.request(
			"POST", 
			"/1/messages.json",
			conn_url, 
			{ "Content-type": "application/x-www-form-urlencoded" }
		)
		conn_resp = conn.getresponse()
		if conn_resp != 200:
			logging.error("API Response: %s %s", conn_resp.status, conn_resp.reason)
		else:
			logging.info("API Response: %s %s", conn_resp.status, conn_resp.reason)

		logging.debug("After push notification send")

		smtp.quit()
