"""
The MIT License (MIT)

Copyright (c) 2015 HexRx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sublime, sublime_plugin
import ftplib
import os
import datetime
import json

class Ftp(object):
	def __init__(self, host, port, username, password, ftpRootDir):
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.ftpRootDir = ftpRootDir

	def uploadTo(self, localRootDir, currentFullPath):

		session = ftplib.FTP()
		session.connect(self.host, self.port)
		session.login(self.username, self.password)

		currentPath = os.path.dirname(currentFullPath)
		# Remove full path and remove \\
		localFilePath = currentPath.replace(localRootDir, '')[1:]

		# Replace win path to unix path
		fullFtpPath = os.path.join(self.ftpRootDir, localFilePath).replace('\\', '/')

		file = open(currentFullPath, 'rb')
		# Set ftp directory
		session.cwd(fullFtpPath)

		currentFileName = os.path.basename(currentFullPath)
		session.storbinary('STOR ' + currentFileName, file)

		file.close()
		session.quit()

		time = datetime.datetime.now().strftime('%X')
		msg = '[Deployed {0}]: {1}'.format(time, os.path.join(fullFtpPath, os.path.basename(currentFullPath)).replace('\\', '/'))
		print(msg)
		sublime.status_message(msg)

# Save file event listener
class SaveEventListener(sublime_plugin.EventListener):
	def on_post_save_async(self, view):

		if view.window().project_data():
			for openFolder in view.window().project_data()['folders']:
				firstOpenFolder = openFolder['path']

				configFileName = 'simple-ftp-deploy.json'
				configFile = os.path.join(firstOpenFolder, configFileName)
				# Deploy if exists config file in root folder
				if os.path.isfile(configFile):
					# Read the config
					with open(configFile) as data:
						config = json.load(data)
						ftp = Ftp(config['host'], config['port'] if 'port'in config else 21, config['username'], config['password'], config['rootDirectory'] if 'rootDirectory' in config else '')
						
						# Ignore config file
						if os.path.basename(view.file_name()) != configFileName:
							# Start upload if the file is located in open folder
							if firstOpenFolder in view.file_name():
								ftp.uploadTo(firstOpenFolder, view.file_name())