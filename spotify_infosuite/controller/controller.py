import model
import view
import playback
import musikki
import flickr
# import reviews #pitchfork
# from reviews.pitchfork import pitchfork
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

	def __init__(self, app, screen_width, screen_height, use_default=True):
		super().__init__()

		self.screen_width, self.screen_height = screen_width, screen_height
		self.determine_window_size(screen_width, screen_height, use_default)

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

	# Window scales to a 1080 screen resolution by default, but will revert to your 
	# own screen resolution if the app window ends up being bigger than your screen
	# or if use_default_size is set to False
	def determine_window_size(self, screen_width, screen_height, use_default_size):
		# minimum window dimensions
		min_w, min_h = 1440, 900
		# default window dimensions
		def_w, def_h = 1920, 1080
		window_fits = False
		
		while not window_fits:

			if not use_default_size:
				w = screen_width
				h = screen_height
			else:
				w = def_w
				h = def_h

			space_w = w / 4
			space_h = h / 4
			self.window_w = w - space_w
			self.window_h = h - space_h
			self.window_x = space_w / 4 # if not use_default_size else space_w * 1.17
			self.window_y = space_h / 2 # if not use_default_size else space_h * 1.2

			if not use_default_size:
				window_fits = True
			elif self.window_w <= min_w and self.window_h <= min_h:
				window_fits = True
			else:
				def_w = min_w
				def_h = min_h 

	def init_bio_frame(self):
		x = 0
		y = self.window_h * 0.1
		w = self.window_w / 3
		h = self.window_h*2/3 - y
		self.bio_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "bio_frame"
		)
		self.bio_frame.set_display_title("Bio", 10, 5)
		self.bio_expando_btn = self.bio_frame.create_expando_button()
		self.bio_expando_btn.clicked.connect(self.expand_bio)

		self.multi_frame_window.add_frame_bio(self.bio_frame)

		self.bio_nam = QtNetwork.QNetworkAccessManager()
		self.bio_nam.finished.connect(self.search_bio_handler)

		self.musikki_artist = musikki.search(self.get_current_artist())
		if self.musikki_artist.is_found:
			self.musikki_artist.get_full_bio(self.bio_nam)
		else:
			self.bio_frame.set_display_text('No results for current artist.', 10, 45)

	def init_news_frame(self):
		x = 0
		y = self.window_h*2 / 3
		w = self.window_w / 3
		h = self.window_h / 3
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
		x = self.window_w * 2/3
		y = self.window_h/2 + self.window_h*0.37
		w = self.window_w / 3		
		h = self.window_h * 0.13
					
		self.metacritic_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, 'metacritic_frame'
		)	
		# self.metacritic_frame.set_display_title('Metacritic Reviews', 10, 5)

		self.multi_frame_window.add_frame(self.metacritic_frame)	

	def init_images_frame(self):
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

		self.images_frame.create_image_buttons()
		self.images_frame.get_image_next_button().clicked.connect(self.next_image_handler)
		self.images_frame.get_image_prev_button().clicked.connect(self.prev_image_handler)

		self.multi_frame_window.add_frame(self.images_frame)

		self.flickr_images_nam = QtNetwork.QNetworkAccessManager()
		self.flickr_images_nam.finished.connect(self.flickr_images_handler)

		self.images_nam = QtNetwork.QNetworkAccessManager()
		self.images_nam.finished.connect(self.musikki_images_handler)


		self.flickr_artist = flickr.flickr.Flickr(self.get_current_artist())

		if self.musikki_artist.is_found:
			self.musikki_artist.get_full_images(self.images_nam)
			self.flickr_artist.get_full_images(self.flickr_images_nam, self.get_current_artist())
		else:
			self.images_frame.set_display_text('No results for current artist.', 10, 45)

	def init_social_frame(self):
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

	def get_pitchfork_review(self):
		requester = reviews.Requester()
		requester.pitchfork_receiver.connect(self.update_review_frame)
		requester.get_pitchfork_review(self.current_artist, self.current_album)

	def get_metacritic_review(self):
		requester = reviews.Requester()
		requester.metacritic_receiver.connect(self.update_review_frame)
		requester.get_metacritic_review(self.current_artist, self.current_album)

	def update_everything(self):
		# playback info
		self.update_current_playing()
		self.playback_frame.set_display_title(
			self.current_playing, self.playback_title_x, self.playback_title_y
		)

		self.update_artist_info(update_playback=False)		
		self.update_album_info(update_playback=False)
		self.update_song_info(update_playback=False)

	def update_artist_info(self, update_playback=True):
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)		
		
		# Update the collowing frames, which are dependent on artist:
		#	Bio, News, Social Media, Images
		self.musikki_artist = musikki.search(self.get_current_artist())
		self.musikki_artist.get_full_bio(self.bio_nam)		
		self.musikki_artist.get_news(self.news_nam)
		self.musikki_artist.get_social_media_twitter(self.social_nam)
		self.images_frame.clear_images_list()
		self.musikki_artist.get_full_images(self.images_nam)
		self.flickr_artist.get_full_images(self.flickr_images_nam, self.get_current_artist())
		

	def update_song_info(self, update_playback=True):
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)	

		# Update the collowing frames, which are dependent on song:
		#	Lyrics
		self.get_lyrics()	

	def update_album_info(self, update_playback=True):
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)	
		
		# Update the collowing frames, which are dependent on album:
		#	Reviews: Pitchfork, Metacritic
		self.get_pitchfork_review()
		self.get_metacritic_review()

	def update_current_playing(self):
		self.current_playing = self.get_current_playing()
		self.current_artist = self.get_current_artist()
		self.current_song = self.get_current_song()
		self.current_album = self.get_current_album()	
		print('\n\n-----Now Playing-----')
		print('Artist:\t', self.current_artist)
		print('Song:\t', self.current_song)
		print('Album:\t', self.current_album, '\n')

	def get_lyrics(self, url=''):
		artist, song = self.current_artist, self.current_song
		if url == '':
			url = "http://genius.com/%s-%s-lyrics" % (artist.replace(' ', '-'), song.replace(' ', '-'))
		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		self.lyrics_nam.get(req)

	# Reviews Handler
	#
	# Reviews object consists of the following:
	# artist,album,date,critic_rating,critic_count,user_rating,user_count,img_url
	def update_review_frame(self, review):

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
				print('User Score:\t', review.user_rating, '\t(',review.user_count,' reviews)')
				print('-------------------------------------------\n')
	
	# lyrics handler
	def lyrics_handler(self, reply):

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


	def set_lyrics(self, url='', lyrics_exist=True):
		error = "Error: Could not find lyrics."
		proxy = urllib.request.getproxies()

		artist = self.get_current_artist()
		song = self.get_current_song()
		
		if lyrics_exist:
			try:
				if url == '':
					url = "http://genius.com/%s-%s-lyrics" % (artist.replace(' ', '-'), song.replace(' ', '-'))
				lyricspage = requests.get(url, proxies=proxy)

				soup = BeautifulSoup(lyricspage.text, 'html.parser')
				lyrics = soup.text.split('Lyrics')[3].split('More on Genius')[0]
				if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
					lyrics = error

				self.lyrics_frame.set_results(True)
			except Exception:
				lyrics = error
		else:
			lyrics = error
		
		# set those lyrics on the frame
		self.lyrics_frame.set_display_text(lyrics, 10, 45, 'lyrics_text')

	def news_handler(self, reply):
		default_img = os.path.dirname(__file__) + '/info-icon.png'

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
				results = {}
				resultlist = []
				for r in json_resp['results'].toArray():

					if counter < 1:

						r = r.toObject()

						results['author'], name = [], ''
						if r['author_info'] != '':
							if r['author_info'].toObject()['name'] != '':
								name = r['author_info'].toObject()['name'].toString()
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
				self.news_frame.add_news(results)
			#end if
			else:
				print('No news found')
				self.news_frame.add_news('No news for this artist.', QPixmap(default_img))
		else:
			print('No news found')
			self.news_frame.add_news('No news for this artist.', QPixmap(default_img))

	# bio handler
	def search_bio_handler(self, reply):

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
					paragraph += f['title'].toString() + '\n\n' + t.rstrip() if i == 0 else (' ' + t.rstrip())
				bio += paragraph + '\n\n'

			self.bio_frame.set_results(True)
			self.bio_frame.set_display_text(bio, 10, 45, 'bio_text')
			
		else:
			self.bio_frame.set_display_text('No artist bio found.', 10, 45)

	def flickr_images_handler(self, reply):
		urls, pixmaps, widths, heights = [], [], [], []

		er = reply.error()

		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()
			notfound_count = 0

			if (json_resp['stat'] == 'ok'):
				for p in json_resp['photos'].toObject()['photo'].toArray():
					photo_url = 'https://farm' + str(p.toObject()['farm'].toInt()) + '.staticflickr.com/' + str(p.toObject()['server'].toString())
					photo_url = photo_url + '/' + str(p.toObject()['id'].toString()) + '_' + str(p.toObject()['secret'].toString()) + '.jpg'

					try:
						context = ssl._create_unverified_context()
						data = urlopen(photo_url, context=context).read()
						pixmap = QPixmap()
						pixmap.loadFromData(data)
						pixmaps.append(pixmap)
					except:
						notfound_count += 1

					urls.append(photo_url)

		if notfound_count > 0:
			print(notfound_count, " 404 responses in image handler")

		if len(pixmaps) > 0:
			self.images_frame.add_flickr_artist_images(pixmaps)
		else:
			# use default image of dirty-piano.jpg
			pixmaps = [QPixmap(os.path.dirname(__file__)+'/dirty-piano.jpg')]
			self.images_frame.add_flickr_artist_images(pixmaps)

	# images handler
	def musikki_images_handler(self, reply):
		urls, pixmaps, widths, heights = [], [], [], []

		er = reply.error()
		
		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()
			notfound_count = 0

			for f in json_resp['results'].toArray():
				f = f.toObject() 
				thumb = f['thumbnails'].toArray()[0].toObject()
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
		else:
			# use default image of dirty-piano.jpg
			print('will search flickr as a backup')
			# pixmaps = [QPixmap(os.path.dirname(__file__)+'/dirty-piano.jpg')]
			# widths = [pixmaps[0].width()]
			# heights = [pixmaps[0].height()]
			# self.images_frame.add_artist_images(pixmaps, widths, heights)
			# self.images_frame.set_display_text('No Images Found.')

	def social_handler(self, reply):
		er = reply.error()

		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()

			service_name = json_resp['service_name'].toString()

			year = json_resp['timeline_posts'].toArray()[0].toObject()['date'].toObject()['year'].toInt()
			month = json_resp['timeline_posts'].toArray()[0].toObject()['date'].toObject()['month'].toInt()
			day = json_resp['timeline_posts'].toArray()[0].toObject()['date'].toObject()['day'].toInt()

			date = str(month) + '/' + str(day) + '/' + str(year)

			content = json_resp['timeline_posts'].toArray()[0].toObject()['content'].toString()

			social_text = date + ' - via ' + service_name + '\n\n' + content

			self.social_frame.set_display_text(social_text, 10, 45, 'social_text')
			self.musikki_artist.twitter_search = False

		elif self.musikki_artist.facebook_search == False:
			self.musikki_artist.get_social_media_facebook(self.social_nam)
		else:
			self.social_frame.set_display_text('No social media found.', 10, 45)
			self.musikki_artist.facebook_search = False

	def next_image_handler(self):
		self.images_frame.next_image()

	def prev_image_handler(self):
		self.images_frame.prev_image()

	# playback handler
	def update_playback_display(self):
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
			print('No lyrics results, so no lyrics popup')

	def build_popup(self, source_frame):
		offset = 50
		self.popup_window = view.SingleFrameWindow(self.screen_width, self.screen_height)		
		self.popup_window.init_popup(
			self.window_x-offset, self.window_y-offset, source_frame.display_title, 'single_frame_window'
		)
		source_frame.create_popup(self.popup_window)
		self.popup_window.add_frame(source_frame)
		self.popup_window.show()		

	# Spotify Controls
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

		while True:
			if self.stored_song != self.spotify.get_current_playing().rstrip():
				self.song_change.emit()
				self.stored_song = self.spotify.get_current_playing().rstrip()
			
			sleep(1)

