# main_window.py

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from ui_proiect import Ui_MainFrame
import BersteinFunctions as bnf # Your existing math functions

# Import the new modules
from plot_handler import PlotHandler
from ui_helpers import UIHelpers


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainFrame()
        self.ui.setupUi(self)

        self.interval_1 = 0.0
        self.interval_2 = 1.0

        # Initialize helper modules
        self.plot_handler = PlotHandler(self.ui.AB_WIG_GRAF, self.interval_1, self.interval_2)
        self.ui_helpers = UIHelpers(slider_scale_factor=100) # Use your original scale factor of 100

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
        #self.plot_handler.stop_animation()

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
