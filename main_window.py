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
        
        self.ui.IL_BUTTON_ADAUGA.clicked.connect(self.add_lagrange_point)
        
        self.setup_lagrange_graph()

    def setup_lagrange_graph(self):
        self.lagrange_figure = Figure(figsize=(5, 4), dpi=100)
        self.lagrange_axes = self.lagrange_figure.add_subplot(111)
        self.lagrange_canvas = FigureCanvas(self.lagrange_figure)
        self.lagrange_toolbar = NavigationToolbar(self.lagrange_canvas, self)
        
        self.lagrange_graph_layout = QtWidgets.QVBoxLayout(self.ui.IL_WIG_GRAF)
        self.lagrange_graph_layout.addWidget(self.lagrange_toolbar)
        self.lagrange_graph_layout.addWidget(self.lagrange_canvas)
        
        self.lagrange_axes.text(0.5, 0.5, '',
                              horizontalalignment='center',
                              verticalalignment='center',
                              transform=self.lagrange_axes.transAxes)
        self.lagrange_canvas.draw()
    
    def add_lagrange_point(self):
        try:
            num_nodes_text = self.ui.IL_TEXTFIELD_NODURI.text().strip()
            if not num_nodes_text:
                raise ValueError("Please enter the number of nodes")
            num_nodes = int(num_nodes_text)
            if num_nodes <= 0:
                raise ValueError("Number of nodes must be positive")
            
            interval_text = self.ui.IL_TEXTFIELD_INTERVAL.text().strip()
            if not interval_text:
                raise ValueError("Please enter the interval")
                
            interval_match = re.match(r'\[(\d+),(\d+)\]', interval_text)
            if not interval_match:
                raise ValueError("Invalid interval format. Use [a,b]")    
            a, b = map(int, interval_match.groups())
            if a >= b:
                raise ValueError("Interval start must be less than interval end")
            
            x_points = np.linspace(a, b, num_nodes)
            y_points = [math.sin(x) for x in x_points]
            
            # Clear existing points
            self.lagrange_x_points = []
            self.lagrange_y_points = []
            self.ui.IL_TABEL.setRowCount(0)
            
            # Add points to table and store them
            for x, y in zip(x_points, y_points):
                self.lagrange_x_points.append(x)
                self.lagrange_y_points.append(y)
                row = self.ui.IL_TABEL.rowCount()
                self.ui.IL_TABEL.insertRow(row)
                self.ui.IL_TABEL.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{x:.4f}"))
                self.ui.IL_TABEL.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{y:.4f}"))
            
            self.plot_lagrange()
            self.ui.statusbar.showMessage(f"Added {num_nodes} points for interpolation", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            self.ui.statusbar.showMessage("Failed to add points. Please check your input.", 3000)
    
    def remove_lagrange_point(self):
        """Remove the selected point from the Lagrange interpolation table"""
        current_row = self.ui.IL_TABEL.currentRow()
        if current_row >= 0:
            self.ui.IL_TABEL.removeRow(current_row)
            self.lagrange_x_points.pop(current_row)
            self.lagrange_y_points.pop(current_row)
            
            if self.lagrange_x_points:
                self.plot_lagrange()
                self.ui.statusbar.showMessage(f"Removed point. {len(self.lagrange_x_points)} points remaining.", 3000)
            else:
                self.lagrange_axes.clear()
                self.lagrange_axes.text(0.5, 0.5, 'Add points to see the interpolation',
                                      horizontalalignment='center',
                                      verticalalignment='center',
                                      transform=self.lagrange_axes.transAxes)
                self.lagrange_canvas.draw()
                self.ui.statusbar.showMessage("No points available. Please add points first.", 3000)
    
    def calculate_lagrange(self):
        """Calculate the Lagrange interpolation at the given point"""
        try:
            if not self.lagrange_x_points:
                raise ValueError("No points available for interpolation. Please add points first.")
            
            # Get the point to evaluate from the output field
            x_eval_text = self.ui.IL_TEXTFIELD_OUTPUT.text().strip()
            if not x_eval_text:
                raise ValueError("Please enter a point to evaluate")
                
            x_eval = float(x_eval_text)
            
            # Check if the point is within the interpolation range
            x_min, x_max = min(self.lagrange_x_points), max(self.lagrange_x_points)
            if not (x_min <= x_eval <= x_max):
                QMessageBox.warning(self, "Warning", 
                                  f"Point {x_eval} is outside the interpolation range [{x_min:.2f}, {x_max:.2f}]")
            
            # Calculate the interpolation
            result = lf.lagrange_interpolation(self.lagrange_x_points, self.lagrange_y_points, x_eval)
            
            # Display the result
            self.ui.IL_TEXTFIELD_OUTPUT.setText(f"{result:.6f}")
            self.ui.statusbar.showMessage(f"Interpolation calculated at x = {x_eval}", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            self.ui.statusbar.showMessage("Failed to calculate interpolation. Please check your input.", 3000)
  
    def calculate_lagrange_error(self):
        """Calculate the error of the Lagrange interpolation"""
        try:
            if not self.lagrange_x_points:
                raise ValueError("No points available for interpolation. Please add points first.")
            
            # Define the original function (you can modify this)
            def original_func(x):
                return math.sin(x)
            
            # Calculate the error
            error = lf.calculate_error(self.lagrange_x_points, self.lagrange_y_points, original_func)
            
            # Display the error
            self.ui.IL_TEXTFIELD_ERROR.setText(f"{error:.6f}")
            self.ui.statusbar.showMessage("Error calculated successfully", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            self.ui.statusbar.showMessage("Failed to calculate error. Please check your input.", 3000)
    
    def plot_lagrange(self):
        """Plot the Lagrange interpolation"""
        try:
            if not self.lagrange_x_points:
                raise ValueError("No points available for interpolation. Please add points first.")
            def original_func(x):
                return math.sin(x)
            fig, ax = lf.plot_lagrange_interpolation(
                self.lagrange_x_points,
                self.lagrange_y_points,
                original_func
            )
            self.lagrange_axes.clear()
            self.lagrange_axes.plot(ax.lines[0].get_xdata(), ax.lines[0].get_ydata(), 'b-', label='Lagrange Interpolation')
            self.lagrange_axes.scatter(self.lagrange_x_points, self.lagrange_y_points, color='red', label='Interpolation Points')
            self.lagrange_axes.plot(ax.lines[1].get_xdata(), ax.lines[1].get_ydata(), 'g--', label='Original Function')
            self.lagrange_axes.grid(True)
            self.lagrange_axes.legend()
            self.lagrange_axes.set_title('Lagrange Interpolation')
            self.lagrange_axes.set_xlabel('x')
            self.lagrange_axes.set_ylabel('y')
            self.lagrange_canvas.draw()
            self.ui.statusbar.showMessage("Plot updated successfully", 3000)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            self.ui.statusbar.showMessage("Failed to update plot. Please check your input.", 3000)
