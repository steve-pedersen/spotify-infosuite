from model.frame import Frame
# from playback.playback import Playback
from view.view_multi import ViewMulti
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *
import sys
import subprocess

class Controller():

	def __init__(self):

		self.view_multi = ViewMulti(0, 0, 800, 600, "Spotify Info Suite", "view_multi")

		self.bio_frame = Frame(self, self.view_multi, 0, 100, 250, 400, "bio_frame")
		self.bio_frame.set_display_text("mogwai was born in blah blah blah", 10, 10)
		self.bio_frame.set_display_title("Bio", 5, 5)
		self.view_multi.add_frame_bio(self.bio_frame)
		self.view_multi.show()

		# init and open Spotify Desktop App
		# self.spotify = self.open_spotify()
		print('Currently listening to: ', self.get_current_playing())



	# Spotify Controls
	def open_spotify(self):
		spotify = Playback()
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

	# def get_current_playing(self):
	# 	return self.get_current_artist() + ' - ' + self.get_current_song()

	def get_current_playing(self):
		instruction = ('on getCurrentTrack()\n'
			' tell application "Spotify"\n'
			'  set currentArtist to artist of current track as string\n'
			'  set currentTitle to name of current track as string\n'
			'  return currentArtist & " - " & currentTitle\n'
			' end tell\n'
			'end getCurrentTrack\n'
			'getCurrentTrack()')
		proc = subprocess.Popen(
			['osascript', '-e', instruction],
			stdout=subprocess.PIPE)
		out, err = proc.communicate()
		return out.decode(sys.getfilesystemencoding())