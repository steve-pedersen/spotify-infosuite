
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
		self.char_limit = limit
		self.display_title_label = None
		self.display_text_label = None
		self.controller = controller
		self.setGeometry(self.x, self.y, self.w, self.h)

	def set_display_title(self, title, x, y):
		self.display_title_label = QLabel(self)
		self.display_title_label.setText(title)
		self.display_title_label.move(x, y)
		# self.display_title_label.resize(w, h)

	def set_display_text(self, text, x, y):
		self.display_text_label = QLabel(self)
		self.display_text_label.setText(text)
		self.display_text_label.move(x, y)
		# self.display_text_label.resize(w, h)

	def mousePressEvent(self, event):
		self.clicked.emit(self)

	def set_expand_button(self, view):
		self.expand_button = QPushButton('Expand', view)