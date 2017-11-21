import requests
import re
import json
import os
from PyQt5 import QtNetwork, QtCore

class Flickr:

	THUMB_QTY = 5
	# MAX_RESULTS = 20
	FLICKR_URL = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&format=json&nojsoncallback=1&sort=relevance'

	def __init__(self, artist, appkey, has_images=True):
		self.artist = artist
		self.appkey = appkey
		self.has_images = has_images

		self.images = []


# Search for a specified amount of images (at the maximum) and display in browser
def search(artist):
	query = artist
	query = query.replace(' ', '%20')
	maxResults = 20

	with open('./flickr/credentials.json') as creds:
		credentials = json.load(creds)

	appkey = credentials['flickr']['appkey']

	url = 'https://api.flickr.com/services/rest/?'
	url = url + 'method=flickr.photos.search&'
	url = url + 'format=json&'
	url = url + 'nojsoncallback=1&'
	url = url + 'sort=relevance'
	url = url + 'tags=music,song,musician,artist'

	url = url + '&per_page=' + str(maxResults) + '&api_key=' + appkey + '&text=' + str(query)
	response = requests.get(url).json()

	if (response['stat'] == 'ok'):
		photoUrls = []
		for p in response['photos']['photo']:
			photoUrl = 'https://farm' + str(p['farm']) + '.staticflickr.com/' + str(p['server'])
			photoUrl = photoUrl + '/' + str(p['id']) + '_' + str(p['secret']) + '.jpg'
			photoUrls.append(photoUrl)
			print(photoUrl)
			print(type(photoUrl))
		# fileNames = self.model.requestImages(photoUrls)
		return photoUrls


	else:
		# self.statusText.setText('No results found.')
		return None
