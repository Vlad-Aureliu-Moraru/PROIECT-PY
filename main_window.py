# main_window.py

import sys
import re
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from ui_proiect import Ui_MainFrame
import BersteinFunctions as bnf # Your existing math functions

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from matplotlib.animation import FuncAnimation 

import numpy as np 
import BersteinFunctions as bnf
import LagrangeFunctions as lf


# Import the new modules
from plot_handler import PlotHandler
from ui_helpers import UIHelpers
from LagrangeWindowImp import LagrangeWindowImp


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.interval_1 = 0.0
        self.interval_2 = 1.0
        self.SLIDER_SCALE_FACTOR = 100

        self.ui = Ui_MainFrame()
        self.ui.setupUi(self)

        self.interval_1 = 0.0
        self.interval_2 = 1.0

        # Initialize helper modules
        self.plot_handler = PlotHandler(self.ui.AB_WIG_GRAF, self.interval_1, self.interval_2)
        self.ui_helpers = UIHelpers(slider_scale_factor=100) # Use your original scale factor of 100
        self.lagrange_window = LagrangeWindowImp(self.ui, self.ui.statusbar, self)

        # --- UI Element Setup ---
        self.ui.AB_SLIDER.setMinimum(1)
        self.ui.AB_SLIDER.setMaximum(50)
        self.ui.AB_SLIDER.setValue(5)

        self.ui_helpers.setup_float_slider(self.ui.AB_SLIDER_PUNCT, self.interval_1, self.interval_2)
        self.ui_helpers.set_slider_float_value(self.ui.AB_SLIDER_PUNCT, (self.interval_1 + self.interval_2) / 2)


        # --- Connect Signals/Slots ---
        self.ui.AB_BUTTON_CALCULEAZA.clicked.connect(self.calculeaza_func)
        self.ui.AB_SLIDER.valueChanged.connect(self.update_grad_label)
        self.ui.AB_SLIDER_PUNCT.valueChanged.connect(self.update_punct_label)
        self.ui.AB_BUTTON_INTERVAL.clicked.connect(self.set_interval)

        self.ui.AB_BUTTON_PLAY.clicked.connect(self.start_animation)
        # Uncomment and connect these if you add pause/stop buttons in your UI
        self.ui.AB_BUTTON_PREV.clicked.connect(self.stop_animation)
        # self.ui.ANIM_STOP_button.clicked.connect(self.stop_animation)

        # --- Initial UI State ---
        self.update_grad_label(self.ui.AB_SLIDER.value())
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value())
        self.ui.OUTPUT_textfield.setReadOnly(True)

        self.ui.statusbar.showMessage("Ready to calculate Bernstein approximation.", 3000) 

        # Initialize Lagrange interpolation variables
        self.lagrange_x_points = []
        self.lagrange_y_points = []
        self.lagrange_figure = None
        self.lagrange_canvas = None
        
        # Connect Lagrange interpolation UI elements
        #self.ui.IL_BUTTON_CALCULEAZA.clicked.connect(self.calculate_lagrange)
        self.ui.IL_BUTTON_DERIVATA.clicked.connect(self.calculate_lagrange_derivative)
        #self.ui.IL_BUTTON_ERROR.clicked.connect(self.calculate_lagrange_error)
        #self.ui.IL_BUTTON_GRAFIC.clicked.connect(self.plot_lagrange)
        self.ui.IL_BUTTON_ADAUGA.clicked.connect(self.add_lagrange_point)
        #self.ui.IL_BUTTON_STERGE.clicked.connect(self.remove_lagrange_point)
        
        # Set up Lagrange interpolation table
        self.ui.IL_TABEL.setColumnCount(2)
        self.ui.IL_TABEL.setHorizontalHeaderLabels(['X', 'Y'])
        
        # Set up Lagrange interpolation graph
        self.setup_lagrange_graph()
        
        # Set default values and placeholders
        self.ui.IL_TEXTFIELD_INTERVAL.setPlaceholderText("Enter interval [a,b]")
        self.ui.IL_TEXTFIELD_NODURI.setPlaceholderText("Enter number of nodes")
        self.ui.IL_TEXTFIELD_OUTPUT.setPlaceholderText("Enter point to evaluate")
        
        # Show initial status message
        self.ui.statusbar.showMessage("Ready for Lagrange interpolation. Please add points first.", 3000)

        # Perform initial plot
        self.plot_handler.plot_approximation(self.ui.AB_SLIDER.value())

    def setup_lagrange_graph(self):
        """Set up the graph for Lagrange interpolation"""
        self.lagrange_figure = Figure(figsize=(5, 4), dpi=100)
        self.lagrange_axes = self.lagrange_figure.add_subplot(111)
        self.lagrange_canvas = FigureCanvas(self.lagrange_figure)
        self.lagrange_toolbar = NavigationToolbar(self.lagrange_canvas, self)
        
        # Add the canvas and toolbar to the UI
        self.lagrange_graph_layout = QtWidgets.QVBoxLayout(self.ui.IL_WIG_GRAF)
        self.lagrange_graph_layout.addWidget(self.lagrange_toolbar)
        self.lagrange_graph_layout.addWidget(self.lagrange_canvas)
        
        # Add initial message to the plot
        self.lagrange_axes.text(0.5, 0.5, 'Add points to see the interpolation',
                              horizontalalignment='center',
                              verticalalignment='center',
                              transform=self.lagrange_axes.transAxes)
        self.lagrange_canvas.draw()
    
    def add_lagrange_point(self):
        """Add a new point to the Lagrange interpolation table"""
        try:
            # Get the number of nodes from the input field
            num_nodes_text = self.ui.IL_TEXTFIELD_NODURI.text().strip()
            if not num_nodes_text:
                raise ValueError("Please enter the number of nodes")
            
            num_nodes = int(num_nodes_text)
            if num_nodes <= 0:
                raise ValueError("Number of nodes must be positive")
            
            # Get the interval from the input field
            interval_text = self.ui.IL_TEXTFIELD_INTERVAL.text().strip()
            if not interval_text:
                raise ValueError("Please enter the interval")
                
            interval_match = re.match(r'\[(\d+),(\d+)\]', interval_text)
            if not interval_match:
                raise ValueError("Invalid interval format. Use [a,b]")
            
            a, b = map(int, interval_match.groups())
            if a >= b:
                raise ValueError("Interval start must be less than interval end")
            
            # Generate evenly spaced x points
            x_points = np.linspace(a, b, num_nodes)
            
            # Generate y points using a sample function (you can modify this)
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
            
            # Update the plot
            self.plot_lagrange()
            
            # Show success message
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
                # Reset the plot to show the initial message
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
    
    def calculate_lagrange_derivative(self):
        """Calculate the derivative of the Lagrange interpolation"""
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
            
            # Calculate the derivative
            result = lf.lagrange_derivative(self.lagrange_x_points, self.lagrange_y_points, x_eval)
            
            # Display the result
            self.ui.IL_TEXTFIELD_OUTPUT.setText(f"{result:.6f}")
            self.ui.statusbar.showMessage(f"Derivative calculated at x = {x_eval}", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            self.ui.statusbar.showMessage("Failed to calculate derivative. Please check your input.", 3000)
    
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
            
            # Define the original function (you can modify this)
            def original_func(x):
                return math.sin(x)
            
            # Create the plot
            fig, ax = lf.plot_lagrange_interpolation(
                self.lagrange_x_points,
                self.lagrange_y_points,
                original_func
            )
            
            # Update the canvas
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

        self.ui.statusbar.showMessage("Ready to calculate Bernstein approximation.", 3000)

        # Perform initial plot
        self.plot_handler.plot_approximation(self.ui.AB_SLIDER.value())

    # --- UI Event Handlers (now calling helper modules) ---
    def calculeaza_func(self):
        # Stop any animation
        self.plot_handler.stop_animation()

        punct = self.ui_helpers.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        grad = self.ui.AB_SLIDER.value()

        print(f"Calculating for point: {punct:.3f}, interval: [{self.interval_1:.2f},{self.interval_2:.2f}], degree: {grad}")

        try:
            approximated_value = bnf.aprox_berstein_on_interval(
                bnf.target_function, punct, grad, self.interval_1, self.interval_2
            )
            actual_value = bnf.target_function(punct)
            self.ui.OUTPUT_textfield.setText(f"Aproximare: {approximated_value:.6f} | Valoare Reala: {actual_value:.6f}")
            self.ui.statusbar.showMessage("Calcul efectuat cu succes!", 3000)
        except ValueError as e:
            QMessageBox.critical(self, "Eroare de Calcul", str(e))
            self.ui.statusbar.showMessage("Calcul esuat!", 3000)

        # Plot the result using the plot handler
        self.plot_handler.plot_approximation(n_degree=grad)


    def set_interval(self):
        # Stop any animation
        self.plot_handler.stop_animation()

        interval_str = self.ui.AB_INPUT_INTERVAL.text()
        parsed_interval_1, parsed_interval_2 = self.ui_helpers.parse_interval_string(interval_str, self)

        if parsed_interval_1 is None or parsed_interval_2 is None:
            # Error message already shown by ui_helpers.parse_interval_string
            self.ui.statusbar.showMessage("Format interval invalid sau valori invalide!", 3000)
            return

        self.interval_1 = parsed_interval_1
        self.interval_2 = parsed_interval_2

        # Update the plot handler's interval
        self.plot_handler.set_interval(self.interval_1, self.interval_2)

        print(f"Interval set to: [{self.interval_1:.2f}, {self.interval_2:.2f}]")
        self.ui.statusbar.showMessage(f"Interval set to [{self.interval_1:.2f}, {self.interval_2:.2f}]", 3000)

        # Update the 'punct' slider's range using ui_helpers
        self.ui_helpers.setup_float_slider(self.ui.AB_SLIDER_PUNCT, self.interval_1, self.interval_2)
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value()) # Update label immediately

        # Re-plot the graph with the new interval
        self.plot_handler.plot_approximation(self.ui.AB_SLIDER.value())


    # --- Slider Label Update Functions ---
    def update_grad_label(self, value):
        self.ui.AB_LABEL_GRAD.setText(f"GRAD:{value}")

    def update_punct_label(self, value):
        float_value = self.ui_helpers.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        self.ui.AB_LABEL_PUNCT.setText(f"Punct:{float_value:.3f}")

    # --- Animation Control Methods ---
    def start_animation(self):
        print("ANIMATION")
        self.ui.statusbar.showMessage("Starting animation...", 2000)
        min_degree = self.ui.AB_SLIDER.minimum()
        max_degree = self.ui.AB_SLIDER.maximum()
        self.plot_handler.start_animation(min_degree, max_degree)

    def pause_animation(self):
        # Implement if you add a pause button
        self.plot_handler.stop_animation()
        pass

    def stop_animation(self):
        # Implement if you add a stop button
        self.plot_handler.stop_animation()
        # self.plot_handler.plot_approximation(self.ui.AB_SLIDER.value()) # Re-plot static graph
        pass
