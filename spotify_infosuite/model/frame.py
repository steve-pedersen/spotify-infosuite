
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
		self.display_title_label = QLabel(self)
		self.display_text_label = QLabel(self)
		self.controller = controller
		self.view = view
		self.setGeometry(self.x, self.y, self.w, self.h)
		self.frame_components = []

	def set_display_title(self, title, x, y):
		# self.display_title_label = QLabel(self)
		self.display_title_label.setText(title)
		self.display_title_label.move(x, y)
		self.display_title_label.resize(int(self.w*0.93), 35) # limit width to 93% of frame
		self.display_title_label.setObjectName('frame_title')
		self.display_title_label.setWordWrap(True)
		self.frame_components.append(self.display_title_label)

	def set_display_text(self, text, x, y):
		# self.display_text_label = QLabel(self)
		self.display_text_label.setText(text)
		self.display_text_label.setGeometry(x, y, self.w*0.95, self.h*0.9)
		self.display_text_label.setObjectName('frame_text')
		self.display_text_label.setWordWrap(True)
		self.frame_components.append(self.display_text_label)

	def get_display_text_label(self):
		return self.display_text_label
	def get_display_title_label(self):
		return self.display_title_label

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

		div =  self.w / self.playpause_button.width()
		# print(self.playpause_button.width(), ' ', self.prev_button.width())
		prev_x = 40
		play_x = self.playpause_button.width()
		next_x = play_x + self.playpause_button.width()
		# print('prev_x: ', prev_x, '  play_x: ', play_x, '  next_x: ', next_x)
		self.prev_button.move(prev_x, 65)	
		self.playpause_button.move(play_x, 65)	
		self.next_button.move(next_x, 65)

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