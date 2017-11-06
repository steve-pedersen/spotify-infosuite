import model
import view
import playback
import musikki

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *


class Controller():

	def __init__(self):

		self.multi_frame_window = view.MultiFrameWindow(0, 0, 800, 600, "Spotify Info Suite", "multi_frame_window")

		self.bio_frame = model.Frame(self, self.multi_frame_window, 0, 100, 250, 400, "bio_frame")
		self.bio_frame.set_display_text("mogwai was born in blah blah blah", 10, 10)
		self.bio_frame.set_display_title("Bio", 5, 5)
		self.multi_frame_window.add_frame_bio(self.bio_frame)
		self.multi_frame_window.show()

		# init and open Spotify Desktop App
		self.spotify = self.open_spotify()

		self.init_playback_frame()

		# artist = musikki.search(self.get_current_artist())
		# full_bio = artist.get_full_bio()


	def init_playback_frame(self):
		self.playback_frame = model.Frame(self, self.multi_frame_window, 0,0, 400,250, 'playback_frame')
		self.playback_frame.set_display_title(self.get_current_playing(), 10, 10)
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

