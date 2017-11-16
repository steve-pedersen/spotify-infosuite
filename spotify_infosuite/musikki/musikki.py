import requests
import re
import json
import os
from PyQt5 import QtNetwork, QtCore


class Artist:
	def __init__(self, mkid, artist, appid, appkey, is_found=True):
		# print(mkid)
		if mkid == 0:
			print('no artist found')
		self.mkid = mkid
		self.artist = artist
		self.appid = appid
		self.appkey = appkey
		self.is_found = is_found

		self.images = []

		print('Musikki found artist with name: ', self.artist)

	# will fetch bio text and place it into specified container
	def get_full_bio(self, nam, container):
		self.bio_container = container

		url = 'https://music-api.musikki.com/v1/artists'
		url = url + '/' + str(self.mkid) + '/bio'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid
		print(url)

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# will fetch images and place it into specified container
	def get_full_images(self, nam, container):
		self.images_container = container

		url = 'https://music-api.musikki.com/v1/artists'
		url = url + '/' + str(self.mkid) + '/images'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid
		print(url)

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

# method needs to make a search req and then create Artist obj with mkid
def search(artist, song='', album=''):
	# replace spaces in the url with the '%20'
	query = re.sub('\s+', '%20', artist)

	with open('./musikki/credentials.json') as creds:
		credentials = json.load(creds)

	appid = credentials['musikki']['appid']
	appkey = credentials['musikki']['appkey']

	url = 'https://music-api.musikki.com/v1/artists?'
	url = url + 'q=[artist-name:' + query + ']'
	url = url + ',[query-type:suggest]'

	url = url + '&limit=20'
	url = url + '&appkey=' + appkey
	url = url + '&appid=' + appid

	# fetch the first page
	response = requests.get(url + '&page=1')
	json_resp = response.json()
	# print(json.dumps(json_resp))

	mkid = 0

	match_found = False
	result_counter = 0
	page_counter = 1
	total = json_resp['summary']['result_count']
	total_pages = json_resp['summary']['total_pages']

	# fetch and traverse results until a match is found
	if total > 0:
		while not match_found and total != result_counter:
			for result in json_resp['results']:
				if result['name'] == artist:
					match_found = True
					mkid = result['mkid']
					found_name = result['name']
					print('Match found on entry ', result_counter + 1, ' of ', total)
				result_counter += 1

			if not match_found:
				# make another request on the next page
				page_counter += 1
				json_resp = requests.get(url + '&page=' + str(page_counter)).json()

	if match_found:
		musikki_artist = Artist(mkid, artist, appid, appkey)
		return musikki_artist
	else:
		print('No results found in Musikki database... use a diff API?')
		return Artist(mkid, artist, appid, appkey, False)


