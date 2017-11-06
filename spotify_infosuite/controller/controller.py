from model.frame import Frame
from view.view_multi import ViewMulti
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *

class Controller():

    def __init__(self):

        self.view_multi = ViewMulti(0, 0, 800, 600, "Spotify Info Suite", "view_multi")

        self.bio_frame = Frame(self, self.view_multi, 0, 100, 250, 400, "bio_frame")
        self.bio_frame.set_display_text("mogwai was born in blah blah blah", 10, 10)
        self.bio_frame.set_display_title("Bio", 5, 5)
        self.view_multi.add_frame_bio(self.bio_frame)
        self.view_multi.show()