import model
import view
import playback
import musikki
import json

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *
from PyQt5 import QtNetwork, QtCore


class Controller():

	def __init__(self):

		self.multi_frame_window = view.MultiFrameWindow(0, 0, 800, 600, "Spotify Info Suite", "multi_frame_window")
		self.bio_frame = model.Frame(self, self.multi_frame_window, 0, 100, 250, 450, "bio_frame")
		self.text = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. " \
					"Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus " \
					"mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa " \
					"quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, r" \
					"honcus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. " \
					"Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend " \
					"tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, " \
					"dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet."
		self.bio_frame.set_display_text(self.text, 5, 25)
		self.bio_frame.set_display_title("Bio", 5, 5)
		self.multi_frame_window.add_frame_bio(self.bio_frame)
		self.multi_frame_window.show()

		# init and open Spotify Desktop App
		self.spotify = self.open_spotify()
		self.init_playback_frame()

		artist = musikki.search(self.get_current_artist())

		self.bio_nam = QtNetwork.QNetworkAccessManager()
		self.bio_nam.finished.connect(self.search_bio_handler)
	
		artist.get_full_bio(self.bio_nam, self.bio_frame.get_display_text_label())

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
			self.bio_frame.set_display_text(bio, 5, 25)

	def init_playback_frame(self):
		self.playback_frame = model.Frame(self, self.multi_frame_window, 0,0, 250,100, 'playback_frame')
		self.playback_frame.set_display_title(self.get_current_playing(), 10, 10)		
		
		self.playback_frame.create_playback_buttons()		
		self.playback_frame.get_playback_prev_button().clicked.connect(self.prev)
		self.playback_frame.get_playback_play_button().clicked.connect(self.play_pause)
		self.playback_frame.get_playback_next_button().clicked.connect(self.next)

		self.multi_frame_window.add_frame(self.playback_frame)


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

