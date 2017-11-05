from PyQt5.QtWidgets import QLabel, QPushButton

class Frame(QLabel):

	# when QLabel is clicked, emit a signal with an object param
	clicked = pyqtSignal(object)

	def __init__(self, x, y, w, h, title, controller, limit=0):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.object_title = title
		self.char_limit = limit
		self.display_title_label = None
		self.display_text_label = None
		self.controller = controller

	def set_display_title(self, view, title, x, y, w, h):
		self.display_title_label = QLabel(view)
		self.display_title_label.setText(title)
		self.display_title_label.move(x, y)
		self.display_title_label.resize(w, h)	

	def set_display_text(self, view, text, x, y, w, h):
		self.display_text_label = QLabel(view)
		self.display_text_label.setText(text)
		self.display_text_label.move(x, y)
		self.display_text_label.resize(w, h)

	def mousePressEvent(self, event)
		self.clicked.emit(self)

	def set_expand_button(self, view)
		self.expand_button = QPushButton('Expand', view)