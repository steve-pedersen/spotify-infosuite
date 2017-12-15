"""
Fall 2017 CSc 690
File: multi_frame.py
Author: Steve Pedersen & Andrew Lesondak
System: OS X
Date: 12/13/2017
Usage: python3 spotify_infosuite.py
Dependencies: pyqt5
Description: MultiFrameWindow class.  The main window of the application, made up of frames.

"""

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *
import os

class MultiFrameWindow(QWidget):
    """MultiFrameWindow is the main window of the application.  It serves as the central
    location for all frames to reside.

    Args:
        x (int) -- position of MultiFrameWindow
        y (int) -- position of MultiFrameWindow
        w (int) -- width of MultiFrameWindow
        h (int) -- height of MultiFrameWindow
        window_title (str) -- title text displayed at top of window
        object_title (str) - used to organize visual styling of elements

    """
    def __init__(self, x, y, w, h, window_title, object_title):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.window_title = window_title
        self.object_title = object_title
        self.setWindowTitle(self.window_title)
        self.setObjectName(self.object_title)
        self.setGeometry(self.x, self.y, self.w, self.h)
        self.frames = []
        self.load_styles()


    def add_frame_bio(self, frame):
        """Used to add artist bio to bio frame

        Args:
            frame (object) -- name of frame to add bio to

        """
        # frame.move(frame.x, frame.y)
        self.frames.append(frame)
        frame.show()

    def add_frame(self, frame):
        """Used to add frame to main window

        Args:
            frame (object) -- name of frame to add to window

        """
        self.frames.append(frame)
        for component in frame.get_frame_components():
            component.show()        
        frame.show()


    # Opens css stylesheet and apply it to Spotify Infosuite elements
    def load_styles(self):
        """Used to add CSS styling to elements

        """
        style = ''
        # with open('./view/style.css') as f:
        with open(os.path.dirname(__file__) + '/style.css') as f:
            for line in f:
                style += line
                # print(line)
        self.setStyleSheet(style)

