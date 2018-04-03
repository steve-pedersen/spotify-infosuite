"""
Fall 2017 CSc 690
File: controller.py
Author: Steve Pedersen & Andrew Lesondak
System: OS X
Date: 12/13/2017
Usage: python3 spotify_infosuite.py
Dependencies: model, musikki, playback, reviews, view, requests, urllib, unidecode, pyqt5
Description: Controller class.  Used to generate window frames and handle events, such as key presses, mouse clicks.
                                It also handles calculations needed to display elements to the window correctly.
"""

import model
import view
import playback
import musikki
import flickr
from flickr import flickr_thread
from reviews import reviews

import json
import sys
import threading
import requests
import urllib
import ssl
import os
import sys
import shutil
import unidecode
import string

from threading import Thread
from time import sleep
from urllib.request import urlopen
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *
from PyQt5 import QtNetwork, QtCore
from PyQt5.QtGui import *
from PyQt5 import QtGui


class Controller(QWidget):
	"""Handles all logic to build frames and dispatch content to window.

	Args:
		app (object) -- QApplication
		use_default (bool) -- Use default window size or not

	"""
	def __init__(self, app, use_default=True):
		super().__init__()
		self.app = app

		self.determine_window_size(use_default)

		# Build the main view: Multi-Frame Window
		self.multi_frame_window = view.MultiFrameWindow(
			self.window_x, 
			self.window_y, 
			self.window_w, 
			self.window_h, 
			"Spotify Info Suite",	# window title
			"multi_frame_window"	# object name
		)
		self.multi_frame_window.show()

		self.init_playback_frame()
		self.init_bio_frame()
		self.init_news_frame()
		self.init_review_frame()
		self.init_images_frame()
		self.init_lyrics_frame()
		self.init_social_frame()


	def determine_window_size(self, use_default_size):
		"""Window scales to a 1080 screen resolution by default, but will revert to your
		own screen resolution if the app window ends up being bigger than your screen
		or if use_default_size is set to False

		Args:
			use_default_size (bool) -- Use default window size or not

		"""
		screen_resolution = self.app.desktop().screenGeometry()
		self.screen_width = screen_resolution.width()
		self.screen_height = screen_resolution.height()
		
		# minimum window dimensions
		min_w, min_h = 1440, 900
		
		# default window dimensions
		def_w, def_h = 1920, 1080
		window_fits = False

		while not window_fits:

			if not use_default_size:
				w = self.screen_width
				h = self.screen_height
			else:
				w = def_w
				h = def_h

			space_w = w / 4
			space_h = h / 4
			self.window_w = w - space_w
			self.window_h = h - space_h
			self.window_x = space_w / 4
			self.window_y = space_h / 2

			if not use_default_size:
				window_fits = True
			elif self.window_w <= min_w and self.window_h <= min_h:
				window_fits = True
			else:
				def_w = min_w
				def_h = min_h


	def init_bio_frame(self):
		"""
		Initialize Bio frame and make the initial async request to Musikki for the Bio.

		"""
		x = 0
		y = self.window_h * 0.1
		w = self.window_w / 3
		h = self.window_h*3/4 - y
		self.bio_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "bio_frame"
		)
		self.bio_frame.set_display_title("Bio", 10, 5)
		self.bio_expando_btn = self.bio_frame.create_expando_button()
		self.bio_expando_btn.clicked.connect(self.expand_bio)

		self.multi_frame_window.add_frame_bio(self.bio_frame)

		self.bio_nam = QtNetwork.QNetworkAccessManager()
		self.bio_nam.finished.connect(self.search_bio_handler)

		self.musikki_artist = musikki.search(self.current_artist)
		
		if not self.musikki_artist.is_found:
			# try again with formatted string
			formatted_artist = self.format_unicode_alpha(self.current_artist)
			self.musikki_artist = musikki.search(formatted_artist)
		
		if self.musikki_artist.is_found:
			self.musikki_artist.get_full_bio(self.bio_nam)
		else:
			self.bio_frame.set_display_text('No results for current artist.', 10, 45)


	def init_news_frame(self):
		"""
		Initialize News frame and make the initial async request to Musikki.

		"""
		x = 0
		y = self.window_h*3 / 4
		w = self.window_w / 3
		h = self.window_h / 4
		self.news_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "news_frame"
		)
		self.news_frame.set_display_title("News", 10, 5)
		self.multi_frame_window.add_frame(self.news_frame)

		self.news_nam = QtNetwork.QNetworkAccessManager()
		self.news_nam.finished.connect(self.news_handler)

		if self.musikki_artist.is_found:
			self.musikki_artist.get_news(self.news_nam)


	def init_playback_frame(self):
		"""
		Initialize Playback Frame, make the connection to Spotify and create playback listener thread.

		"""
		self.spotify = self.open_spotify()
		self.update_current_playing()

		self.playback_title_x = 10
		self.playback_title_y = 5

		x = 0
		y = 0
		w = self.window_w / 3
		h = self.window_h * 0.1
		self.playback_frame = model.Frame(self, self.multi_frame_window, x,y, w,h, 'playback_frame')
		self.playback_frame.set_display_title(
			self.get_current_playing(), self.playback_title_x, self.playback_title_y
		)
		
		self.playback_frame.create_playback_buttons()		
		self.playback_frame.get_playback_prev_button().clicked.connect(self.prev)
		self.playback_frame.get_playback_play_button().clicked.connect(self.play_pause)
		self.playback_frame.get_playback_next_button().clicked.connect(self.next)

		self.multi_frame_window.add_frame(self.playback_frame)

		# spawn a playback listener to keep InfoSuite in sync with Spotify
		self.listener = Listener(self.current_playing, self.spotify)
		self.listener.song_change.connect(self.update_playback_display)
		self.listener.run()	


	def init_lyrics_frame(self):
		"""
		Initialize Lyrics frame and make the initial async request to Genius.

		"""
		x = self.window_w / 3
		y = 0
		w = self.window_w / 3
		h = self.window_h * 0.75
		self.lyrics_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "lyrics_frame"
		)
		self.lyrics_frame.set_display_title("Lyrics", 10, 5)

		self.lyrics_expando_btn = self.lyrics_frame.create_expando_button()
		self.lyrics_expando_btn.clicked.connect(self.expand_lyrics)

		self.multi_frame_window.add_frame(self.lyrics_frame)

		self.lyrics_nam = QtNetwork.QNetworkAccessManager()
		self.lyrics_nam.finished.connect(self.lyrics_handler)

		self.get_lyrics()


	def init_review_frame(self):
		"""
		Initialize Review (Pitchfork) frame and make the initial async request to Pitchfork & Metacritic.

		"""
		x = self.window_w * 2 / 3
		y = self.window_h / 2
		w = self.window_w / 3
		h = self.window_h * 0.37
		title_x = 10
		title_y = 5
		self.review_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, 'review_frame'
		)
		self.review_frame.set_display_title('Reviews', title_x, title_y)
		self.review_expando_btn = self.review_frame.create_expando_button()
		self.review_expando_btn.clicked.connect(self.expand_review)
		self.multi_frame_window.add_frame(self.review_frame)

		self.init_metacritic_frame()

		self.get_pitchfork_review()
		self.get_metacritic_review()


	def init_metacritic_frame(self):
		"""
		Initialize Metacritic frame.

		"""
		x = self.window_w * 2/3
		y = self.window_h/2 + self.window_h*0.37
		w = self.window_w / 3		
		h = self.window_h * 0.13
					
		self.metacritic_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, 'metacritic_frame'
		)	
		self.multi_frame_window.add_frame(self.metacritic_frame)	


	def init_images_frame(self):
		"""
		Initialize Images frame and make the initial async requests to Musikki and Flickr.

		"""
		x = self.window_w * 2 / 3
		y = 0
		w = self.window_w / 3
		h = self.window_h / 2
		title_x = 10
		title_y = 5
		self.images_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, 'images_frame'
		)
		self.images_frame.set_display_title('Images', title_x, title_y)

		self.multi_frame_window.add_frame(self.images_frame)

		self.images_nam = QtNetwork.QNetworkAccessManager()
		self.images_nam.finished.connect(self.musikki_images_handler)

		self.get_images()


	def init_social_frame(self):
		"""
		Initialize Social frame and make the initial async requests to Musikki.

		"""
		x = self.window_w / 3
		y = self.window_h * 0.75
		w = self.window_w / 3
		h = self.window_h * 0.25
		self.social_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "social_frame"
		)

		self.social_frame.set_display_title("Social", 10, 5)
		self.multi_frame_window.add_frame(self.social_frame)

		self.social_nam = QtNetwork.QNetworkAccessManager()
		self.social_nam.finished.connect(self.social_handler)

		if self.musikki_artist.is_found:
			self.musikki_artist.get_social_media_twitter(self.social_nam)
		else:
			self.social_frame.set_display_text('No results for current artist.', 10, 45)


	def get_images(self):
		"""Spawn a thread to request images from Flickr. 
		Thread will signal to update_images_frame() handler with the downloaded images.

		"""
		if self.musikki_artist.is_found:
			self.musikki_artist.get_full_images(self.images_nam)

		requester = flickr_thread.Requester()
		requester.flickr_reciever.connect(self.update_images_frame)
		requester.get_images(self.current_artist)


	def get_pitchfork_review(self):
		"""Spawn a thread to fetch a review for current album from Pitchfork.com. 
		Thread will signal to update_review_frame() handler with the downloaded review.

		"""
		requester = reviews.Requester()
		requester.pitchfork_receiver.connect(self.update_review_frame)
		artist, album = self.format_unicode_alpha([self.current_artist, self.current_album])
		print('before asking pitchfork...', artist)
		requester.get_pitchfork_review(artist, album)


	def get_metacritic_review(self):
		"""Spawn a thread to fetch a review for current album from a Metacritic API. 
		Thread will signal to update_review_frame() handler with the downloaded review.

		"""
		requester = reviews.Requester()
		requester.metacritic_receiver.connect(self.update_review_frame)
		requester.get_metacritic_review(self.current_artist, self.current_album)


	def update_everything(self):
		"""
		Fetch new info for all frames.

		"""
		self.update_current_playing()
		self.playback_frame.set_display_title(
			self.current_playing, self.playback_title_x, self.playback_title_y
		)

		self.update_artist_info(update_playback=False)		
		self.update_album_info(update_playback=False)
		self.update_song_info(update_playback=False)


	def update_artist_info(self, update_playback=True):
		"""
		Fetch new info for the following frames, which are dependent on artist:	
			Bio, News, Social Media, Images

		"""
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)		

		self.musikki_artist = musikki.search(self.get_current_artist())
		self.musikki_artist.get_full_bio(self.bio_nam)
		self.musikki_artist.get_news(self.news_nam)
		self.musikki_artist.get_social_media_twitter(self.social_nam)
		self.images_frame.clear_images_list()
		self.get_images()


	def update_song_info(self, update_playback=True):
		"""
		Fetch new info for the following frames, which are dependent on song:	
			Lyrics

		"""
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)	

		self.get_lyrics()	


	def update_album_info(self, update_playback=True):
		"""
		Fetch new info for the following frames, which are dependent on album:	
			Reviews: Pitchfork, Metacritic

		"""
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)	

		self.get_pitchfork_review()
		self.get_metacritic_review()


	def update_current_playing(self):
		"""
		Update formatted playback, artist, song and album strings from Spotify.	

		"""
		self.current_playing = self.get_current_playing()
		self.current_artist = self.get_current_artist()
		self.current_song = self.get_current_song()
		self.current_album = self.get_current_album()	
		print('='*60, '\n\n-----Now Playing-----')
		print('Artist:\t', self.current_artist)
		print('Song:\t', self.current_song)
		print('Album:\t', self.current_album, '\n')


	def get_lyrics(self, url=''):
		"""Make an async request to Genius.com for lyrics.	
		
		Args:
			url (str) -- Either the url we know or the one returned in a 301 response.

		"""
		artist, song = self.format_unicode_alpha([self.current_artist, self.current_song])
		print('Searching lyrics for: ', artist, ' - ', song)

		if url == '':
			url = "https://genius.com/%s-%s-lyrics" % (artist.replace(' ', '-'), song.replace(' ', '-'))
		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		self.lyrics_nam.get(req)


	def set_lyrics(self, url='', lyrics_exist=True):
		"""Make synchronous lyrics request, then set text in the lyrics frame.	
		
		Args:
			url (str) -- URL to request lyrics if not using default URL
			lyrics_exist (bool) -- Don't make request for lyrics if you know they don't exist.

		"""
		error = "Error: Could not find lyrics."
		proxy = urllib.request.getproxies()

		# remove punctuation and convert to English alphabet
		artist, song = self.format_unicode_alpha([self.current_artist, self.current_song])
		
		if lyrics_exist:
			try:
				if url == '':
					url = "https://genius.com/%s-%s-lyrics"%(artist.replace(' ', '-'),song.replace(' ', '-'))
				lyricspage = requests.get(url, proxies=proxy)

				soup = BeautifulSoup(lyricspage.text, 'html.parser')
				lyrics = soup.text.split(' Lyrics')[3].split('More on Genius')[0]
				if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
					lyrics = error

				self.lyrics_frame.set_results(True)
			except Exception:
				lyrics = error
		else:
			lyrics = error
		
		# set those lyrics on the frame
		self.lyrics_frame.set_display_text(lyrics, 10, 45, 'lyrics_text')


	def format_unicode_alpha(self, strings):
		"""Removes punctuation and replaces non-English alphabet chars with closest equivalent.	
		
		Args:
			strings (list:str) -- A list of strings or single string to be formatted

		"""
		formatted_strings = []
		is_list = True
		
		if isinstance(strings, str):
			is_list = False
			strings = [strings]
				
		for s in strings:
			s = unidecode.unidecode(s)		
			s = s.translate(str.maketrans('','',string.punctuation))
			formatted_strings.append(s)

		return (formatted_strings if is_list else formatted_strings[0])


	def update_review_frame(self, review):
		"""Reviews Handler.	
		
		Args:
			review (str:object) -- Either Pitchfork formatted string or a metacritic.Review object
				Review object consists of the following:
				artist album date critic_rating critic_count user_rating user_count img_url

		"""
		# Pitchfork frame
		if isinstance(review, str):
			self.review_frame.set_results(True)
			self.review_frame.set_display_text(review)

		# Metacritic frame
		elif isinstance(review, object):
			default_image = QPixmap(os.path.dirname(__file__)+'/info-icon.png')

			if not review.has_review:
				self.metacritic_frame.default_metacritic_content(default_image)
			else:
				try:
					album_image = urllib.request.urlopen(review.img_url).read()
				except:
					album_image = default_image
				
				review.pixmap = album_image
				self.metacritic_frame.add_metacritic_content(review)
				
				print('\n-----Metacritic Results-----')
				print(review.artist, ' - ', review.album)
				print('Critic Score:\t', review.critic_rating, '\t(',review.critic_count,' reviews)')
				print('User Score:\t', review.user_rating, '\t(',review.user_count,' reviews)\n')


	def update_images_frame(self, images):
		"""Images handler.	
		
		Args:
			images (list) -- List of QPixmaps

		"""
		if len(images) > 0:
			# add image scrolling buttons
			self.images_frame.create_image_buttons()
			self.images_frame.get_image_next_button().clicked.connect(self.next_image_handler)
			self.images_frame.get_image_prev_button().clicked.connect(self.prev_image_handler)
			self.images_frame.get_image_next_button().show()
			self.images_frame.get_image_prev_button().show()
			# add the flickr images
			self.images_frame.add_flickr_artist_images(images)


	def lyrics_handler(self, reply):
		"""Lyrics handler.	
		
		Args:
			reply (object) -- QNetworkReply

		"""
		er = reply.error()

		if er == QtNetwork.QNetworkReply.NoError:

			if reply.rawHeader(QByteArray(b'Status')) == '301 Moved Permanently':
				qbyteurl = reply.rawHeader(QByteArray(b'Location'))
				url = ''
				for q in qbyteurl:
					url += q
				
				# parse the html for lyrics
				self.set_lyrics(url)
			
			elif reply.rawHeader(QByteArray(b'Status') != '200 OK'):
				print('response not a 301 or 200. it is: ', reply.rawHeader(QByteArray(b'Status')))

		else:
			self.set_lyrics(url='', lyrics_exist=False)


	def news_handler(self, reply):
		"""News handler.	
		
		Args:
			reply (object) -- QNetworkReply

		"""
		default_img = os.path.dirname(__file__) + '/info-icon.png'
		results = {}

		er = reply.error()

		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()

			if len(json_resp['summary'].toObject()['errors'].toArray()) == 0 \
				and json_resp['summary'].toObject()['result_count'].toInt() > 0:

				counter = 0				
				resultlist = []
				for r in json_resp['results'].toArray():

					if counter < 1:

						r = r.toObject()

						results['author'], name = [], ''
						if r['author_info'] != '':
							try:
								if r['author_info'].toObject()['name'] != '':
									name = r['author_info'].toObject()['name'].toString()
							except:
								name = ''
						results['author'] = name

						results['source'], avatar, title = [],'',''
						if r['source'] != '':
							if r['source'].toObject()['title'] != '':
								results['src_title'] = r['source'].toObject()['title'].toString()
							if r['source'].toObject()['avatar'].toString() != '':
								avatar = r['source'].toObject()['avatar'].toString()
						results['source'].extend([avatar, title])

						results['date'], year, month, day = '','','',''
						if r['publish_date'] != '':
							if str(r['publish_date'].toObject()['year'].toInt()) != '':
								year = str(r['publish_date'].toObject()['year'].toInt())
							if str(r['publish_date'].toObject()['month'].toInt()) != '':
								month = str(r['publish_date'].toObject()['month'].toInt())
							if str(r['publish_date'].toObject()['day'].toInt()) != '':
								day = str(r['publish_date'].toObject()['day'].toInt())
						results['date'] = year +'-'+ month +'-'+ day

						results['mkid'] = ''
						if str(r['mkid'].toInt()) != '':
							results['mkid'] = str(r['mkid'].toInt())

						results['title'] = ''
						if r['title'].toString() != '':
							results['title'] = r['title'].toString()

						results['newsurl'] = ''
						if r['url'].toString() != '':
							results['newsurl'] = r['url'].toString()

						results['summary'] = ''
						if r['summary'].toString() != '':
							results['summary'] = r['summary'].toString()

						results['imgurl'] = ''
						if r['image'].toString() != '':
							results['imgurl'] = r['image'].toString()
							try:
								url = results['imgurl']

								r = requests.get(url, stream=True)
								filename = os.path.dirname(__file__)+'/images/'+results['title']+'.jpg'
								with open(filename, 'wb') as fd:
									for chunk in r.iter_content(chunk_size=128):
										fd.write(chunk)
								results['newsicon'] = QPixmap(filename)

							except BaseException as e:
								print(e)
								results['newsicon'] = QPixmap(default_img)
					else:
						break

						resultlist.append(results)
					counter += 1
				# end for
				results['found'] = True
				try:
					results['newsicon'] = results['newsicon'] if results['newsicon'] else QPixmap(default_img)	
				except:
					results['newsicon'] = QPixmap(default_img)
				self.news_frame.add_news(results)
			#end if
			else:
				print('No news found')
				results['found'] = False
				results['message'] = 'No news for this artist.'
				self.news_frame.add_news(results, QPixmap(default_img))
		else:
			print('No news found')
			results['found'] = False
			results['message'] = 'No news for this artist.'
			self.news_frame.add_news(results, QPixmap(default_img))


	def search_bio_handler(self, reply):
		"""Biography handler.	
		
		Args:
			reply (object) -- QNetworkReply

		"""
		er = reply.error()

		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()

			bio = ''
			for f in json_resp['full'].toArray():
				f = f.toObject()
				paragraph = ''
				for i, t in enumerate(f['text'].toArray()):
					t = t.toString()
					paragraph += f['title'].toString()+'\n\n'+t.rstrip() if i==0 else (' '+t.rstrip())
				bio += paragraph + '\n\n'

			self.bio_frame.set_results(True)
			self.bio_frame.set_display_text(bio, 10, 45, 'bio_text')
			
		else:
			self.bio_frame.set_display_text('No artist bio found.', 10, 45)


	def musikki_images_handler(self, reply):
		"""Musikki images handler.	
		
		Args:
			reply (object) -- QNetworkReply

		"""
		urls, pixmaps, widths, heights = [], [], [], []

		er = reply.error()
		
		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()
			notfound_count = 0

			if len(json_resp['results'].toArray()) > 0:
				f = json_resp['results'].toArray()

				thumb = f[0].toObject()['thumbnails'].toArray()[0].toObject()
				thumb_url = thumb['url'].toString()
				thumb_width = thumb['width'].toInt()
				thumb_height = thumb['height'].toInt()

				try:
					context = ssl._create_unverified_context()
					data = urlopen(thumb_url, context=context).read()
					pixmap = QPixmap()
					pixmap.loadFromData(data)
					pixmaps.append(pixmap)
				except:
					notfound_count += 1

				urls.append(thumb_url)
				widths.append(thumb_width)
				heights.append(thumb_height)

		if notfound_count > 0:
			print(notfound_count, " 404 responses in image handler")

		if len(pixmaps) > 0:
			# load the biggest image as the first and only pixmap
			biggest = 0
			for i, p in enumerate(pixmaps):
				if p.width() > biggest:
					biggest = i
			pixmaps[0] = pixmaps[biggest]
			widths[0] = widths[biggest]
			heights[0] = heights[biggest]
			self.images_frame.add_musikki_artist_images(pixmaps, widths, heights)


	def social_handler(self, reply):
		"""Social handler.	
		
		Args:
			reply (object) -- QNetworkReply

		"""
		er = reply.error()

		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()

			found = True
			try:
				service_name = json_resp['service_name'].toString()
			except:
				found = False
				service_name = ''

			try:
				year = json_resp['timeline_posts'].toArray()[0].toObject()['date'].toObject()['year'].toInt()
				month = json_resp['timeline_posts'].toArray()[0].toObject()['date'].toObject()['month'].toInt()
				day = json_resp['timeline_posts'].toArray()[0].toObject()['date'].toObject()['day'].toInt()
			except:
				year, month, day = 0000, 00, 00

			date = str(month) + '/' + str(day) + '/' + str(year)

			try:
				content = json_resp['timeline_posts'].toArray()[0].toObject()['content'].toString()
			except:
				content = ''

			social_text = date + ' - via ' + service_name + '\n\n' + content

			if found:
				self.social_frame.set_display_text(social_text, 10, 45, 'social_text')
				self.musikki_artist.twitter_search = False
			elif not found:
				self.social_frame.set_display_text('No social media found.', 10, 45)
				self.musikki_artist.facebook_search = False

		elif self.musikki_artist.facebook_search == False:
			self.musikki_artist.get_social_media_facebook(self.social_nam)
		else:
			self.social_frame.set_display_text('No social media found.', 10, 45)
			self.musikki_artist.facebook_search = False


	def next_image_handler(self):
		self.images_frame.next_image()


	def prev_image_handler(self):
		self.images_frame.prev_image()


	def update_playback_display(self):
		"""
		Playback handler.
		
		"""
		if self.current_playing != self.get_current_playing():
			if (self.current_artist == self.get_current_artist() and
				self.current_song != self.get_current_song()):
				if self.current_album != self.get_current_album():
					print('Album change...')
					self.update_album_info(update_playback=True)
					self.update_song_info(update_playback=False)
				else:
					print('Song change...')
					self.update_song_info(update_playback=True)
			else:
				print('Artist and song change...')
				self.update_everything()
		elif (self.current_artist == self.get_current_artist() and
			self.current_album != self.get_current_album()):
			print('Album changed but song & artist did not...')
			self.update_album_info(update_playback=True)
			self.update_song_info(update_playback=False)


	def expand_bio(self):
		if self.bio_frame.has_results():
			self.build_popup(self.bio_frame)
		else:
			print('No bio results, so no bio popup')


	def expand_lyrics(self):
		if self.lyrics_frame.has_results():
			self.build_popup(self.lyrics_frame)
		else:
			print('No lyrics results, so no lyrics popup')


	def expand_review(self):
		if self.review_frame.has_results():
			self.build_popup(self.review_frame)
		else:
			print('No review results, so no review popup')


	def build_popup(self, source_frame):
		"""Build a SingleFrameWindow popup window.	
		
		Args:
			source_frame (object) -- model.Frame is the content for the popup

		"""
		offset = 50
		self.popup_window = view.SingleFrameWindow(self.screen_width, self.screen_height)
		self.popup_window.init_popup(
			self.window_x-offset, self.window_y-offset, source_frame.display_title, 'single_frame_window'
		)
		source_frame.create_popup(self.popup_window)
		self.popup_window.add_frame(source_frame)
		self.popup_window.show()


	def open_spotify(self):
		spotify = playback.Playback() 
		return spotify

	def play_pause(self):
		self.spotify.play_pause()

	def next(self):
		self.spotify.next()

	def prev(self):
		self.spotify.prev()

	def pause(self):
		self.spotify.pause()

	def get_current_artist(self):
		return self.spotify.get_current_artist()

	def get_current_song(self):
		return self.spotify.get_current_song()

	def get_current_album(self):
		return self.spotify.get_current_album()

	def get_current_playing(self):
		return self.get_current_artist() + ' - ' + self.get_current_song()


class Listener(QThread):

	song_change = pyqtSignal()
	
	"""Listener object that can run playback synchronization threads.	
	
	Args:
		stored_song (str) -- formatted string (Artist - Song Title)
		spotify (object) -- playback.Playback object which connects and talks to Spotify

	"""
	def __init__(self, stored_song, spotify):
		super().__init__()
		self.stored_song = stored_song.rstrip()
		self.spotify = spotify

		# start a synchronization thread that will close when app does
		self.playback_sync_thread = Thread(target=self.sync_playback)
		self.playback_sync_thread.setDaemon(True) 

	def run(self):
		self.playback_sync_thread.start() 	

	def sync_playback(self):
		"""
		Every 1 second, check the stored_song against what Spotify is currently playing.

		"""
		while True:
			if self.stored_song != self.spotify.get_current_playing().rstrip():
				self.song_change.emit()
				self.stored_song = self.spotify.get_current_playing().rstrip()
			
			sleep(1)

