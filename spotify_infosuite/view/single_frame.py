from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QAction, QLineEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import *
import os

class SingleFrameWindow(QWidget):

    def __init__(self):
        super().__init__()
        

    def init_popup(self, x, y, window_title, object_title):
        self.x = x
        self.y = y
        self.window_title = window_title
        self.object_title = object_title
        self.setWindowTitle(self.window_title)
        self.setObjectName(self.object_title)
        
        self.setFocus()
        # A modal widget prevents widgets in all other windows from getting any input.
        # self.isModal()


    def add_frame(self, frame):
        for component in frame.get_popup_components():
            component.show()        

        self.w = frame.popup_text.width()        
        self.h = frame.popup_text.height()
        
        self.setGeometry(self.x, self.y, self.w, self.h)
        self.load_styles()

        frame.show()


    # Opens css stylesheet and apply it to Spotify Infosuite elements
    def load_styles(self):
        self.setStyleSheet('')
        style = ''
        with open('./view/style.css') as f:
            for line in f:
                style += line
                # print(line)
        self.setStyleSheet(style)

