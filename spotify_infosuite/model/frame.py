
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import *

class Frame(QLabel):

	# when QLabel is clicked, emit a signal with an object param
	clicked = pyqtSignal(object)

	def __init__(self, controller, view, x, y, w, h, title, limit=0):
		super().__init__(view)
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.object_title = title
		self.setObjectName((self.object_title))
		self.char_limit = limit
		self.display_title_label = None
		self.display_text_label = None
		self.controller = controller
		self.view = view
		self.setGeometry(self.x, self.y, self.w, self.h)
		self.frame_components = []

	def set_display_title(self, title, x, y):
		self.display_title_label = QLabel(self)
		self.display_title_label.setText(title)
		self.display_title_label.move(x, y)
		self.display_title_label.resize(int(self.w*0.93), 35) # limit width to 93% of frame
		self.display_title_label.setObjectName('frame_title')
		self.display_title_label.setWordWrap(True)
		self.frame_components.append(self.display_title_label)

	def set_display_text(self, text, x, y):
		self.display_text_label = QLabel(self)
		self.display_text_label.setText(text)
		self.display_text_label.setGeometry(x, y, 240, 395)
		self.display_text_label.setObjectName('frame_text')
		self.display_text_label.setWordWrap(True)
		self.frame_components.append(self.display_text_label)

	def set_expand_button(self):
		self.expand_button = QPushButton('Expand', self.view)
		self.frame_components.append(self.expand_button)

	def create_playback_buttons(self):
		self.playpause_button = QPushButton('Play/Pause', self.view)
		self.prev_button = QPushButton('Prev', self.view)
		self.next_button = QPushButton('Next', self.view)
		self.frame_components.extend([
			self.playpause_button, self.prev_button, self.next_button
		])
				
		self.playpause_button.setObjectName('playpause_button')
		self.prev_button.setObjectName('prev_button')		
		self.next_button.setObjectName('next_button')			
		self.prev_button.move(0, 65)	
		self.playpause_button.move(70, 65)	
		self.next_button.move(180, 65)

	def get_playback_prev_button(self):
		return self.prev_button

	def get_playback_play_button(self):
		return self.playpause_button

	def get_playback_next_button(self):
		return self.next_button

	def get_frame_components(self):
		return self.frame_components

	def mousePressEvent(self, event):
		self.clicked.emit(self)