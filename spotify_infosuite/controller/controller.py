import model
import view
import playback
import musikki
import json
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *
from PyQt5 import QtNetwork, QtCore
from PyQt5.QtGui import *
from PyQt5 import QtGui


class Controller():

	def __init__(self, screen_width, screen_height):
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
		self.spotify = self.open_spotify()
		self.init_playback_frame()


		artist = musikki.search(self.get_current_artist())

		self.bio_nam = QtNetwork.QNetworkAccessManager()
		self.bio_nam.finished.connect(self.search_bio_handler)
	
		artist.get_full_bio(self.bio_nam, self.bio_frame.get_display_text_label())


	def init_bio_frame(self):
		x = 0
		y = self.window_h * 0.15
		w = self.window_w / 4
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
		w = self.window_w / 4
		h = self.window_h * 0.15
		self.playback_frame = model.Frame(self, self.multi_frame_window, x,y, w,h, 'playback_frame')
		self.playback_frame.set_display_title(self.get_current_playing(), 10, 10)		
		
		self.playback_frame.create_playback_buttons()		
		self.playback_frame.get_playback_prev_button().clicked.connect(self.prev)
		self.playback_frame.get_playback_play_button().clicked.connect(self.play_pause)
		self.playback_frame.get_playback_next_button().clicked.connect(self.next)

		self.multi_frame_window.add_frame(self.playback_frame)


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
				for t in f['text'].toArray():
					t = t.toString()
					paragraph += t.rstrip()
				bio += paragraph + '\n\n'
			
			# print(bio)
			self.bio_frame.set_display_text(bio, 10, 45)


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

	def get_current_playing(self):
		return self.get_current_artist() + ' - ' + self.get_current_song()
