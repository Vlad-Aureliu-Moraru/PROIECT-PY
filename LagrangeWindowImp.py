import numpy as np
import math
import re
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import LagrangeFunctions as lf
from matplotlib.animation import FuncAnimation

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
        self.animation = None
        self.current_points = 0
        self.max_points = 0
        self.animation_interval = 1000  # 1 second between frames
        
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
        self.ui.IL_TEXTFIELD_ERROR.setPlaceholderText("Enter error")
        
        # Connect buttons
        self.ui.IL_BUTTON_ADAUGA.clicked.connect(self.add_lagrange_point)
        self.ui.IL_BUTTON_PLAY.clicked.connect(self.start_animation)
        self.ui.IL_BUTTON_PREV.clicked.connect(self.stop_animation)
        self.ui.IL_BUTTON_NEXT.clicked.connect(self.reset_animation)
        
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
        """Add points and calculate Lagrange interpolation"""
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
            
            # Store the interval and max points for animation
            self.interval = (a, b)
            self.max_points = num_nodes
            self.current_points = 0
            
            # Generate evenly spaced x points
            x_points = np.linspace(a, b, num_nodes)
            
            # Generate y points using the target function
            y_points = [lf.target_function(x) for x in x_points]
            
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
            
            # Calculate interpolation at the midpoint of the interval
            x_eval = (a + b) / 2
            interpolated_value = lf.lagrange_interpolation(self.lagrange_x_points, self.lagrange_y_points, x_eval)
            actual_value = lf.target_function(x_eval)
            
            # Calculate the maximum error
            max_error = lf.calculate_interpolation_error(self.lagrange_x_points, self.lagrange_y_points)
            
            # Display the results
            self.ui.IL_TEXTFIELD_OUTPUT.setText(f"Interpolated: {interpolated_value:.6f} | Actual: {actual_value:.6f}")
            self.ui.IL_TEXTFIELD_ERROR.setText(f"{max_error:.6f}")
            
            # Update the plot
            self.plot_lagrange()
            
            # Show success message
            self.statusbar.showMessage(f"Added {num_nodes} points. Max error: {max_error:.6f}", 3000)
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))
            self.statusbar.showMessage("Failed to add points. Please check your input.", 3000)

    def update_animation(self, frame):
        """Update the animation frame"""
        if self.current_points < self.max_points:
            self.current_points += 1
            a, b = self.interval
            
            # Generate points up to current count
            x_points = np.linspace(a, b, self.current_points)
            y_points = [lf.target_function(x) for x in x_points]
            
            # Update the plot
            self.lagrange_axes.clear()
            
            # Plot target function
            x_plot = np.linspace(a, b, 1000)
            y_target = [lf.target_function(x) for x in x_plot]
            self.lagrange_axes.plot(x_plot, y_target, 'g--', label='Target Function')
            
            # Plot interpolation points
            self.lagrange_axes.scatter(x_points, y_points, color='red', label='Interpolation Points')
            
            # Plot interpolation curve
            y_interp = [lf.lagrange_interpolation(x_points, y_points, x) for x in x_plot]
            self.lagrange_axes.plot(x_plot, y_interp, 'b-', label='Lagrange Interpolation')
            
            self.lagrange_axes.grid(True)
            self.lagrange_axes.legend()
            self.lagrange_axes.set_title(f'Lagrange Interpolation (Points: {self.current_points})')
            self.lagrange_axes.set_xlabel('x')
            self.lagrange_axes.set_ylabel('y')
            
            self.lagrange_canvas.draw()
            
            # Update status
            self.statusbar.showMessage(f"Animation: {self.current_points}/{self.max_points} points", 1000)
            
            return self.lagrange_axes.artists
        return []

    def start_animation(self):
        """Start the animation"""
        if not self.lagrange_x_points:
            QMessageBox.warning(self.ui, "Warning", "Please add points first")
            return
            
        if self.animation is None:
            self.animation = FuncAnimation(
                self.lagrange_figure,
                self.update_animation,
                frames=self.max_points,
                interval=self.animation_interval,
                blit=True
            )
            self.statusbar.showMessage("Animation started", 2000)
        else:
            self.animation.event_source.start()
            self.statusbar.showMessage("Animation resumed", 2000)

    def stop_animation(self):
        """Stop the animation"""
        if self.animation is not None:
            self.animation.event_source.stop()
            self.statusbar.showMessage("Animation stopped", 2000)

    def reset_animation(self):
        """Reset the animation"""
        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
            self.current_points = 0
            self.plot_lagrange()  # Show the full plot
            self.statusbar.showMessage("Animation reset", 2000)

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
