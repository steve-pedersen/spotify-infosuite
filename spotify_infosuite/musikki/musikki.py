import requests
import re
import json
import os
from PyQt5 import QtNetwork, QtCore


class Artist:

	def __init__(self, mkid, artist, appid, appkey):
		# print(mkid)
		if mkid == 0:
			print('no artist found')
		self.mkid = mkid# '100578790'#mkid
		self.artist = artist
		self.appid = appid
		self.appkey = appkey
		print('Musikki found artist with name: ', self.artist)
		

	# will fetch bio text and place it into specified container
	def get_full_bio(self, nam, container):
		self.bio_container = container

		url = 'https://music-api.musikki.com/v1/artists'
		url = url + '/' + str(self.mkid) + '/bio'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		nam.get(req)
		print('in get_full_bio()')
		# response = requests.get(url)
		# json_resp = response.json()

		# bio = ''
		# for f in json_resp['full']:
		# 	paragraph = ''
		# 	for t in f['text']:
		# 		paragraph += t
		# 	bio += paragraph + '\n\n'
		
		# return bio

	# def search_handler(self, reply):
	# 	print('in search_handler')
	# 	er = reply.error()
	# 	if er == QtNetwork.QNetworkReply.NoError:

	# 		response = reply.readAll()
	# 		json_resp = response.json()

	# 		bio = ''
	# 		for f in json_resp['full']:
	# 			paragraph = ''
	# 			for t in f['text']:
	# 				paragraph += t
	# 			bio += paragraph + '\n\n'
			
	# 		print(bio)
	# 		self.bio_container.setText(bio)
			

# method needs to make a search req and then create Artist obj with mkid
def search(artist, song='', album=''):

	# replace spaces in the url with the '%20'
	query = re.sub('\s+', '%20', artist)

	cwd = os.getcwd()
	if not cwd.find('/spotify_infosuite'):
		cwd = cwd + '/spotify_infosuite'

	with open(cwd + '/credentials.json') as creds:    
		credentials = json.load(creds)

	appid = credentials['musikki']['appid']
	appkey = credentials['musikki']['appkey']

	url = 'https://music-api.musikki.com/v1/artists?'
	url = url + 'q=[artist-name:' + query + ']'
	url = url + ',[query-type:suggest]'
	
	url = url + '&appkey=' + appkey
	url = url + '&appid=' + appid

	response = requests.get(url)
	json_resp = response.json()
	# print(json.dumps(json_resp))
	mkid = 0
	if json_resp['summary']['result_count'] > 0:
		mkid = json_resp['results'][0]['mkid']

	artist = Artist(mkid, json_resp['results'][0]['name'], appid, appkey)
	return artist
	# print(json.dumps(response.json()))
