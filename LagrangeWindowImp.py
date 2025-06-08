import numpy as np
import math
import re
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import LagrangeFunctions as lf

class LagrangeWindowImp:
    def __init__(self, ui, statusbar, parent_widget):
        self.ui = ui
        self.statusbar = statusbar
        self.parent_widget = parent_widget
        self.lagrange_x_points = []
        self.lagrange_y_points = []
        self.lagrange_figure = None
        self.lagrange_canvas = None
        self.lagrange_axes = None
        
        # Set up UI elements
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI elements for Lagrange interpolation"""
        # Set up Lagrange interpolation table
        self.ui.IL_TABEL.setColumnCount(2)
        self.ui.IL_TABEL.setHorizontalHeaderLabels(['X', 'Y'])
        
        # Set up Lagrange interpolation graph
        self.setup_lagrange_graph()
        
        # Set default values and placeholders
        self.ui.IL_TEXTFIELD_INTERVAL.setPlaceholderText("Enter interval [a,b]")
        self.ui.IL_TEXTFIELD_NODURI.setPlaceholderText("Enter number of nodes")
        self.ui.IL_TEXTFIELD_OUTPUT.setPlaceholderText("Enter point to evaluate")
        
        # Connect buttons
        #self.ui.IL_BUTTON_CALCULEAZA.clicked.connect(self.calculate_lagrange)
        self.ui.IL_BUTTON_DERIVATA.clicked.connect(self.calculate_lagrange_derivative)
        #self.ui.IL_BUTTON_ERROR.clicked.connect(self.calculate_lagrange_error)
        #self.ui.IL_BUTTON_GRAFIC.clicked.connect(self.plot_lagrange)
        self.ui.IL_BUTTON_ADAUGA.clicked.connect(self.add_lagrange_point)
        #self.ui.IL_BUTTON_STERGE.clicked.connect(self.remove_lagrange_point)
        
        # Show initial status message
        self.statusbar.showMessage("Ready for Lagrange interpolation. Please add points first.", 3000)

    def setup_lagrange_graph(self):
        """Set up the graph for Lagrange interpolation"""
        self.lagrange_figure = Figure(figsize=(5, 4), dpi=100)
        self.lagrange_axes = self.lagrange_figure.add_subplot(111)
        self.lagrange_canvas = FigureCanvas(self.lagrange_figure)
        self.lagrange_toolbar = NavigationToolbar(self.lagrange_canvas, self.parent_widget)
        
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
            self.statusbar.showMessage(f"Added {num_nodes} points for interpolation", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))
            self.statusbar.showMessage("Failed to add points. Please check your input.", 3000)

    def remove_lagrange_point(self):
        """Remove the selected point from the Lagrange interpolation table"""
        current_row = self.ui.IL_TABEL.currentRow()
        if current_row >= 0:
            self.ui.IL_TABEL.removeRow(current_row)
            self.lagrange_x_points.pop(current_row)
            self.lagrange_y_points.pop(current_row)
            
            if self.lagrange_x_points:
                self.plot_lagrange()
                self.statusbar.showMessage(f"Removed point. {len(self.lagrange_x_points)} points remaining.", 3000)
            else:
                # Reset the plot to show the initial message
                self.lagrange_axes.clear()
                self.lagrange_axes.text(0.5, 0.5, 'Add points to see the interpolation',
                                      horizontalalignment='center',
                                      verticalalignment='center',
                                      transform=self.lagrange_axes.transAxes)
                self.lagrange_canvas.draw()
                self.statusbar.showMessage("No points available. Please add points first.", 3000)

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
                QMessageBox.warning(self.ui, "Warning", 
                                  f"Point {x_eval} is outside the interpolation range [{x_min:.2f}, {x_max:.2f}]")
            
            # Calculate the interpolation
            result = lf.lagrange_interpolation(self.lagrange_x_points, self.lagrange_y_points, x_eval)
            
            # Display the result
            self.ui.IL_TEXTFIELD_OUTPUT.setText(f"{result:.6f}")
            self.statusbar.showMessage(f"Interpolation calculated at x = {x_eval}", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))
            self.statusbar.showMessage("Failed to calculate interpolation. Please check your input.", 3000)

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
                QMessageBox.warning(self.ui, "Warning", 
                                  f"Point {x_eval} is outside the interpolation range [{x_min:.2f}, {x_max:.2f}]")
            
            # Calculate the derivative
            result = lf.lagrange_derivative(self.lagrange_x_points, self.lagrange_y_points, x_eval)
            
            # Display the result
            self.ui.IL_TEXTFIELD_OUTPUT.setText(f"{result:.6f}")
            self.statusbar.showMessage(f"Derivative calculated at x = {x_eval}", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))
            self.statusbar.showMessage("Failed to calculate derivative. Please check your input.", 3000)

    def calculate_lagrange_error(self):
        """Calculate the error of the Lagrange interpolation"""
        try:
            if not self.lagrange_x_points:
                raise ValueError("No points available for interpolation. Please add points first.")
            
            # Calculate the error using the target function
            error = lf.calculate_error(self.lagrange_x_points, self.lagrange_y_points)
            
            # Display the error
            self.ui.IL_TEXTFIELD_ERROR.setText(f"{error:.6f}")
            self.statusbar.showMessage("Error calculated successfully", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))
            self.statusbar.showMessage("Failed to calculate error. Please check your input.", 3000)

    def plot_lagrange(self):
        """Plot the Lagrange interpolation"""
        try:
            if not self.lagrange_x_points:
                raise ValueError("No points available for interpolation. Please add points first.")
            
            # Create the plot using the target function
            fig, ax = lf.plot_lagrange_interpolation(
                self.lagrange_x_points,
                self.lagrange_y_points
            )
            
            # Update the canvas
            self.lagrange_axes.clear()
            self.lagrange_axes.plot(ax.lines[0].get_xdata(), ax.lines[0].get_ydata(), 'b-', label='Lagrange Interpolation')
            self.lagrange_axes.scatter(self.lagrange_x_points, self.lagrange_y_points, color='red', label='Interpolation Points')
            self.lagrange_axes.plot(ax.lines[1].get_xdata(), ax.lines[1].get_ydata(), 'g--', label='Target Function')
            self.lagrange_axes.grid(True)
            self.lagrange_axes.legend()
            self.lagrange_axes.set_title('Lagrange Interpolation')
            self.lagrange_axes.set_xlabel('x')
            self.lagrange_axes.set_ylabel('y')
            
            self.lagrange_canvas.draw()
            self.statusbar.showMessage("Plot updated successfully", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))
            self.statusbar.showMessage("Failed to update plot. Please check your input.", 3000)
