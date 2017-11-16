
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt5.QtCore import *
from PyQt5 import QtGui

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
		self.display_images_label = QLabel(self)
		self.layout = QVBoxLayout(self)
		self.controller = controller
		self.view = view
		self.setGeometry(self.x, self.y, self.w, self.h)
		self.frame_components = []

	def set_display_title(self, title, x, y):
		# self.display_title_label = QLabel(self)
		self.display_title_label.setText(title)
		self.display_title_label.move(x, y)
		self.display_title_label.resize(int(self.w*0.96), 35) # limit width to 93% of frame
		self.display_title_label.setObjectName('frame_title')
		self.display_title_label.setWordWrap(True)
		self.frame_components.append(self.display_title_label)

	def set_display_text(self, text, x=5, y=45):
		# self.display_text_label = QLabel(self)
		if self.display_text_label.text() == '':
			self.display_text_label.setText(text)
			self.display_text_label.setGeometry(x, y, self.w*0.96, self.h*0.93)
			self.display_text_label.setObjectName('frame_text')
			self.display_text_label.setWordWrap(True)
			self.display_text_label.setStyleSheet('')
			self.frame_components.append(self.display_text_label)
			scroll = QScrollArea()
			scroll.setWidget(self.display_text_label)
			scroll.setWidgetResizable(True)
			scroll.setFixedHeight(self.h*0.93 - y)		
			self.layout.addWidget(scroll)
		else:
			self.display_text_label.setText(text)

	def set_display_images(self, x=5, y=45):
		self.display_images_label.setGeometry(x, y, self.w*0.96, self.h*0.93)
		self.display_images_label.setObjectName('frame_images')
		self.display_images_label.setStyleSheet('')
		self.frame_components.append(self.display_images_label)

		self.display_images_label.setText('test')

	# TODO: maybe pass in a dict that has the pixmap, width and height of each
	# 	rather than separate lists
	def add_artist_images(self, images, widths, heights):
		x, y = self.w / 8, self.h / 8
		# w, h = self.w / 4, self.h / 3

		for i, image in enumerate(images):
			w, h = widths[i], heights[i]
			# image = image.scaledToWidth(w)
			
			self.container = QLabel(self)
			# self.container.setStyleSheet('border: 1px solid #0f0f0f;')
			self.container.resize(w, h)			
			self.container.setPixmap(image)
			self.container.move(x + x*i, y)
			self.container.show()


	def get_display_text_label(self):
		return self.display_text_label
	def get_display_title_label(self):
		return self.display_title_label

	def get_display_image_labels(self):
		return self.display_images_label

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