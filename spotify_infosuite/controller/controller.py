import model
import view
import playback
import musikki
# import reviews #pitchfork
# from reviews.pitchfork import pitchfork
from reviews import reviews
import json
import sys
import threading
import requests
import urllib
import ssl

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

	def __init__(self, app, screen_width, screen_height):
		super().__init__()
		print(screen_width, screen_height)

		space_w = screen_width / 4
		space_h = screen_height / 4
		self.window_w = screen_width - space_w
		self.window_h = screen_height - space_h
		self.window_x = space_w / 2
		self.window_y = space_h / 2

		self.multi_frame_window = view.MultiFrameWindow(
			self.window_x, 
			self.window_y, 
			self.window_w, 
			self.window_h, 
			"Spotify Info Suite", 
			"multi_frame_window"
		)
		self.multi_frame_window.show()

		self.init_playback_frame()
		self.init_bio_frame()
		self.init_review_frame()
		self.init_images_frame()
		self.init_lyrics_frame()


	def init_bio_frame(self):
		x = 0
		y = self.window_h * 0.15
		w = self.window_w / 3
		h = self.window_h * 0.85
		self.bio_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "bio_frame"
		)
		self.bio_frame.set_display_title("Bio", 10, 5)
		self.multi_frame_window.add_frame_bio(self.bio_frame)

		self.bio_nam = QtNetwork.QNetworkAccessManager()
		self.bio_nam.finished.connect(self.search_bio_handler)

		self.musikki_artist = musikki.search(self.get_current_artist())
		if self.musikki_artist.is_found:
			self.musikki_artist.get_full_bio(self.bio_nam)
		else:
			self.bio_frame.set_display_text('No results for current artist.', 10, 45)

	def init_playback_frame(self):
		self.spotify = self.open_spotify()
		self.update_current_playing()

		x = 0
		y = 0
		w = self.window_w / 3
		h = self.window_h * 0.15
		self.playback_frame = model.Frame(self, self.multi_frame_window, x,y, w,h, 'playback_frame')
		self.playback_frame.set_display_title(self.get_current_playing(), 10, 10)		
		
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
		h = self.window_h
		self.lyrics_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "lyrics_frame"
		)

		self.lyrics_frame.set_display_title("Lyrics", 10, 5)
		self.multi_frame_window.add_frame(self.lyrics_frame)
		self.lyrics_nam = QtNetwork.QNetworkAccessManager()
		self.lyrics_nam.finished.connect(self.lyrics_handler)

		# self.set_lyrics()
		self.get_lyrics()

	def init_review_frame(self):
		x = self.window_w * 2 / 3
		y = self.window_h / 2
		w = self.window_w / 3
		h = self.window_h / 2
		title_x = 10
		title_y = 5
		self.review_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, 'review_frame'
		)
		self.review_frame.set_display_title('Reviews', title_x, title_y)
		self.multi_frame_window.add_frame(self.review_frame)

		self.get_pitchfork_review()
		self.get_metacritic_review()

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
		self.multi_frame_window.add_frame(self.images_frame)

		self.images_nam = QtNetwork.QNetworkAccessManager()
		self.images_nam.finished.connect(self.search_images_handler)

		if self.musikki_artist.is_found:
			self.musikki_artist.get_full_images(self.images_nam)
		else:
			self.images_frame.set_display_text('No results for current artist.', 10, 45)

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
		self.playback_frame.set_display_title(self.current_playing, 10, 10)

		self.update_artist_info(False)		
		self.update_album_info(False)
		self.update_song_info(False)

	def update_artist_info(self, update_playback=True):
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)		
		
		# new bio needed
		self.musikki_artist = musikki.search(self.get_current_artist())
		self.musikki_artist.get_full_bio(self.bio_nam)
		self.musikki_artist.get_full_images(self.images_nam)

	def update_song_info(self, update_playback=True):
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)	

		# self.set_lyrics()	
		self.get_lyrics()	

	def update_album_info(self, update_playback=True):
		if update_playback:
			self.update_current_playing()
			self.playback_frame.set_display_title(self.current_playing, 10, 10)	
		
		# new reviews needed
		self.get_pitchfork_review()
		self.get_metacritic_review()

	def update_current_playing(self):
		self.current_playing = self.get_current_playing()
		self.current_artist = self.get_current_artist()
		self.current_song = self.get_current_song()
		self.current_album = self.get_current_album()	
		print('\n-----Now Playing-----')
		print('Artist:\t', self.current_artist)
		print('Song:\t', self.current_song)
		print('Album:\t', self.current_album)

	def get_lyrics(self, url=''):
		artist, song = self.current_artist, self.current_song
		if url == '':
			url = "http://genius.com/%s-%s-lyrics" % (artist.replace(' ', '-'), song.replace(' ', '-'))
		req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
		self.lyrics_nam.get(req)
	
	# lyrics handler
	def lyrics_handler(self, reply):

		er = reply.error()

		# for h in reply.rawHeaderList():
		# 	header_key = ''
		# 	for l in h:
		# 		header_key += l
		# 	print(header_key, ': ', reply.rawHeader(QByteArray(h)))

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
				# test print statements... shouldn't get here
				print('got here somehow')
				print('status: ', reply.rawHeader(QByteArray(b'Status')))
				qbyteurl = reply.rawHeader(QByteArray(b'Location'))
				print(qbyteurl)
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
				# print(url)
				soup = BeautifulSoup(lyricspage.text, 'html.parser')
				lyrics = soup.text.split('Lyrics')[3].split('More on Genius')[0]
				if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
					lyrics = error
			except Exception:
				lyrics = error
		else:
			lyrics = error
		
		# set those lyrics on the frame
		self.lyrics_frame.set_display_text(lyrics, 10, 45, 'lyrics_text')

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

			self.bio_frame.set_display_text(bio, 10, 45, 'bio_text')
			
		else:
			self.bio_frame.set_display_text('No artist bio found.', 10, 45)

	# images handler
	def search_images_handler(self, reply):
		urls, pixmaps, widths, heights = [], [], [], []

		er = reply.error()
		
		if er == QtNetwork.QNetworkReply.NoError:
			response = reply.readAll()
			document = QJsonDocument()
			error = QJsonParseError()
			document = document.fromJson(response, error)
			json_resp = document.object()
			
			for f in json_resp['results'].toArray():				
				f = f.toObject() 
				thumb = f['thumbnails'].toArray()[0].toObject()
				thumb_url = thumb['url'].toString()
				thumb_width = thumb['width'].toInt()
				thumb_height = thumb['height'].toInt()
				context = ssl._create_unverified_context()
				data = urlopen(thumb_url, context=context).read()
				pixmap = QPixmap()
				pixmap.loadFromData(data)

				urls.append(thumb_url)
				pixmaps.append(pixmap)
				widths.append(thumb_width)
				heights.append(thumb_height)

		if len(pixmaps) > 0:
			self.images_frame.add_artist_images(pixmaps, widths, heights)
		else:
			self.images_frame.set_display_text('No Images Found.')

	# playback handler
	def update_playback_display(self):
		if self.current_playing != self.get_current_playing():
			if (self.current_artist == self.get_current_artist() and
				self.current_song != self.get_current_song()):
				if self.current_album != self.get_current_album():
					print('Album change...')
					self.update_everything()
				else:
					print('Song change...')
					self.update_song_info()
			else:
				print('Artist and song change...')
				self.update_everything()
		elif (self.current_artist == self.get_current_artist() and
			self.current_album != self.get_current_album()):
			print('need album update')
			self.update_everything()

	# reviews handler
	# from metacritic:
	# artist,album,date,critic_rating,critic_count,user_rating,user_count,img_url
	def update_review_frame(self, review):
		if isinstance(review, str):
			self.review_frame.set_display_text(review)
		elif isinstance(review, object):
			print('\n-----Metacritic Results-----\n')
			print(review.artist, ' - ', review.album)
			print('Critic Score:\t', review.critic_rating, '\t(',review.critic_count,' reviews)')
			print('User Score:\t', review.user_rating, '\t(',review.user_count,' reviews)')
			print('-------------------------------------------')

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

