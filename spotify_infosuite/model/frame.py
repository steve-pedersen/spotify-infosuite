
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore


class Frame(QLabel):
	"""Frame is the main component of a window and serves as a container 
	for all of the Frame components (display_title, display_text, etc.).
	
	Args:
		controller (object) -- the application controller
		view (object) -- the window this Frame is connected to
		x (int) -- position of Frame
		y (int) -- position of Frame
		w (int) -- width of Frame
		h (int) -- height of Frame
		title (str) -- the object title used as an id for stylesheet

	"""
	def __init__(self, controller, view, x, y, w, h, title):
		super().__init__(view)
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.object_title = title
		self.setObjectName(self.object_title)
		self.setGeometry(self.x, self.y, self.w, self.h)

		self.display_title_label = QLabel(self)
		self.display_text_label = QLabel(self)
		self.display_images_label = QLabel(self)
		self.layout = QVBoxLayout(self)
		self.controller = controller
		self.view = view
				
		self.frame_components = []
		self.images_list = []
		self.image_label = QLabel(self)

		self.results_found = False		
		self.metacritic_exists = False
		self.mc_album_thumb = QLabel(self)
		self.mc_title = QLabel(self)
		self.mc_critic = QLabel(self)
		self.mc_user = QLabel(self)

		self.news_img = QLabel(self)
		self.news_title = QLabel(self)
		self.news_summary = QLabel(self)


	def set_display_title(self, title, x, y):
		"""This is the default frame title
		
		Args:
			title (str) -- text used in this QLabel
			x (int) -- position
			y (int) -- position

		"""
		self.display_title = title
		self.display_title_label.setText(title)
		self.display_title_label.move(x, y)
		self.display_title_label.resize(int(self.w*0.96), 35)
		self.display_title_label.setWordWrap(True)
		if self.object_title == 'playback_frame':
			self.display_title_label.setObjectName('playback_title')
		else:
			self.display_title_label.setObjectName('frame_title')
		
		self.frame_components.append(self.display_title_label)


	def set_display_text(self, text, x=5, y=45,obj=''):
		"""This is the default, scrollable text area component
		
		Args:
			text (str) -- text used in this QLabel
			x (int) -- position
			y (int) -- position
			obj (str) -- for setObjectName for stylesheet

		"""
		self.display_text = text
		min_y = self.display_title_label.height() + 8
		scroll_height = self.h - (y+min_y)
		
		if self.display_text_label.text() == '':
			name = 'frame_text' if obj == '' else obj
			self.display_text_label.setObjectName(name)
			self.display_text_label.setText(text)
			self.display_text_label.setGeometry(x, y, self.w, self.h)
			self.display_text_label.setWordWrap(True)
			self.display_text_label.setStyleSheet('')
			self.display_text_label.setAlignment(Qt.AlignTop)
			self.frame_components.append(self.display_text_label)
			
			scroll = QScrollArea()
			scroll.setWidget(self.display_text_label)
			scroll.setWidgetResizable(True)			
			scroll.setFixedHeight(scroll_height)				
			self.layout.addWidget(scroll)			
		else:
			self.display_text_label.setText(text)
			self.display_text_label.setAlignment(Qt.AlignTop)


	def create_popup(self, popup_window):
		"""Creates new text QLabel full of text from this frame's 
		display_text and attach it to the popup_window.
		
		Args:
			popup_window (object) -- SingleFrameWindow (QWidget)

		"""
		self.popup_title = QLabel(self.display_title, popup_window)
		self.popup_title.resize(200, 22)
		self.popup_text = QLabel(self.display_text, popup_window)
		self.popup_components = []
		self.popup_components.extend([self.popup_title, self.popup_text])
		for p in self.popup_components:
			p.setWordWrap(True)
			p.setObjectName('popup_text')


	def add_news(self, results, def_img=None):
		"""Formats the content for the News frame
		
		Args:
			results (dict) -- news data
			def_image (QPixmap)

		"""
		height = self.display_title_label.height() * 1.3
		self.news_img.setGeometry(10,height, self.w/3, self.h/3)

		img = results['newsicon'] if def_img == None else def_img
		if img.width() > img.height():
			img = img.scaledToWidth(self.news_img.width())
		else:
			img = img.scaledToHeight(self.news_img.height())
		self.news_img.setPixmap(img)
		self.news_img.show()

		if not results['found']:
			# no news, use defaults
			self.news_title.setText(results['message'])
			self.news_title.move(self.w/3 + 20, height)
			self.news_title.resize(
				self.news_title.sizeHint().width(), self.news_title.sizeHint().height())
			self.news_title.setObjectName('news_title')
			self.news_title.setStyleSheet('')
			self.news_summary.setText('')
		else:
			# news found, use results data
			src = results['src_title']
			date = results['date']
			title = results['title']
			self.news_title.setText(
				date +'  -  '+ src +'\n'+ title
			)
			self.news_title.move(self.w/3 + 20, height)
			self.news_title.setWordWrap(1)
			self.news_title.resize(self.w*2/3 - 25,
				self.news_img.height())
			self.news_title.setObjectName('news_title')
			self.news_title.setStyleSheet('')
			self.news_title.show()

			self.news_summary.setText(results['summary'])
			self.news_summary.move(10, self.news_img.height()+45)
			self.news_summary.setWordWrap(1)
			self.news_summary.resize(self.w-20, self.news_summary.sizeHint().height())
			self.news_summary.setObjectName('news_summary')
			self.news_summary.setStyleSheet('')
			self.news_summary.show()


	def add_musikki_artist_images(self, images, widths, heights):
		"""Attach a list of pixmaps to image labels.
		
		Args:
			images (list) -- QPixmaps
			widths (list) -- integers
			heights (list) -- integers

		"""
		x, y = 10, 45
		w, h = self.w - x*2, self.h - y - 40
		self.current_image = 0

		for i in range(len(images)):
			if widths[i] > heights[i]:
				if w > widths[i]:
					# image is wider than it is tall and less wide than the frame
					w = widths[i]
				image = images[i].scaledToWidth(w)
				self.images_list.append(image)
			else:
				if h > heights[i]:
					# image is taller than it is wide and less tall than the frame
					h = heights[i]
				image = images[i].scaledToHeight(h)
				self.images_list.append(image)

		self.image_label.resize(w, h)
		self.image_label.setPixmap(self.images_list[self.current_image])
		self.image_label.move(x, y)
		self.image_label.setAlignment(Qt.AlignCenter)
		self.musikki_images_added = True


	def add_flickr_artist_images(self, images):
		"""Attach a list of pixmaps to image labels.
		
		Args:
			images (list) -- QPixmaps

		"""
		x, y = 10, 45
		w, h = self.w - x*2, self.h - y - 40
		self.current_image = 0

		for i in range(len(images)):
			image = images[i]
			self.images_list.append(image)

		self.image_label.resize(w, h)
		self.image_label.setPixmap(self.images_list[self.current_image])
		self.image_label.move(x, y)
		self.image_label.setAlignment(Qt.AlignCenter)
		self.image_label.show()
		self.flickr_images_added = True


	def create_expando_button(self):
		"""Places an Expand button at the bottom center of the frame.
		
		Ideal for frames with the default display_text scrollable area, 
		since there is room for the button.

		Returns:
			Object QPushButton. The Expand button itself.

		"""
		self.expando_btn = QPushButton('Expand', self)
		self.expando_btn.setObjectName('expando_btn')
		self.expando_btn.setGeometry(
			self.w/2 - self.expando_btn.width()/2,	# x
			self.h - self.expando_btn.height()-6,	# y
			self.expando_btn.sizeHint().width(),	# w
			self.expando_btn.sizeHint().height()	# h
		)
		self.expando_btn.setStyleSheet('')
		self.frame_components.append(self.expando_btn)
		return self.expando_btn


	def add_metacritic_content(self, review):
		"""Format Metacritic frame content from review data
		
		Args:
			review (object) -- metacritic.Review object

		"""
		if type(review.pixmap) == QPixmap:
			pixmap = review.pixmap
		else:
			pixmap = QPixmap()
			pixmap.loadFromData(review.pixmap)

		padding = 20
		if pixmap.height() > pixmap.width():
			pixmap = pixmap.scaledToHeight(self.h - padding-24)
		else:
			pixmap = pixmap.scaledToWidth(self.w/4 - padding-24)

		if not self.metacritic_exists:	
			# create the layout
			x = padding/10
			y = 0
			w = self.w / 4
			h = self.h
					
			self.mc_album_thumb.setGeometry(x,y, w,h)
			self.mc_album_thumb.setPixmap(pixmap)
			self.mc_album_thumb.setAlignment(Qt.AlignCenter)

			self.mc_title.setText(review.album)
			self.mc_title.setObjectName('mc_title')
			self.mc_title.setGeometry(self.w/3.8, self.h/10, self.w*0.75,20)
			self.mc_title.setWordWrap(True)
			self.mc_title.setStyleSheet('')

			self.mc_critic.setText(
				'Critic Score:   '+ str(review.critic_rating)[0]+'.'+str(review.critic_rating)[1]+
				'  ('+str(review.critic_count)+' reviews)'			
			)
			self.mc_critic.setObjectName('mc_critic')
			self.mc_critic.setGeometry(self.w/3.8, self.h/2.5, self.w*0.75,20)
			self.mc_critic.setWordWrap(True)
			self.mc_critic.setStyleSheet('')

			self.mc_user.setText(
				'User Score:    '+ str(review.user_rating)+ '  ('+str(review.user_count)+' reviews)'
			)		
			self.mc_user.setObjectName('mc_user')
			self.mc_user.setGeometry(self.w/3.8, self.h/1.5, self.w*0.75,20)
			self.mc_user.setWordWrap(True)
			self.mc_user.setStyleSheet('')

			self.frame_components.extend([
				self.mc_album_thumb, self.mc_title, self.mc_critic, self.mc_user
			])

			# metacritic components have been created--no need to do it again when song changes.
			self.metacritic_exists = True
		
		else:
			# otherwise, update the text and image
			self.mc_album_thumb.setPixmap(pixmap)
			self.mc_title.setText(review.album)
			self.mc_critic.setText(
				'Critic Score:   '+ str(review.critic_rating)[0]+'.'+str(review.critic_rating)[1]+
				'  ('+str(review.critic_count)+' reviews)'	
			)
			self.mc_user.setText(
				'User Score:    '+ str(review.user_rating)+ '  ('+str(review.user_count)+' reviews)'
			)

		self.show_frame_components()


	def default_metacritic_content(self, default_image):
		"""Clears Metacritic frame and creates default image & text
		
		Args:
			default_image (QPixmap)

		"""
		padding = 20
		if default_image.height() > default_image.width():
			default_image = default_image.scaledToHeight(self.h - padding)
		else:
			default_image = default_image.scaledToWidth(self.w/4 - padding)

		if not self.metacritic_exists:
			x = padding/10
			y = 0
			w = self.w / 4
			h = self.h
				
			self.mc_album_thumb.setGeometry(x,y, w,h)
			self.mc_album_thumb.setAlignment(Qt.AlignCenter)
			self.mc_title.setObjectName('mc_title')
			self.mc_title.setGeometry(self.w/3.8, self.h/10, self.w*0.75,20)
			self.mc_title.setWordWrap(True)

		self.mc_album_thumb.setPixmap(default_image)
		self.mc_title.setText('No results on Metacritic')
		self.mc_title.setStyleSheet('')
		self.mc_critic.hide() 
		self.mc_user.hide()


	def create_playback_buttons(self):
		"""
		Buttons created are: Previous, Play/Pause, Next

		"""
		self.playpause_button = QPushButton('Play/Pause', self.view)
		self.prev_button = QPushButton('Prev', self.view)
		self.next_button = QPushButton('Next', self.view)
		self.frame_components.extend([
			self.playpause_button, self.prev_button, self.next_button
		])
				
		self.playpause_button.setObjectName('playpause_button')
		self.prev_button.setObjectName('prev_button')		
		self.next_button.setObjectName('next_button')	

		self.prev_button.resize(self.prev_button.sizeHint().width()*1.4,
			self.prev_button.sizeHint().height())
		self.playpause_button.resize(self.playpause_button.sizeHint().width()*1.4,
			self.playpause_button.sizeHint().height())
		self.next_button.resize(self.next_button.sizeHint().width()*1.4,
			self.next_button.sizeHint().height())

		prevw = self.prev_button.width()
		playw = self.playpause_button.width()
		nextw = self.next_button.width()
		spacer = self.w / 30 if self.w / 30 < 16 else 15
		total = prevw + playw + nextw + spacer*2
		leftover = self.w - total
		prev_x = leftover / 2
		play_x = prev_x + spacer + prevw
		next_x = play_x + spacer + playw

		self.prev_button.move(prev_x, self.display_title_label.height()+
			self.display_title_label.height()/3)
		self.playpause_button.move(play_x, self.display_title_label.height()+
			self.display_title_label.height()/3)
		self.next_button.move(next_x, self.display_title_label.height()+
			self.display_title_label.height()/3)


	def create_image_buttons(self):
		"""
		Buttons created are: < (Left) & > (Right)

		"""
		self.next_image_button = QPushButton('>', self.view)
		self.prev_image_button = QPushButton('<', self.view)
		self.frame_components.extend([
			self.next_image_button, self.prev_image_button
		])

		self.next_image_button.setObjectName('next_image_button')
		self.prev_image_button.setObjectName('prev_image_button')

		self.next_image_button.resize(40, 30)
		self.prev_image_button.resize(40, 30)
		next_x = self.x + self.w/2
		prev_x = self.x + self.w/2 - 50
		y = self.h - 35
		self.next_image_button.move(next_x, y)
		self.prev_image_button.move(prev_x, y)


	def next_image(self):
		if self.images_list is not None:
			# Circular indexing--go to beginning of list if moving right at max index
			self.current_image = (self.current_image + 1) % len(self.images_list) 
			self.image_label.setPixmap(self.images_list[self.current_image])


	def prev_image(self):
		if self.images_list is not None:
			# Circular indexing--go to end of list if moving left on index 0
			self.current_image = (self.current_image - 1) % len(self.images_list)
			self.image_label.setPixmap(self.images_list[self.current_image])


	def clear_images_list(self):
		del self.images_list[:]

	def get_display_image_labels(self):
		return self.display_images_label

	def get_display_text_label(self):
		return self.display_text_label

	def get_display_title_label(self):
		return self.display_title_label

	def hide_frame_components(self):
		for f in self.frame_components:
			f.hide()

	def show_frame_components(self):
		for f in self.frame_components:
			f.show()

	def get_playback_prev_button(self):
		return self.prev_button

	def get_playback_play_button(self):
		return self.playpause_button

	def get_playback_next_button(self):
		return self.next_button

	def get_frame_components(self):
		return self.frame_components

	def get_popup_components(self):
		return self.popup_components

	def set_view(self, view):
		self.view = view

	# def mousePressEvent(self, event):
	# 	self.clicked.emit(self)

	def get_image_next_button(self):
		return self.next_image_button

	def get_image_prev_button(self):
		return self.prev_image_button

	def set_results(self, found):
		self.results_found = found

	def has_results(self):
		return self.results_found