# main_window.py

import sys
import re
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
from ui_proiect import Ui_MainFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np
import BersteinFunctions as bnf
import LagrangeFunctions as lf

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.interval_1 = 0.0
        self.interval_2 = 1.0
        self.SLIDER_SCALE_FACTOR = 100
        self.ui = Ui_MainFrame()
        self.ui.setupUi(self)

        # --- Matplotlib Graph Setup ---
        # 1. Create a Figure object for the plot
        self.figure = Figure(figsize=(5, 4), dpi=100)
        # 2. Add an Axes (subplot) to the figure. This is where we'll draw.
        self.axes = self.figure.add_subplot(111)
        # 3. Create a FigureCanvasQTAgg instance (the actual Qt widget for the plot)
        self.canvas = FigureCanvas(self.figure)
        # 4. Create a NavigationToolbar for interactive features (zoom, pan, save)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # 5. Add the canvas and toolbar to your UI's graph placeholder widget
        self.graph_layout = QtWidgets.QVBoxLayout(self.ui.AB_WIG_GRAF)
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)

        # --- Animation Specific Attributes ---
        self.animation = None         # Stores the FuncAnimation object
        self.is_animating = False     # Flag to track animation state
        self.anim_interval_ms = 100   # Milliseconds between frames (adjust for speed)

        # --- UI Element Setup ---
        self.ui.AB_SLIDER.setMinimum(1)
        self.ui.AB_SLIDER.setMaximum(50)
        self.ui.AB_SLIDER.setValue(5)

        # --- Connect Signals/Slots ---
        self.ui.AB_BUTTON_CALCULEAZA.clicked.connect(self.calculeaza_func)
        self.ui.AB_SLIDER.valueChanged.connect(self.update_grad_label)
        self.ui.AB_SLIDER_PUNCT.valueChanged.connect(self.update_punct_label)
        self.ui.AB_BUTTON_INTERVAL.clicked.connect(self.set_interval)
        self.ui.AB_BUTTON_PLAY.clicked.connect(self.start_animation)
        self.ui.AB_BUTTON_PREV.clicked.connect(self.stop_animation)
        self.ui.AB_BUTTON_NEXT.clicked.connect(self.reset_animation)

        # --- Initial UI State ---
        self.update_grad_label(self.ui.AB_SLIDER.value())
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value())
        self.ui.OUTPUT_textfield.setReadOnly(True)
        self.ui.statusbar.showMessage("Ready to calculate Bernstein approximation.", 3000)

        # --- Lagrange Interpolation Setup ---
        # Initialize Lagrange interpolation variables
        self.lagrange_x_points = []
        self.lagrange_y_points = []
        self.lagrange_figure = None
        self.lagrange_canvas = None
        
        # Animation attributes for Lagrange interpolation
        self.lagrange_animation = None
        self.is_lagrange_animating = False
        self.lagrange_anim_interval_ms = 100
        self.current_lagrange_frame = 0
        self.lagrange_animation_frames = 100  # Total number of frames in animation

        # Connect Lagrange interpolation UI elements
        self.ui.IL_BUTTON_CALCULEAZA.clicked.connect(self.add_lagrange_point)
        self.ui.IL_BUTTON_DERIVATA.clicked.connect(self.calculate_lagrange_derivative)
        self.ui.IL_BUTTON_ERROR.clicked.connect(self.calculate_lagrange_error)
        self.ui.IL_BUTTON_GRAFIC.clicked.connect(self.plot_lagrange)
        self.ui.IL_BUTTON_ADAUGA.clicked.connect(self.add_lagrange_point)
        self.ui.IL_BUTTON_STERGE.clicked.connect(self.remove_lagrange_point)
        
        # Connect Lagrange animation buttons
        self.ui.IL_BUTTON_PLAY.clicked.connect(self.start_lagrange_animation)
        self.ui.IL_BUTTON_PREV.clicked.connect(self.stop_lagrange_animation)
        self.ui.IL_BUTTON_NEXT.clicked.connect(self.reset_lagrange_animation)
        
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

    def _plot_approximation(self, num_points=200):
        """Internal method to clear and redraw the Matplotlib graph based on current parameters."""
        # Clear the previous plot content
        self.axes.cla()
        # Get current parameters from the instance variables and UI
        a = self.interval_1
        b = self.interval_2
        n_degree = self.ui.AB_SLIDER.value() # Degree comes from the integer slider

        # Generate evenly spaced y-values across the current interval for plotting
        y_values = np.linspace(a, b, num_points)

        # Calculate the original function values
        original_func_values = [bnf.target_function(y) for y in y_values]

        # Calculate the Bernstein approximation values for each point
        bernstein_approx_values = [bnf.aprox_berstein_on_interval(bnf.target_function, y, n_degree, a, b) for y in y_values]

        # Plot the data on the axes
        self.axes.plot(y_values, original_func_values, label='Functia Originala $f(y)$', color='blue', linestyle='-')
        self.axes.plot(y_values, bernstein_approx_values, label=f'Aproximare Bernstein ($n={n_degree}$)', color='red', linestyle='--')

        # Add labels, title, and legend for clarity
        self.axes.set_title(f"Aproximare Bernstein pe intervalul $[{a:.2f}, {b:.2f}]$")
        self.axes.set_xlabel("y")
        self.axes.set_ylabel("$f(y)$ / Aproximare")
        self.axes.legend()
        self.axes.grid(True)
        # Add vertical lines to clearly mark the interval boundaries
        self.axes.axvline(a, color='gray', linestyle=':', linewidth=0.8, label=f'Inceput Interval ({a:.2f})')
        self.axes.axvline(b, color='gray', linestyle=':', linewidth=0.8, label=f'Sfarsit Interval({b:.2f})')
        # Redraw the canvas to display the updated plot in the GUI
        self.canvas.draw()

    def calculeaza_func(self):
        """Calculate the Bernstein approximation at the given point"""
        punct = self.ui.AB_SLIDER_PUNCT.value()/100
        grad = self.ui.AB_SLIDER.value()
        print(f"{punct}:{self.interval_1};{grad}")
        bnf.aprox_berstein_on_interval(bnf.target_function,punct,grad,self.interval_1,self.interval_2)
        print(f"real value {bnf.target_function(punct)}")
        self._plot_approximation()

    def set_interval(self):
        """Set the interval for calculations"""
        intervalRegEx = r"^\[\d+,\d+\]$"
        interval = self.ui.AB_INPUT_INTERVAL.text()
        if not re.match(intervalRegEx, interval):
            print("ERROR MATCHING")
            return
        first_half = interval[1:2]
        second_half = interval[3:4]
        self.interval_1 = int(first_half)
        self.interval_2 = int(second_half)
        print(self.interval_1)
        print(self.interval_2)
        self.ui.AB_SLIDER_PUNCT.setMinimum(self.interval_1*self.SLIDER_SCALE_FACTOR)
        self.ui.AB_SLIDER_PUNCT.setMaximum(self.interval_2*self.SLIDER_SCALE_FACTOR)
        print(interval)

    def update_grad_label(self, value):
        """Update the degree label"""
        self.ui.AB_LABEL_GRAD.setText(f"GRAD:{value}")

    def update_punct_label(self, value):
        """Update the point label"""
        self.ui.AB_LABEL_PUNCT.setText(f"Punct:{value/100}")

    def start_animation(self):
        """Start the animation of the Bernstein approximation"""
        print("ANIMATION")
        if self.is_animating:
            return # Animation already running
        self.ui.statusbar.showMessage("Starting animation...", 2000)
        self.is_animating = True
        # Ensure initial plot for blitting setup
        self._plot_approximation(fixed_degree=self.current_anim_degree)

        # Create the animation object
        self.animation = FuncAnimation(
            self.figure,
            self._update_animation_frame,
            frames=range(self.ui.AB_SLIDER.minimum(), self.ui.AB_SLIDER.maximum() + 1),
            interval=self.anim_interval_ms,
            blit=True,
            repeat=False
        )

        self.canvas.draw_idle()

    def stop_animation(self):
        """Stop the animation"""
        if self.animation:
            self.animation.event_source.stop()
            self.is_animating = False
            self.ui.statusbar.showMessage("Animation stopped", 2000)

    def reset_animation(self):
        """Reset the animation"""
        self.stop_animation()
        self.current_anim_degree = self.ui.AB_SLIDER.minimum()
        self._plot_approximation()
        self.ui.statusbar.showMessage("Animation reset", 2000)

    def _update_animation_frame(self, frame):
        """Update function for the animation"""
        self.current_anim_degree = frame
        self._plot_approximation()
        return self.axes.get_lines() + self.axes.collections

    # --- Lagrange Interpolation Methods ---
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

    def start_lagrange_animation(self):
        """Start the animation of the Lagrange interpolation"""
        if self.is_lagrange_animating:
            return  # Animation already running
            
        if not self.lagrange_x_points:
            QMessageBox.warning(self, "Error", "Please add points first")
            return
            
        self.is_lagrange_animating = True
        self.current_lagrange_frame = 0
        self.ui.statusbar.showMessage("Starting Lagrange interpolation animation...", 2000)
        
        # Create the animation
        self.lagrange_animation = FuncAnimation(
            self.lagrange_figure,
            self._update_lagrange_animation_frame,
            frames=150,  # More frames for smoother point appearance
            interval=100,  # Keep the same interval
            blit=True,
            repeat=False
        )
        
        self.lagrange_canvas.draw_idle()

    def stop_lagrange_animation(self):
        """Stop the Lagrange interpolation animation"""
        if self.lagrange_animation:
            self.lagrange_animation.event_source.stop()
            self.is_lagrange_animating = False
            self.ui.statusbar.showMessage("Animation stopped", 2000)

    def reset_lagrange_animation(self):
        """Reset the Lagrange interpolation animation"""
        self.stop_lagrange_animation()
        self.current_lagrange_frame = 0
        self.plot_lagrange()  # Reset to initial state
        self.ui.statusbar.showMessage("Animation reset", 2000)

    def _update_lagrange_animation_frame(self, frame):
        """Update function for the Lagrange interpolation animation with sequential node appearance"""
        self.current_lagrange_frame = frame
        progress = frame / self.lagrange_animation_frames
        
        # Clear the current plot
        self.lagrange_axes.clear()
        
        # Calculate the domain for plotting
        x_min, x_max = min(self.lagrange_x_points), max(self.lagrange_x_points)
        x_curve = np.linspace(x_min, x_max, 200)
        
        # Calculate how many points should be visible based on progress
        num_points = len(self.lagrange_x_points)
        points_to_show = int(progress * num_points)
        
        # Plot only the visible points
        visible_x = self.lagrange_x_points[:points_to_show]
        visible_y = self.lagrange_y_points[:points_to_show]
        
        # Plot the visible points
        self.lagrange_axes.scatter(visible_x, visible_y, 
                                 color='red', label='Interpolation Points',
                                 s=100, alpha=0.8)
        
        # Only draw the interpolation curve if we have at least 2 points
        if points_to_show >= 2:
            # Calculate and plot the interpolation curve
            y_curve = [lf.lagrange_interpolation(visible_x, visible_y, x) 
                      for x in x_curve]
            
            # Plot the interpolation curve
            self.lagrange_axes.plot(x_curve, y_curve, 'b-', 
                                  label='Lagrange Interpolation',
                                  linewidth=2)
        
        # Add original function
        def original_func(x):
            return math.sin(x)
        y_original = [original_func(x) for x in x_curve]
        self.lagrange_axes.plot(x_curve, y_original, 'g--', 
                              label='Original Function',
                              alpha=0.5)
        
        # Set up the plot
        self.lagrange_axes.grid(True, alpha=0.3)
        self.lagrange_axes.legend(loc='upper right')
        self.lagrange_axes.set_title(f'Lagrange Interpolation (Points: {points_to_show}/{num_points})')
        self.lagrange_axes.set_xlabel('x')
        self.lagrange_axes.set_ylabel('y')
        
        return self.lagrange_axes.get_lines() + self.lagrange_axes.collections

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
