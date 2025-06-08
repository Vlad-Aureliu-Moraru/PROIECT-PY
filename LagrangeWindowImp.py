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
        self.animation_interval = 500
        
        self.setup_ui()
        
    def setup_ui(self):
        self.ui.IL_TABEL.setColumnCount(2)
        self.ui.IL_TABEL.setHorizontalHeaderLabels(['X', 'Y'])
        self.setup_lagrange_graph()
        self.ui.IL_BUTTON_ADAUGA.clicked.connect(self.add_lagrange_point)
        self.ui.IL_BUTTON_PLAY.clicked.connect(self.start_animation)
        self.ui.IL_BUTTON_PREV.clicked.connect(self.stop_animation)
        self.ui.IL_BUTTON_NEXT.clicked.connect(self.reset_animation)

    def setup_lagrange_graph(self):
        self.lagrange_figure = Figure(figsize=(5, 4), dpi=100)
        self.lagrange_axes = self.lagrange_figure.add_subplot(111)
        self.lagrange_canvas = FigureCanvas(self.lagrange_figure)
        self.lagrange_toolbar = NavigationToolbar(self.lagrange_canvas, self.parent_widget)
        
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
                raise ValueError("Introdu Numarul De Noduri")
            
            num_nodes = int(num_nodes_text)
            if num_nodes <= 0:
                raise ValueError("Numarul de noduri trebuie sa fie pozitiv")
            
            interval_text = self.ui.IL_TEXTFIELD_INTERVAL.text().strip()
            if not interval_text:
                raise ValueError("introdu intervalul")
                
            interval_match = re.match(r'\[(\d+),(\d+)\]', interval_text)
            if not interval_match:
                raise ValueError("format invalid")
            
            a, b = map(int, interval_match.groups())
            if a >= b:
                raise ValueError("Startul trebuie sa fie > ca Endul")
            
            self.interval = (a, b)
            self.max_points = num_nodes
            self.current_points = 0
            
            x_points = np.linspace(a, b, num_nodes)
            y_points = [lf.target_function(x) for x in x_points]
            
            self.lagrange_x_points = []
            self.lagrange_y_points = []
            self.ui.IL_TABEL.setRowCount(0)
            
            for x, y in zip(x_points, y_points):
                self.lagrange_x_points.append(x)
                self.lagrange_y_points.append(y)
                row = self.ui.IL_TABEL.rowCount()
                self.ui.IL_TABEL.insertRow(row)
                self.ui.IL_TABEL.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{x:.4f}"))
                self.ui.IL_TABEL.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{y:.4f}"))
            
            x_eval = (a + b) / 2
            interpolated_value = lf.lagrange_interpolation(self.lagrange_x_points, self.lagrange_y_points, x_eval)
            actual_value = lf.target_function(x_eval)
            
            max_error = lf.calculate_interpolation_error(self.lagrange_x_points, self.lagrange_y_points)
            
            self.ui.IL_TEXTFIELD_OUTPUT.setText(f"Val Interpolarii: {interpolated_value:.6f} |Functia in py: {actual_value:.6f}")
            self.ui.IL_TEXTFIELD_ERROR.setText(f"{max_error:.6f}")
            
            self.plot_lagrange()
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))

    def update_animation(self, frame):
        if self.current_points < self.max_points:
            self.current_points += 1
            a, b = self.interval
            
            x_points = np.linspace(a, b, self.current_points)
            y_points = [lf.target_function(x) for x in x_points]
            
            self.lagrange_axes.clear()
            
            x_plot = np.linspace(a, b, 1000)
            y_target = [lf.target_function(x) for x in x_plot]
            self.lagrange_axes.plot(x_plot, y_target, 'g--', label='Functia Originala')
            
            self.lagrange_axes.scatter(x_points, y_points, color='red', label='Punctele de interpolare')
            
            y_interp = [lf.lagrange_interpolation(x_points, y_points, x) for x in x_plot]
            self.lagrange_axes.plot(x_plot, y_interp, 'b-', label='Interpolarea Lagrange')
            
            self.lagrange_axes.grid(True)
            self.lagrange_axes.legend()
            self.lagrange_axes.set_title(f'Interpolarea Lagrange (puncte: {self.current_points})')
            self.lagrange_axes.set_xlabel('x')
            self.lagrange_axes.set_ylabel('y')
            
            self.lagrange_canvas.draw()
            
            return self.lagrange_axes.artists
        return []

    def start_animation(self):
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
        else:
            self.animation.event_source.start()

    def stop_animation(self):
        if self.animation is not None:
            self.animation.event_source.stop()

    def reset_animation(self):
        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
            self.current_points = 0
            self.plot_lagrange()  

    def plot_lagrange(self):
        try:
            if not self.lagrange_x_points:
                raise ValueError("No points available for interpolation. Please add points first.")
            
            fig, ax = lf.plot_lagrange_interpolation(
                self.lagrange_x_points,
                self.lagrange_y_points
            )
            
            self.lagrange_axes.clear()
            self.lagrange_axes.plot(ax.lines[0].get_xdata(), ax.lines[0].get_ydata(), 'b-', label='Interpolarea Lagrange')
            self.lagrange_axes.scatter(self.lagrange_x_points, self.lagrange_y_points, color='red', label='Punctele Interpolarii')
            self.lagrange_axes.plot(ax.lines[1].get_xdata(), ax.lines[1].get_ydata(), 'g--', label='Functia in py')
            self.lagrange_axes.grid(True)
            self.lagrange_axes.legend()
            self.lagrange_axes.set_title('Interpolarea Lagrange')
            self.lagrange_axes.set_xlabel('x')
            self.lagrange_axes.set_ylabel('y')
            
            self.lagrange_canvas.draw()
            
        except ValueError as e:
            QMessageBox.warning(self.ui, "Error", str(e))
