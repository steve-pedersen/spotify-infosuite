import model
import view
import playback
import musikki
import pitchfork
import json
import sys
import threading

from threading import Thread
from time import sleep

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

		self.init_bio_frame()
		self.init_playback_frame()
		self.init_review_frame()

		self.bio_nam = QtNetwork.QNetworkAccessManager()
		self.bio_nam.finished.connect(self.search_bio_handler)

		artist = musikki.search(self.get_current_artist())

		if artist.is_found:
			artist.get_full_bio(self.bio_nam, self.bio_frame.get_display_text_label())
		else:
			self.bio_frame.set_display_text('No results for current artist.', 10, 45)

	def init_review_frame(self):
		x = self.window_w * 2 / 3
		y = self.window_h / 2
		w = self.window_w / 3
		h = self.window_h / 2
		title_x = 5
		title_y = 5
		self.review_frame = model.Frame(
			self, self.multi_frame_window, x,y, w,h, 'review_frame'
		)
		self.review_frame.set_display_title('Reviews', title_x, title_y)
		self.multi_frame_window.add_frame(self.review_frame)

		self.get_pitchfork_review()	

	def get_pitchfork_review(self):

		def __get_data():
			album = self.current_album.replace('(Deluxe Version)','').rstrip() \
				.replace('[Remastered]','') \
				.replace('(Deluxe Edition)','') \
				.replace('(Remastered Deluxe Edition)','')
			
			print('Searching Pitchfork for album: ', album)
			p = pitchfork.search(self.current_artist, album)

			# self.review_frame.set_display_text(
			# 	'Pitchfork - Rating: '+str(p.score())+' - '+p.album()
			# 	+' ('+str(p.year())+')'+'\n\n'+p.editorial()[:800]
			# )
			
		my_thread = threading.Thread(target=__get_data)
		my_thread.start()		

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
		self.listener = Listener(self.current_playing, self.current_album, self.spotify)
		self.listener.song_change.connect(self.update_playback_display)
		self.listener.run()	

	def update_everything(self):
		# playback info
		self.update_current_playing()
		self.playback_frame.set_display_title(self.current_playing, 10, 10)

		self.update_artist_info()
		self.update_song_info()
		self.update_album_info()

	def update_artist_info(self):
		self.update_current_playing()
		self.playback_frame.set_display_title(self.current_playing, 10, 10)		
		# bio
		artist = musikki.search(self.get_current_artist())
		artist.get_full_bio(self.bio_nam, self.bio_frame.get_display_text_label())

	def update_song_info(self):
		self.update_current_playing()
		self.playback_frame.set_display_title(self.current_playing, 10, 10)

	def update_album_info(self):
		self.get_pitchfork_review()

	def update_current_playing(self):
		self.current_playing = self.get_current_playing()
		self.current_artist = self.get_current_artist()
		self.current_song = self.get_current_song()
		self.current_album = self.get_current_album()		
		print('\n-----Now Playing-----')
		print('Artist:\t', self.current_artist)
		print('Song:\t', self.current_song)
		print('Album:\t', self.current_album)

	# Handlers
	def search_bio_handler(self, reply):
		print('in search_handler')
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

	# Spotify Controls
	def open_spotify(self):
		spotify = playback.Playback()
		return spotify

	def play_pause(self):
		self.spotify.play_pause()
		self.update_playback_display()		

	def next(self):
		self.spotify.next()
		self.update_playback_display()

	def prev(self):
		self.spotify.prev()
		self.update_playback_display()	

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
		# print('listener: started')
		while True:
			if self.stored_song != self.spotify.get_current_playing().rstrip():
				self.song_change.emit()
			sleep(1)

