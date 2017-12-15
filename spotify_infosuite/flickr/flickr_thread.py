"""
Fall 2017 CSc 690
File: flickr_thread.py
Author: Steve Pedersen & Andrew Lesondak
System: OS X
Date: 12/13/2017
Usage: python3 spotify_infosuite.py
Dependencies: flickr, threading, pyqt5
Description: Requester class.  A thread used to search the Flickr API asynchronously.

"""

from flickr import flickr
import threading
import json
from threading import Thread
from PyQt5.QtCore import *


class Requester(QThread):

	flickr_reciever = pyqtSignal(list)

	def __init__(self):
		super().__init__()

	def get_images(self, artist):

		def __get_data(arg1):
			artist = arg1

			print('Searching Flickr for artist: ', artist)
			f = flickr.search(artist)

			self.flickr_reciever.emit(f)

		worker = threading.Thread(target=__get_data, args=[artist])
		worker.setDaemon(True)
		worker.start()