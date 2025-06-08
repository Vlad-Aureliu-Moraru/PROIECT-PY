# main_window.py
import sys
import re
import math

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation 
import numpy as np 

from plot_handler import PlotHandler
from ui_helpers import UIHelpers

from LagrangeWindowImp import LagrangeWindowImp
from BersteinWindowImp import BersteinWindowImp
from ui_proiect import Ui_MainFrame

import BersteinFunctions as bnf
import LagrangeFunctions as lf

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainFrame()
        self.ui.setupUi(self)
        
        self.ui_helpers = UIHelpers(slider_scale_factor=100)
        self.lagrange_window = LagrangeWindowImp(self.ui, self.ui.statusbar, self)
        
        self.bernstein_window = BersteinWindowImp(self.ui, self.ui.statusbar, self)
        self.ui.IL_TABEL.setColumnCount(2)
        self.ui.IL_TABEL.setHorizontalHeaderLabels(['X', 'Y'])
        
        self.lagrange_x_points = []
        self.lagrange_y_points = []
        self.lagrange_figure = None
        self.lagrange_canvas = None
        
        self.ui.IL_BUTTON_ADAUGA.clicked.connect(LagrangeWindowImp.add_lagrange_point)
