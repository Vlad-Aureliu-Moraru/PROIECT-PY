# plot_handler.py

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from PyQt5 import QtWidgets

import BersteinFunctions as bnf

class PlotHandler:
    def __init__(self, parent_widget, initial_interval_a, initial_interval_b):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, parent_widget)

        self.graph_layout = QtWidgets.QVBoxLayout(parent_widget)
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)

        self.interval_1 = initial_interval_a
        self.interval_2 = initial_interval_b
        self.original_line = None # Will store the Line2D object for the original function
        self.approx_line = None   # Will store the Line2D object for the approximation

        self.animation = None
        self.is_animating = False
        self.anim_interval_ms = 100

    def set_interval(self, a, b):
        self.interval_1 = a
        self.interval_2 = b

    def plot_approximation(self, n_degree, num_points=200):
        self.axes.cla()
        a = self.interval_1
        b = self.interval_2

        y_values = np.linspace(a, b, num_points)
        original_func_values = [bnf.target_function(y) for y in y_values]
        bernstein_approx_values = [bnf.aprox_berstein_on_interval(bnf.target_function, y, n_degree, a, b) for y in y_values]

        self.original_line, = self.axes.plot(y_values, original_func_values, label='Functia Originala $f(y)$', color='blue', linestyle='-')
        self.approx_line, = self.axes.plot(y_values, bernstein_approx_values, label=f'Aproximare Bernstein ($n={n_degree}$)', color='red', linestyle='--')

        self.axes.set_title(f"Aproximare Bernstein pe intervalul $[{a:.2f}, {b:.2f}]$ (Grad $n={n_degree}$)")
        self.axes.set_xlabel("y")
        self.axes.set_ylabel("$f(y)$ / Aproximare")
        self.axes.legend()
        self.axes.grid(True)
        self.axes.axvline(a, color='gray', linestyle=':', linewidth=0.8, label=f'Inceput Interval ({a:.2f})')
        self.axes.axvline(b, color='gray', linestyle=':', linewidth=0.8, label=f'Sfarsit Interval ({b:.2f})')

        self.canvas.draw()
        return self.approx_line, self.original_line # Return lines for blitting

    def _update_animation_frame(self, frame_degree):
        """
        Internal method for FuncAnimation to update plot data.
        This is called by FuncAnimation, not directly by MainWindow.
        """
        a = self.interval_1
        b = self.interval_2
        y_values = np.linspace(a, b, 200)
        bernstein_approx_values = [bnf.aprox_berstein_on_interval(bnf.target_function, y, frame_degree, a, b) for y in y_values]

        self.approx_line.set_ydata(bernstein_approx_values)
        self.approx_line.set_label(f'Aproximare Bernstein ($n={frame_degree}$)')

        if self.axes.get_legend():
             self.axes.get_legend().remove()
        self.axes.legend()
        self.axes.set_title(f"Aproximare Bernstein pe intervalul $[{a:.2f}, {b:.2f}]$ (Grad $n={frame_degree}$)")

        return self.approx_line, self.original_line, # Return all artists that need blitting

    def start_animation(self, min_degree, max_degree):
        if self.is_animating:
            return
        self.is_animating = True
        self.plot_approximation(n_degree=min_degree) # Plot initial frame for blitting setup

        self.animation = FuncAnimation(
            self.figure,
            self._update_animation_frame,
            frames=range(min_degree, max_degree + 1),
            interval=self.anim_interval_ms,
            blit=True,
            repeat=False
        )
        self.canvas.draw_idle()

    def stop_animation(self):
        if self.animation:
           # self.animation.event_source.stop()
            self.animation = None
            self.is_animating = False
        else:
            self.axes.cla()

