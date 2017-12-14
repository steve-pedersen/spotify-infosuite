"""
Fall 2017 CSc 690
File: playback.py
Author: Steve Pedersen & Andrew Lesondak
System: OS X
Date: 12/13/2017
Usage: python3 spotify_infosuite.py
Dependencies: Python3, PyQt5, beautifulsoup4, lxml, unidecode
Description: Playback class.  Used to control the Spotify application's play, pause, previous, and next controls.

"""

from __future__ import absolute_import, unicode_literals
import sys
import subprocess
from time import sleep


class Playback():
	"""Playback is a single frame of the application, providing users the name of the artist and song.
	It also has buttons for Play/Pause, Next track, and Previous track.

	"""
	def __init__(self):
		"""
			Check if there is a Spotify process running and if not,
			run Spotify.
		"""
		try:
			count = int(subprocess.check_output([
					'osascript',
					'-e', 'tell application "System Events"',
					'-e', 'count (every process whose name is "Spotify")',
					'-e', 'end tell'
				]).strip())
			if count == 0:
				print('\n[OPENING SPOTIFY] The Spotify app was not open.\n')

				self._make_osascript_call(
					'tell application "Spotify" to activate'
				)
				# Wait for Spotify to open before letting app continue
				sleep(3)
		except Exception:
			sys.exit('You don\'t have Spotify installed. Please install it.')

	def _make_osascript_call(self, command):
		"""Used to interact with the Spotify Application

		Args:
			command (string) - Apple script

		"""
		subprocess.call([
			'osascript',
			'-e',
			command
		])

	def listen(self, index):
		"""Used to check for song changes in the Spotify application

		Args:
			index (int) - location of song URI

		"""
		uri = self._get_song_uri_at_index(index)
		self._make_osascript_call(
			'tell app "Spotify" to play track "%s"' % uri
		)

	def next(self):
		self._make_osascript_call('tell app "Spotify" to next track')

	def prev(self):
		self._make_osascript_call('tell app "Spotify" to previous track')

	def play_pause(self):
		self._make_osascript_call('tell app "Spotify" to playpause')

	def pause(self):
		self._make_osascript_call('tell app "Spotify" to pause')

	def get_track_uri(self):
		print()
		# set info to info & "\n URI:      " & spotify url of current track

	def get_current_artist(self):
		"""Used to get currently playing artist

		"""
		instruction = ('on getCurrentTrack()\n'
			' tell application "Spotify"\n'
			'  set currentArtist to artist of current track as string\n'
			'  return currentArtist\n'
			' end tell\n'
			'end getCurrentTrack\n'
			'getCurrentTrack()')
		proc = subprocess.Popen(
			['osascript', '-e', instruction],
			stdout=subprocess.PIPE)
		out, err = proc.communicate()
		return out.decode(sys.getfilesystemencoding()).rstrip()

	def get_current_song(self):
		"""Used to get currently playing song

		"""
		instruction = ('on getCurrentTrack()\n'
			' tell application "Spotify"\n'
			'  set currentTitle to name of current track as string\n'
			'  return currentTitle\n'
			' end tell\n'
			'end getCurrentTrack\n'
			'getCurrentTrack()')
		proc = subprocess.Popen(
			['osascript', '-e', instruction],
			stdout=subprocess.PIPE)
		out, err = proc.communicate()
		return out.decode(sys.getfilesystemencoding()).rstrip()

	def get_current_album(self):
		"""Used to get currently playing album

		"""
		instruction = ('on getCurrentTrack()\n'
			' tell application "Spotify"\n'
			'  set currentAlbum to album of current track as string\n'
			'  return currentAlbum\n'
			' end tell\n'
			'end getCurrentTrack\n'
			'getCurrentTrack()')
		proc = subprocess.Popen(
			['osascript', '-e', instruction],
			stdout=subprocess.PIPE)
		out, err = proc.communicate()
		return out.decode(sys.getfilesystemencoding()).rstrip()		

	def get_current_playing(self):
		"""Used to get currently playing song

		"""
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
