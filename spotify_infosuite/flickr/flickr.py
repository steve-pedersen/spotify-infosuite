"""
Fall 2017 CSc 690
File: flickr.py
Author: Steve Pedersen & Andrew Lesondak
System: OS X
Date: 12/13/2017
Usage: python3 spotify_infosuite.py
Dependencies: Python3, PyQt5, beautifulsoup4, lxml, unidecode
Description: Flickr class.  Used to search the Flickr API for images.

"""

import requests
import re
import json
import os
from PyQt5 import QtNetwork, QtCore
from PyQt5.QtGui import QPixmap
import ssl
from urllib.request import urlopen

class Flickr:

	def __init__(self, artist, has_images=True):
		self.artist = artist
		self.has_images = has_images

		self.images = []

# Search for a specified amount of images (at the maximum) and display in browser
def search(artist):
	notfound_count = 0
	pixmaps = []
	query = artist
	query = query.replace(' ', '%20')
	maxResults = 20

	# with open('./flickr/credentials.json') as creds:
	with open(os.path.dirname(__file__) + '/credentials.json') as creds:
		credentials = json.load(creds)

	appkey = credentials['flickr']['appkey']

	url = 'https://api.flickr.com/services/rest/?'
	url = url + 'method=flickr.photos.search&'
	url = url + 'format=json&'
	url = url + 'nojsoncallback=1&'
	url = url + 'sort=relevance&'
	url = url + 'tags=' + artist + ',music,musician,band,live,album,song'

	url = url + '&per_page=' + str(maxResults) + '&api_key=' + appkey + '&text=' + str(query)
	response = requests.get(url).json()

	if (response['stat'] == 'ok'):
		photo_urls = []
		for p in response['photos']['photo']:
			photo_url = 'https://farm' + str(p['farm']) + '.staticflickr.com/' + str(p['server'])
			photo_url = photo_url + '/' + str(p['id']) + '_' + str(p['secret']) + '.jpg'

			try:
				context = ssl._create_unverified_context()
				data = urlopen(photo_url, context=context).read()
				pixmap = QPixmap()
				pixmap.loadFromData(data)
				pixmaps.append(pixmap)
			except:
				notfound_count += 1

		# fileNames = self.model.requestImages(photoUrls)
		return pixmaps


	else:
		# self.statusText.setText('No results found.')
		return None
