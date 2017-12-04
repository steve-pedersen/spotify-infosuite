from flickr import flickr
import threading
import json
from threading import Thread
from PyQt5.QtCore import *


class Requester(QThread):

	# print('in reviews.py Requester class')
	flickr_reciever = pyqtSignal(list)

	def __init__(self):
		super().__init__()

	def get_images(self, artist):

		def __get_data(arg1):
			artist = arg1

			with open('./flickr/credentials.json') as creds:
				credentials = json.load(creds)

			appkey = credentials['flickr']['appkey']

			print('Searching Flickr for artist: ', artist)
			f = flickr.search(artist, appkey)

			# if m.has_review:
			self.flickr_reciever.emit(f)

		worker = threading.Thread(target=__get_data, args=[artist])
		worker.setDaemon(True)
		worker.start()