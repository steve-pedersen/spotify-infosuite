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
		self.twitter_search = False
		self.facebook_search = False
		self.artisturl = 'https://music-api.musikki.com/v1/artists'
		self.images = []

		print('Musikki found artist with name: ', self.artist)

	# https://music-api.musikki.com/reference/artists#bio
	def get_full_bio(self, nam):		
		url = self.artisturl + '/' + str(self.mkid) + '/bio'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# https://music-api.musikki.com/reference/artists#images
	def get_full_images(self, nam):		
		url = self.artisturl + '/' + str(self.mkid) + '/images'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# https://music-api.musikki.com/reference/artists#collaborations
	def get_collaborations(self, nam):		
		url = self.artisturl + '/' + str(self.mkid) + '/collaborations'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# https://music-api.musikki.com/reference/artists#labels
	def get_labels(self, nam, q=''):		
		url = self.artisturl + '/' + str(self.mkid) + '/labels'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# https://music-api.musikki.com/reference/artists#news
	def get_news(self, nam):	
		url = self.artisturl + '/' + str(self.mkid) + '/news'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# https://music-api.musikki.com/reference/artists#related
	def get_related_artists(self, nam):		
		url = self.artisturl + '/' + str(self.mkid) + '/related'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)
	
	# https://music-api.musikki.com/reference/artists#releases
	def get_releases(self, nam, q=''):		
		url = self.artisturl + '/' + str(self.mkid) + '/releases'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# https://music-api.musikki.com/reference/artists#summary
	def get_release_summary(self, nam):		
		url = self.artisturl + '/' + str(self.mkid) + '/releases/summary'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	# https://music-api.musikki.com/reference/artists#social
	def get_social_media_twitter(self, nam):
		self.twitter_search = True
		url = self.artisturl + '/' + str(self.mkid) + '/social?q=[service-name:twitter]'
		url = url + '&appkey=' + self.appkey
		url = url + '&appid=' + self.appid
		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)

	def get_social_media_facebook(self, nam):
		self.facebook_search = True
		url = self.artisturl + '/' + str(self.mkid) + '/social?q=[service-name:facebook]'
		url = url + '&appkey=' + self.appkey
		url = url + '&appid=' + self.appid
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
					# print('Match found on entry ', result_counter + 1, ' of ', total)
					# break
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


