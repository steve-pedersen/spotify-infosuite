from reviews.pitchfork import pitchfork
from reviews.metacritic import metacritic
import threading
import json
import os
from threading import Thread
from PyQt5.QtCore import *


class Requester(QThread):

	pitchfork_receiver = pyqtSignal(str)
	metacritic_receiver = pyqtSignal(object)

	"""
	This class makes threaded requests for reviews from various sources.
	It emits pyqtSignals with response objects or strings.

	"""
	def __init__(self):
		super().__init__()


	def get_metacritic_review(self, artist, album):
		"""
		Spawns a thread to search for a review for an album, then emits a pyqtsignal 
		with the review object from metacritic.Review

		"""
		def __get_data(arg1, arg2):
			artist, album = arg1, arg2
			album = self.get_formatted_album_string(album, 'metacritic')

			# with open('./reviews/credentials.json') as creds:
			with open(os.path.dirname(__file__) + '/credentials.json') as creds:
				credentials = json.load(creds)
			apikey = credentials['metacritic']['apikey']
			
			print('Searching Metacritic for album: ', album)
			m = metacritic.search(artist, album, apikey)

			# if m.has_review:
			self.metacritic_receiver.emit(m)			
			
		worker = threading.Thread(target=__get_data, args=[artist,album])
		worker.setDaemon(True) 
		worker.start()		

	def get_pitchfork_review(self, artist, album):
		"""
		Spawns a thread to search for a review for an album, then emits a pyqtsignal 
		with the formatted review string.

		"""
		def __get_data(arg1, arg2):
			artist, album = arg1, arg2
			album = self.get_formatted_album_string(album)
			
			print('Searching Pitchfork for artist/album: ', artist,' - ',album)
			p = pitchfork.search(artist, album)

			if p.has_review:
				review = 'Pitchfork - Rating: '+str(p.score())+' - '+p.album() \
					+' ('+str(p.year())+')'+'\n\n'+p.editorial() #[:800]
			else:
				review = p.message

			self.pitchfork_receiver.emit(review)
			
		worker = threading.Thread(target=__get_data, args=[artist,album])
		worker.setDaemon(True) 
		worker.start()

	def get_formatted_album_string(self, album, source=''):
		"""
		This is bad... meant only to be a temporary workaround to get some of my
		favorite albums to work with InfoSuite.

		"""
		album = album.replace('(Deluxe Version)','').rstrip() \
			.replace('[Remastered]','') \
			.replace('(Deluxe Edition)','') \
			.replace('(Remastered Deluxe Edition)','') \
			.replace('(Non UK Version)','') \
			.replace('(US Internet Release)','') \
			.replace('(Special Edition)','') \
			.replace('(Remastered)','') \
			.replace('(Legacy Edition)','') \
			.replace('(Deluxe Edition [Remastered])','') \
			.replace('(U.S. Version)','') \
			.replace('(1998 Remastered Version)','') \
			.replace('(2011 Remastered Version)','') \
			.replace('(2011 Remaster)','') \
			.replace('(Deluxe)','') \
			.replace('Deluxe Edition','') \
			.replace('(Expanded Edition)','') \
			.replace('(Remastered Original Album)','') \
			.replace("(20th Anniversary Collector's Edition)",'')

		if source == 'metacritic':
			album = album.replace(' ', '-')

		return album



