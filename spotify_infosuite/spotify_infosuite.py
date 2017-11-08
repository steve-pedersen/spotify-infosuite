from controller.controller import Controller
import os, sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
	app = QApplication(sys.argv)
	screen_resolution = app.desktop().screenGeometry()
	width, height = screen_resolution.width(), screen_resolution.height()	
	controller = Controller(width, height)
	sys.exit(app.exec_())