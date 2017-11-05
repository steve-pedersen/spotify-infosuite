
import requests
import re
import json


class Artist:

	def __init__(self, mkid):
		print('')


# method needs to make a search req and then create Artist obj with mkid
def search(artist, song='', album=''):
	# print('in search() in musikki.py')
	# print('you searched for: ', artist, ' ', song, ' ', album)

	# Import API Keys
	with open('./credentials.json') as creds:    
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

	print(json.dumps(response.json()))