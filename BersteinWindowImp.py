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
        
        self.ui.AB_SLIDER.setMinimum(1)
        self.ui.AB_SLIDER.setMaximum(50)
        self.ui.AB_SLIDER.setValue(5)
        
        self.setup_bernstein_graph()
        
        self.ui.AB_BUTTON_CALCULEAZA.clicked.connect(self.calculeaza_func)
        self.ui.AB_SLIDER.valueChanged.connect(self.update_grad_label)
        self.ui.AB_SLIDER_PUNCT.valueChanged.connect(self.update_punct_label)
        self.ui.AB_BUTTON_INTERVAL.clicked.connect(self.set_interval)
        self.ui.AB_BUTTON_PLAY.clicked.connect(self.start_animation)
        self.ui.AB_BUTTON_PREV.clicked.connect(self.stop_animation)
        
        self.update_grad_label(self.ui.AB_SLIDER.value())
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value())
        self.ui.OUTPUT_textfield.setReadOnly(True)
        
        self.plot_approximation(self.ui.AB_SLIDER.value())

    def setup_bernstein_graph(self):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self.main_window)
        
        self.graph_layout = QtWidgets.QVBoxLayout(self.ui.AB_WIG_GRAF)
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)
        
        self.animation_manager = AnimationManager(
            self.figure,
            self.update_animation_frame,
            range(1, 51),
            interval_ms=100
        )

    def get_slider_float_value(self, slider):
        slider_value = slider.value()
        return self.interval_1 + (self.interval_2 - self.interval_1) * (slider_value / self.SLIDER_SCALE_FACTOR)

    def setup_float_slider(self, slider, min_val, max_val):
        slider.setMinimum(0)
        slider.setMaximum(self.SLIDER_SCALE_FACTOR)
        slider.setValue(int(self.SLIDER_SCALE_FACTOR / 2))

    def parse_interval_string(self, interval_str):
        try:
            interval_str = interval_str.strip('[]')
            a, b = map(float, interval_str.split(','))
            if a >= b:
                QMessageBox.warning(self.main_window, "Interval Invalid", 
                                  "Startul trebuie sa fie > ca Sf")
                return None, None
            return a, b
        except (ValueError, IndexError):
            QMessageBox.warning(self.main_window, "Format Invalid", 
                              "Foloseste formatul [a,b]")
            return None, None

    def calculeaza_func(self):
        self.animation_manager.stop()
        punct = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        grad = self.ui.AB_SLIDER.value()
        try:
            approximated_value = bnf.aprox_berstein_on_interval(
                bnf.target_function, punct, grad, self.interval_1, self.interval_2
            )
            actual_value = bnf.target_function(punct)
            self.ui.OUTPUT_textfield.setText(f"Aproximare: {approximated_value:.6f} | Valoare implementata in Py: {actual_value:.6f}")
            self.statusbar.showMessage("Calcul efectuat cu succes!", 3000)
        except ValueError as e:
            QMessageBox.critical(self.main_window, "Eroare de Calcul", str(e))
            self.statusbar.showMessage("Calcul esuat!", 3000)
        self.plot_approximation(n_degree=grad)

    def set_interval(self):
        self.animation_manager.stop()
        interval_str = self.ui.AB_INPUT_INTERVAL.text()
        parsed_interval_1, parsed_interval_2 = self.parse_interval_string(interval_str)
        if parsed_interval_1 is None or parsed_interval_2 is None:
            self.statusbar.showMessage("Format interval invalid sau valori invalide!", 3000)
            return
        self.interval_1 = parsed_interval_1
        self.interval_2 = parsed_interval_2
        self.setup_float_slider(self.ui.AB_SLIDER_PUNCT, self.interval_1, self.interval_2)
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value())
        self.plot_approximation(self.ui.AB_SLIDER.value())

    def update_grad_label(self, value):
        self.ui.AB_LABEL_GRAD.setText(f"GRAD:{value}")

    def update_punct_label(self, value):
        float_value = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        self.ui.AB_LABEL_PUNCT.setText(f"Punct:{float_value:.3f}")

    def plot_approximation(self, n_degree):
        self.axes.clear()
        
        x = np.linspace(self.interval_1, self.interval_2, 1000)
        y_original = [bnf.target_function(xi) for xi in x]
        y_approx = [bnf.aprox_berstein_on_interval(bnf.target_function, xi, n_degree, self.interval_1, self.interval_2) for xi in x]
        
        self.axes.plot(x, y_original, 'b-', label='Functia implementata in Py')
        self.axes.plot(x, y_approx, 'r--', label=f'Bernstein (n={n_degree})')
        
        current_x = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        current_y = bnf.target_function(current_x)
        self.axes.plot(current_x, current_y, 'go', label='Punct Ales')
        
        self.axes.grid(True)
        self.axes.legend()
        self.axes.set_title('Aproximare Berstein')
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        self.canvas.draw()

    def update_animation_frame(self, frame):
        self.axes.clear()
        n_degree = frame + 1
        
        x = np.linspace(self.interval_1, self.interval_2, 1000)
        y_original = [bnf.target_function(xi) for xi in x]
        y_approx = [bnf.aprox_berstein_on_interval(bnf.target_function, xi, n_degree, self.interval_1, self.interval_2) for xi in x]
        
        self.axes.plot(x, y_original, 'b-', label='Functia implementata in Py')
        self.axes.plot(x, y_approx, 'r--', label=f'Bernstein (n={n_degree})')
        
        current_x = self.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        current_y = bnf.target_function(current_x)
        self.axes.plot(current_x, current_y, 'go', label='Punct Ales')
        
        self.axes.grid(True)
        self.axes.legend()
        self.axes.set_title('Aproximare Berstein')
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('y')
        
        self.ui.AB_SLIDER.setValue(n_degree)
        
        return self.axes.get_lines() + self.axes.collections

    def start_animation(self):
        print("ANIMATION")
        self.animation_manager.start()

    def stop_animation(self):
        self.animation_manager.stop()
