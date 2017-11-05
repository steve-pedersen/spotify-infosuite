import os, sys, Controller
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
	app = QApplication(sys.argv)
	controller = Controller()
	sys.exit(app.exec_())    