import model
import view
import playback
import musikki
import json
import sys
import threading
import requests
import urllib

from threading import Thread
from time import sleep

from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
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

		self.init_bio_frame()
		self.init_lyrics_frame()
		self.spotify = self.open_spotify()
		self.current_playing = self.get_current_playing()
		self.current_artist = self.get_current_artist()
		self.current_song = self.get_current_song()
		self.init_playback_frame()

		self.bio_nam = QtNetwork.QNetworkAccessManager()
		self.bio_nam.finished.connect(self.search_bio_handler)

		artist = musikki.search(self.get_current_artist())

		if artist.is_found:
			artist.get_full_bio(self.bio_nam, self.bio_frame.get_display_text_label())
		else:
			self.bio_frame.set_display_text('No results for current artist.', 10, 45)

		self.set_lyrics()

		# spawn a playback listener to keep InfoSuite in sync with Spotify
		self.listener = Listener(self.current_playing, self.spotify)
		self.listener.song_change.connect(self.update_playback_display)
		self.listener.run()		
		# try:
		# 	self.listener = Listener(self.current_playing, self.spotify)
		# 	self.listener.song_change.connect(self.update_playback_display)
		# 	self.listener.run()
		# except (KeyboardInterrupt, SystemExit):
		# 	cleanup_stop_thread()
		# 	sys.exit()	


	def playback_change(self):
		self.update_playback_display()

	def init_lyrics_frame(self):
		x = self.window_w / 3
		y = 0
		w = self.window_w / 3
		h = self.window_h
		self.lyrics_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "lyrics_frame"
		)

		self.lyrics_frame.set_display_title("Lyrics", 10, 5)
		self.multi_frame_window.add_frame_lyrics(self.lyrics_frame)

	def init_bio_frame(self):
		x = 0
		y = self.window_h * 0.15
		w = self.window_w / 3
		h = self.window_h * 0.85
		self.bio_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, "bio_frame"
		)

		# self.bio_frame.set_display_text(self.text, 5, 25)
		self.bio_frame.set_display_title("Bio", 10, 5)
		self.multi_frame_window.add_frame_bio(self.bio_frame)

	def init_playback_frame(self):
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

	def update_everything(self):
		# playback info
		self.current_playing = self.get_current_playing()
		self.playback_frame.set_display_title(self.current_playing, 10, 10)

		self.update_artist_info()
		self.update_song_info()

	def update_artist_info(self):
		self.current_playing = self.get_current_playing()
		self.playback_frame.set_display_title(self.current_playing, 10, 10)		
		# bio
		artist = musikki.search(self.get_current_artist())
		artist.get_full_bio(self.bio_nam, self.bio_frame.get_display_text_label())

	def update_song_info(self):
		self.current_playing = self.get_current_playing()
		self.playback_frame.set_display_title(self.current_playing, 10, 10)

	def set_lyrics(self):
		error = "Error: Could not find lyrics."
		proxy = urllib.request.getproxies()

		print("current playing: ", self.current_playing)
		artist = self.get_current_artist()
		song = self.get_current_song()

		url = ""
		try:
			url = "http://genius.com/%s-%s-lyrics" % (artist.replace(' ', '-'), song.replace(' ', '-'))
			lyricspage = requests.get(url, proxies=proxy)
			print(url)
			soup = BeautifulSoup(lyricspage.text, 'html.parser')
			lyrics = soup.text.split('Lyrics')[3].split('More on Genius')[0]
			if artist.lower().replace(" ", "") not in soup.text.lower().replace(" ", ""):
				lyrics = error
		except Exception:
			lyrics = error
		self.lyrics_frame.set_display_text(lyrics, 10, 45)

	# Handlers
	def search_bio_handler(self, reply):
		print('in search_handler')
		er = reply.error()
		print("REPLY: ", reply)
		print("REPLY: ", type(reply))

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
					paragraph += t.rstrip() if i == 0 else (' ' + t.rstrip())
				bio += paragraph + '\n\n'

			# print(bio)
			self.bio_frame.set_display_text(bio, 10, 45)
		else:
			self.bio_frame.set_display_text('No artist bio found.', 10, 45)

	def update_playback_display(self):
		if self.current_playing != self.get_current_playing():
			if (self.current_artist == self.get_current_artist() and
				self.current_song != self.get_current_song()):
				print('Song change...')
				self.update_song_info()
			else:
				print('Artist and song change...')
				self.update_everything()	

	# Spotify Controls
	def open_spotify(self):
		spotify = playback.Playback()
		return spotify

	def play_pause(self):
		self.spotify.play_pause()
		self.update_playback_display()
		self.set_lyrics()

	def next(self):
		self.spotify.next()
		self.update_playback_display()
		self.set_lyrics()

	def prev(self):
		self.spotify.prev()
		self.update_playback_display()
		self.set_lyrics()

	def pause(self):
		self.spotify.pause()

	def get_current_artist(self):
		return self.spotify.get_current_artist().rstrip()

	def get_current_song(self):
		return self.spotify.get_current_song().rstrip()

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
		print('listener: started')
		while True:
			if self.stored_song != self.spotify.get_current_playing().rstrip():
				self.song_change.emit()
			sleep(1)

