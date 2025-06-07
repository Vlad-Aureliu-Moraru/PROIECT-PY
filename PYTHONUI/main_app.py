# main_app.py
import sys
from PyQt5 import QtWidgets

# Import your MainWindow class
from main_window import MainWindow

#funct


#import_CSV

#import_TXT

#manual_input


#calculeaza_func


#compare_func

#salveaza_graph



#salveaza_anim

#set_output

#set_Error

#play_anim

#back_anim

#front_anim
   
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow() 
    window.show()
    sys.exit(app.exec_())
