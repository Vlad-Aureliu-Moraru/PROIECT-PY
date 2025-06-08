from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import BersteinFunctions as bnf
from animation_manager import AnimationManager

class BersteinWindowImp:
    def __init__(self, ui, statusbar, main_window):
        self.ui = ui
        self.statusbar = statusbar
        self.main_window = main_window
        self.interval_1 = 0.0
        self.interval_2 = 1.0
        self.SLIDER_SCALE_FACTOR = 100
        
        # Initialize UI elements
        self.ui.AB_SLIDER.setMinimum(1)
        self.ui.AB_SLIDER.setMaximum(50)
        self.ui.AB_SLIDER.setValue(5)
        
        # Set up the graph
        self.setup_bernstein_graph()
        
        # Connect signals
        self.ui.AB_BUTTON_CALCULEAZA.clicked.connect(self.calculeaza_func)
        self.ui.AB_SLIDER.valueChanged.connect(self.update_grad_label)
        self.ui.AB_SLIDER_PUNCT.valueChanged.connect(self.update_punct_label)
        self.ui.AB_BUTTON_INTERVAL.clicked.connect(self.set_interval)
        self.ui.AB_BUTTON_PLAY.clicked.connect(self.start_animation)
        self.ui.AB_BUTTON_PREV.clicked.connect(self.stop_animation)
        
        # Initial UI state
        self.update_grad_label(self.ui.AB_SLIDER.value())
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value())
        self.ui.OUTPUT_textfield.setReadOnly(True)
        
        # Initial plot
        self.plot_approximation(self.ui.AB_SLIDER.value())
        
        self.statusbar.showMessage("Ready to calculate Bernstein approximation.", 3000)

    def setup_bernstein_graph(self):
        """Set up the graph for Bernstein approximation"""
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self.main_window)
        
        # Add the canvas and toolbar to the UI
        self.graph_layout = QtWidgets.QVBoxLayout(self.ui.AB_WIG_GRAF)
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)
        
        # Initialize animation manager
        self.animation_manager = AnimationManager(
            self.figure,
            self.update_animation_frame,
            range(1, 51),
            interval_ms=100
        )

    def get_slider_float_value(self, slider):
        """Convert slider value to float value in the current interval"""
        slider_value = slider.value()
        return self.interval_1 + (self.interval_2 - self.interval_1) * (slider_value / self.SLIDER_SCALE_FACTOR)

    def setup_float_slider(self, slider, min_val, max_val):
        """Set up a slider to work with float values in the given range"""
        slider.setMinimum(0)
        slider.setMaximum(self.SLIDER_SCALE_FACTOR)
        slider.setValue(int(self.SLIDER_SCALE_FACTOR / 2))

    def parse_interval_string(self, interval_str):
        """Parse interval string in format [a,b]"""
        try:
            # Remove brackets and split by comma
            interval_str = interval_str.strip('[]')
            a, b = map(float, interval_str.split(','))
            if a >= b:
                QMessageBox.warning(self.main_window, "Invalid Interval", 
                                  "Start of interval must be less than end")
                return None, None
            return a, b
        except (ValueError, IndexError):
            QMessageBox.warning(self.main_window, "Invalid Format", 
                              "Please use format [a,b] where a and b are numbers")
            return None, None

    def calculeaza_func(self):
        """Calculate Bernstein approximation at the current point"""
        self.animation_manager.stop()
        punct = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        grad = self.ui.AB_SLIDER.value()
        print(f"Calculating for point: {punct:.3f}, interval: [{self.interval_1:.2f},{self.interval_2:.2f}], degree: {grad}")
        try:
            approximated_value = bnf.aprox_berstein_on_interval(
                bnf.target_function, punct, grad, self.interval_1, self.interval_2
            )
            actual_value = bnf.target_function(punct)
            self.ui.OUTPUT_textfield.setText(f"Aproximare: {approximated_value:.6f} | Valoare Reala: {actual_value:.6f}")
            self.statusbar.showMessage("Calcul efectuat cu succes!", 3000)
        except ValueError as e:
            QMessageBox.critical(self.main_window, "Eroare de Calcul", str(e))
            self.statusbar.showMessage("Calcul esuat!", 3000)
        self.plot_approximation(n_degree=grad)

    def set_interval(self):
        """Set the interval for Bernstein approximation"""
        self.animation_manager.stop()
        interval_str = self.ui.AB_INPUT_INTERVAL.text()
        parsed_interval_1, parsed_interval_2 = self.parse_interval_string(interval_str)
        if parsed_interval_1 is None or parsed_interval_2 is None:
            self.statusbar.showMessage("Format interval invalid sau valori invalide!", 3000)
            return
        self.interval_1 = parsed_interval_1
        self.interval_2 = parsed_interval_2
        print(f"Interval set to: [{self.interval_1:.2f}, {self.interval_2:.2f}]")
        self.statusbar.showMessage(f"Interval set to [{self.interval_1:.2f}, {self.interval_2:.2f}]", 3000)
        self.setup_float_slider(self.ui.AB_SLIDER_PUNCT, self.interval_1, self.interval_2)
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value())
        self.plot_approximation(self.ui.AB_SLIDER.value())

    def update_grad_label(self, value):
        """Update the degree label"""
        self.ui.AB_LABEL_GRAD.setText(f"GRAD:{value}")

    def update_punct_label(self, value):
        """Update the point label"""
        float_value = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        self.ui.AB_LABEL_PUNCT.setText(f"Punct:{float_value:.3f}")

    def plot_approximation(self, n_degree):
        """Plot the Bernstein approximation"""
        self.axes.clear()
        
        # Generate points for plotting
        x = np.linspace(self.interval_1, self.interval_2, 1000)
        y_original = [bnf.target_function(xi) for xi in x]
        y_approx = [bnf.aprox_berstein_on_interval(bnf.target_function, xi, n_degree, self.interval_1, self.interval_2) for xi in x]
        
        # Plot both functions
        self.axes.plot(x, y_original, 'b-', label='Original Function')
        self.axes.plot(x, y_approx, 'r--', label=f'Bernstein (n={n_degree})')
        
        # Add current point
        current_x = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        current_y = bnf.target_function(current_x)
        self.axes.plot(current_x, current_y, 'go', label='Current Point')
        
        self.axes.grid(True)
        self.axes.legend()
        self.axes.set_title('Bernstein Approximation')
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        self.canvas.draw()

    def update_animation_frame(self, frame):
        """Update function for animation"""
        self.axes.clear()
        n_degree = frame + 1
        
        # Generate points for plotting
        x = np.linspace(self.interval_1, self.interval_2, 1000)
        y_original = [bnf.target_function(xi) for xi in x]
        y_approx = [bnf.aprox_berstein_on_interval(bnf.target_function, xi, n_degree, self.interval_1, self.interval_2) for xi in x]
        
        # Plot both functions
        self.axes.plot(x, y_original, 'b-', label='Original Function')
        self.axes.plot(x, y_approx, 'r--', label=f'Bernstein (n={n_degree})')
        
        # Add current point
        current_x = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        current_y = bnf.target_function(current_x)
        self.axes.plot(current_x, current_y, 'go', label='Current Point')
        
        self.axes.grid(True)
        self.axes.legend()
        self.axes.set_title('Bernstein Approximation')
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        
        # Update slider value
        self.ui.AB_SLIDER.setValue(n_degree)
        
        return self.axes.get_lines() + self.axes.collections

    def start_animation(self):
        """Start the animation"""
        print("ANIMATION")
        self.statusbar.showMessage("Starting animation...", 2000)
        self.animation_manager.start()

    def stop_animation(self):
        """Stop the animation"""
        self.animation_manager.stop()
