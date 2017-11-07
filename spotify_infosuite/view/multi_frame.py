from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *
import os

class MultiFrameWindow(QWidget):

    def __init__(self, x, y, w, h, window_title, object_title):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.window_title = window_title
        self.object_title = object_title
        self.setObjectName(self.object_title)
        self.setGeometry(self.x, self.y, self.w, self.h)
        self.frames = []
        self.load_styles()


    def add_frame_bio(self, frame):
        # frame.move(frame.x, frame.y)
        self.frames.append(frame)
        frame.show()

    def add_frame(self, frame):
        self.frames.append(frame)
        frame.show()


    # Opens css stylesheet and apply it to Spotify Infosuite elements
    def load_styles(self):
        style = ''
        cwd = os.getcwd() + '/spotify_infosuite/' # Get current working directory         
        with open(cwd + 'view/style.css') as f:
            for line in f:
                style += line
                # print(line)
        self.setStyleSheet(style)
