
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
import BersteinFunctions as bnf
from matplotlib.animation import FuncAnimation # Import FuncAnimation
import numpy as np # NumPy is excellent for creating arrays of numbers and for mathematical operations


class MainWindow(QtWidgets.QMainWindow):
    def _plot_approximation(self, num_points=200):
        """
        Internal method to clear and redraw the Matplotlib graph based on current parameters.
        This is called whenever relevant parameters (interval, degree) change.
        """
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
        # Using a list comprehension for efficiency here.
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
        punct=self.ui.AB_SLIDER_PUNCT.value()/100
        grad = self.ui.AB_SLIDER.value()
        
        print(f"{punct}:{self.interval_1};{grad}")
        bnf.aprox_berstein_on_interval(bnf.target_function,punct,grad,self.interval_1,self.interval_2)
        print(f"real value {bnf.target_function(punct)}")
        self._plot_approximation()
    
    def set_interval(self):
        intervalRegEx = r"^\[\d+,\d+\]$"
        interval = self.ui.AB_INPUT_INTERVAL.text();
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
    
    def update_grad_label(self,value):
        self.ui.AB_LABEL_GRAD.setText(f"GRAD:{value}")
    
    def update_punct_label(self,value):
        self.ui.AB_LABEL_PUNCT.setText(f"Punct:{value/100}")

    def start_animation(self):
        """Starts the animation of the Bernstein approximation."""
        print("ANIMATION")
        if self.is_animating:
            return # Animation already running

        self.ui.statusbar.showMessage("Starting animation...", 2000)
        self.is_animating = True

        # Ensure initial plot for blitting setup
        self._plot_approximation(fixed_degree=self.current_anim_degree)

        # Create the animation object
        # frames: degrees from min to max slider value
        # interval: delay between frames in ms
        # blit: true for smoother animation (only redraws changing parts)
        # repeat: whether the animation should loop
        self.animation = FuncAnimation(
            self.figure,
            self._update_animation_frame,
            frames=range(self.ui.AB_SLIDER.minimum(), self.ui.AB_SLIDER.maximum() + 1),
            interval=self.anim_interval_ms,
            blit=True,
            repeat=False # Set to True if you want it to loop
        )
        self.canvas.draw_idle() # Redraw once to ensure animation starts correctly
    def __init__(self):
        super().__init__()
        self.interval_1= 0.0;
        self.interval_2 = 1.0;
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

        # 5. Add the canvas and toolbar to your UI's graph placeholder widget.
        # Ensure you have a QWidget in your .ui file named 'graph_container_widget'
        # or similar, which acts as the parent for the graph.
        # The line below assumes `self.ui.graph_container_widget` exists.
        self.graph_layout = QtWidgets.QVBoxLayout(self.ui.AB_WIG_GRAF)
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)


 # --- Animation Specific Attributes ---
        self.animation = None         # Stores the FuncAnimation object
        self.is_animating = False     # Flag to track animation state
        self.current_anim_degree = self.ui.AB_SLIDER.minimum() # Start degree for animation
        self.max_anim_degree = self.ui.AB_SLIDER.maximum()   # End degree for animation
        self.anim_interval_ms = 100   # Milliseconds between frames (adjust for speed)
# Connect animation buttons (assuming these exist in your UI)
        # You'll need to add QPushButtons with these objectNames in Qt Designer
        self.ui.AB_BUTTON_PLAY.clicked.connect(self.start_animation)
       #self.ui.ANIM_PAUSE_button.clicked.connect(self.pause_animation)
       # self.ui.ANIM_STOP_button.clicked.connect(self.stop_animation)




        self.ui.AB_BUTTON_CALCULEAZA.clicked.connect(self.calculeaza_func)
        self.ui.AB_SLIDER.valueChanged.connect(self.update_grad_label)
        self.ui.AB_SLIDER_PUNCT.valueChanged.connect(self.update_punct_label)

        self.ui.AB_BUTTON_INTERVAL.clicked.connect(self.set_interval)
        self.ui.AB_SLIDER.setMinimum(1) 
        self.ui.AB_SLIDER.setMaximum(50)
        self.ui.AB_SLIDER.setValue(5)
        self.ui.AB_SLIDER_PUNCT.setMinimum(0)
        self.ui.AB_SLIDER_PUNCT.setMaximum(1*self.SLIDER_SCALE_FACTOR)
        self.update_grad_label(self.ui.AB_SLIDER.value())

        self.ui.OUTPUT_textfield.setReadOnly(True)
        self.ui.statusbar.showMessage("Ready to calculate Bernstein approximation.", 3000)
   
