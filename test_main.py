from ctypes import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import main_window

if __name__ == '__main__':
	
	import sys
	app = QApplication(sys.argv)
	main_window = main_window.MainWindow()
	# Ui_MainWindow().setupUi(main_window)
	main_window.show()
	sys.exit(app.exec_())    



