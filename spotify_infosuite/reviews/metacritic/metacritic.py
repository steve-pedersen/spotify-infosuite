"""
Fall 2017 CSc 690
File: metacritic.py
Author: Steve Pedersen & Andrew Lesondak
System: OS X
Date: 12/13/2017
Usage: python3 spotify_infosuite.py
Dependencies: urllib
Description: MetaReview class.  Used to get search Metacritic API for album review score.

"""

from urllib.request import urlopen
from urllib.request import Request
import ssl
import json

class MetaReview:
	"""
	Class representing the fetched review.
	
	"""
	def __init__(self, has_review):
		self.has_review = has_review
		self.not_found_message = 'No results found with Metacritic'
	
	def load(self, artist, album, date, critic_rating, critic_count,
			 user_rating, user_count, img_url):
		""" 
		Set the property values for the object review.
			
		"""
		self.artist = artist
		self.album = album
		self.date = date
		self.critic_rating = critic_rating
		self.critic_count = critic_count
		self.user_rating = user_rating
		self.user_count = user_count
		self.img_url = img_url


def search(artist, album, apikey):
	"""Makes the request to Metacritic API and returns a MetaReview object singleton.
	
	Args:
		artist (str)
		album (str)
		apikey (str)

	"""
	request = Request(
		url='https://api-marcalencc-metacritic-v1.p.mashape.com/album/' + album,
	  	data=None,
	  	headers={
		  	"X-Mashape-Key": apikey,
  			"Accept": "application/json"
  		}
	)
	try:
		context = ssl._create_unverified_context()
		response = urlopen(request, context=context)	
		text = response.read().decode('UTF-8')
		# the server responds with json so we load it into a dictionary
		results = json.loads(text)
		# print(results)
	except:
		results = []
	
	# since we didn't pass in the year there may be more than one match of the album name
	# iterate through results and check artist name for a match
	for result in results:

		try:
			match_found = result['Message'] != 'No matching item found!'
		except Exception:
			match_found = True
		try:
			mc_artist = result['PrimaryArtist']
		except:
			mc_artist = ''

		if not match_found:
			continue
		elif match_found and mc_artist == artist:
			try:
				mc_name = result['PrimaryArtist']
			except Exception:
				mc_name = ''
			try:
				mc_album = result['Title']
			except Exception:
				mc_album = ''
			try:
				mc_date = result['ReleaseDate']
			except Exception:
				mc_date = ''
			try:
				mc_critic_rating = result['Rating']['CriticRating']
			except Exception:
				mc_critic_rating = ''
			try:
				mc_critic_review_count = result['Rating']['CriticReviewCount']
			except Exception:
				mc_critic_review_count = ''
			try:
				mc_user_rating = result['Rating']['UserRating']
			except Exception:
				mc_user_rating = ''
			try:
				mc_user_review_count = result['Rating']['UserReviewCount']
			except Exception:
				mc_user_review_count = ''
			try:
				mc_image_url = mc_image_url = result['ImageUrl']
			except Exception:
				mc_image_url = ''

			metacritic = MetaReview(has_review=True)
			metacritic.load(mc_name,mc_album,mc_date,mc_critic_rating,mc_critic_review_count,
				mc_user_rating, mc_user_review_count, mc_image_url
			)
			# print(metacritic)
			return metacritic

	# no match found...
	metacritic = MetaReview(has_review=False)
	return metacritic

