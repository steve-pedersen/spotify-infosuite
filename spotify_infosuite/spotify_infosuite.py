from controller.controller import Controller
import os, sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	# user can choose to scale to window by passing 1 as a cmd arg
	use_default = True
	if len(sys.argv) == 2 and str(sys.argv[1]) == '1':
		use_default = False

	# run app with selected window dimensions
	controller = Controller(app, use_default)
	
	sys.exit(app.exec_())