import requests
import re
import json
import os.path


class Artist:

	def __init__(self, mkid, artist, appid, appkey):
		print(mkid)
		if mkid == 0:
			print('no artist found')
		self.mkid = mkid
		self.artist = artist
		self.appid = appid
		self.appkey = appkey

	def get_full_bio(self):
		url = 'https://music-api.musikki.com/v1/artists'
		url = url + '/' + str(self.mkid) + '/bio'
		url = url + '?appkey=' + self.appkey
		url = url + '&appid=' + self.appid

		response = requests.get(url)
		json_resp = response.json()

		bio = ''
		for f in json_resp['full']:
			paragraph = ''
			for t in f['text']:
				paragraph += t
			bio += paragraph + '\n\n'
		
		return bio

# method needs to make a search req and then create Artist obj with mkid
def search(artist, song='', album=''):
	# print('in search() in musikki.py')
	# print('you searched for: ', artist, ' ', song, ' ', album)

	# Import API Keys
	with open(os.path.dirname(__file__) + '/../credentials.json') as creds:    
		credentials = json.load(creds)

	appid = credentials['musikki']['appid']
	appkey = credentials['musikki']['appkey']

	# replace spaces in the url with the '%20'
	query = re.sub('\s+', '%20', artist)

	url = 'https://music-api.musikki.com/v1/artists?'
	url = url + 'q=[artist-name:' + query + ']'
	url = url + '&appkey=' + appkey
	url = url + '&appid=' + appid

	response = requests.get(url)
	json_resp = response.json()

	mkid = 0
	if json_resp['summary']['result_count'] > 0:
		mkid = json_resp['results'][0]['mkid']

	artist = Artist(mkid, artist, appid, appkey)
	return artist
	# print(json.dumps(response.json()))