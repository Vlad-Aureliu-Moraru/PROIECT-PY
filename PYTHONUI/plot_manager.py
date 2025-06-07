# plot_manager.py

import numpy as np
import matplotlib.pyplot as plt # Needed for general plot settings, though not explicitly plt.show()

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtWidgets

import BersteinFunctions as bnf # Import your functions module

class PlotManager:
    def __init__(self, parent_widget, initial_interval_a, initial_interval_b):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, parent_widget) # Toolbar needs a parent widget

        # Add the canvas and toolbar to the provided parent_widget's layout
        self.graph_layout = QtWidgets.QVBoxLayout(parent_widget)
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)

        self.original_line = None # Will store the Line2D object for the original function
        self.approx_line = None   # Will store the Line2D object for the approximation

        # Initial interval for plotting
        self.a = initial_interval_a
        self.b = initial_interval_b

    def set_interval(self, a, b):
        self.a = a
        self.b = b

    def plot_approximation(self, n_degree, punct_eval=None, num_points=200):
        """
        Clears and redraws the Matplotlib graph.
        n_degree: The degree of the Bernstein polynomial to plot.
        punct_eval: An optional specific point to highlight on the graph.
        """
        self.axes.cla() # Clear the previous plot content

        y_values = np.linspace(self.a, self.b, num_points)
        original_func_values = [bnf.target_function(y) for y in y_values]

        # Calculate Bernstein approximation values
        bernstein_approx_values = [bnf.aprox_berstein_on_interval(bnf.target_function, y, n_degree, self.a, self.b) for y in y_values]

        # Plot the data
        # Store the line objects for potential blitting in animation or just for direct updates
        self.original_line, = self.axes.plot(y_values, original_func_values, label='Functia Originala $f(y)$', color='blue', linestyle='-')
        self.approx_line, = self.axes.plot(y_values, bernstein_approx_values, label=f'Aproximare Bernstein ($n={n_degree}$)', color='red', linestyle='--')

        # Add labels, title, and legend for clarity
        self.axes.set_title(f"Aproximare Bernstein pe intervalul $[{self.a:.2f}, {self.b:.2f}]$ (Grad $n={n_degree}$)")
        self.axes.set_xlabel("y")
        self.axes.set_ylabel("$f(y)$ / Aproximare")
        self.axes.legend()
        self.axes.grid(True)

        # Add vertical lines to clearly mark the interval boundaries
        self.axes.axvline(self.a, color='gray', linestyle=':', linewidth=0.8, label=f'Inceput Interval ({self.a:.2f})')
        self.axes.axvline(self.b, color='gray', linestyle=':', linewidth=0.8, label=f'Sfarsit Interval ({self.b:.2f})')

        # Highlight the evaluation point if provided
        if punct_eval is not None and self.a <= punct_eval <= self.b:
            f_val = bnf.target_function(punct_eval)
            approx_val = bnf.aprox_berstein_on_interval(bnf.target_function, punct_eval, n_degree, self.a, self.b)
            self.axes.plot(punct_eval, f_val, 'go', markersize=8, label='Punct Original') # Green dot for original
            self.axes.plot(punct_eval, approx_val, 'rx', markersize=8, label='Punct Aproximat') # Red 'x' for approximated
            self.axes.legend() # Update legend with new markers

        self.canvas.draw()
        # Return the lines for potential blitting if this method is also used for animation updates
        return self.approx_line, self.original_line

    def update_plot_data(self, n_degree, num_points=200):
        """
        Updates the data of existing plot lines for animation, without clearing the axes.
        Returns the artists that were modified for blitting.
        """
        y_values = np.linspace(self.a, self.b, num_points)
        bernstein_approx_values = [bnf.aprox_berstein_on_interval(bnf.target_function, y, n_degree, self.a, self.b) for y in y_values]

        # Update the data of the existing line object
        self.approx_line.set_ydata(bernstein_approx_values)
        self.approx_line.set_label(f'Aproximare Bernstein ($n={n_degree}$)') # Update label

        # Update the title and legend
        self.axes.set_title(f"Aproximare Bernstein pe intervalul $[{self.a:.2f}, {self.b:.2f}]$ (Grad $n={n_degree}$)")
        if self.axes.get_legend():
             self.axes.get_legend().remove() # Remove old legend
        self.axes.legend() # Recreate new legend

        return self.approx_line, self.original_line, # Return all artists that need blitting (tuple)
