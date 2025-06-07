# main_window.py

import re
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

# Import your generated UI class
from ui_proiect import Ui_MainFrame

# Import your helper managers
import BersteinFunctions as bnf
from plot_manager import PlotManager
from slider_manager import SliderManager
from animation_manager import AnimationManager

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainFrame()
        self.ui.setupUi(self)

        # Initialize core interval variables
        self.interval_1 = 0.0
        self.interval_2 = 1.0

        # --- Initialize Managers ---
        self.plot_manager = PlotManager(self.ui.AB_WIG_GRAF, self.interval_1, self.interval_2)
        self.slider_manager = SliderManager(scale_factor=1000) # Use the same scale factor

        # Animation manager will be initialized later when frames range is known (from slider)
        self.animation_manager = None

        # --- UI Element Setup ---
        # Set up the 'grad' (degree) slider
        self.ui.AB_SLIDER.setMinimum(1)
        self.ui.AB_SLIDER.setMaximum(50)
        self.ui.AB_SLIDER.setValue(5) # Default degree

        # Set up the 'punct' slider for float values using the slider manager
        self.slider_manager.setup_float_slider(self.ui.AB_SLIDER_PUNCT, self.interval_1, self.interval_2)
        self.slider_manager.set_slider_float_value(self.ui.AB_SLIDER_PUNCT, (self.interval_1 + self.interval_2) / 2)

        # --- Connect Signals to Slots ---
        self.ui.AB_BUTTON_CALCULEAZA.clicked.connect(self.calculeaza_func)
        self.ui.AB_SLIDER.valueChanged.connect(self.update_grad_label)
        self.ui.AB_SLIDER_PUNCT.valueChanged.connect(self.update_punct_label)
        self.ui.AB_BUTTON_INTERVAL.clicked.connect(self.set_interval)

        # Connect animation buttons
        self.ui.AB_BUTTON_PLAY.clicked.connect(self.start_animation)
        # Assuming you add these buttons in your UI
        self.ui.AB_BUTTON_PREV.clicked.connect(self.pause_animation)
        self.ui.AB_BUTTON_NEXT.clicked.connect(self.stop_animation)


        # --- Initial UI State ---
        self.update_grad_label(self.ui.AB_SLIDER.value())
        self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value())
        self.ui.OUTPUT_textfield.setReadOnly(True)
        self.ui.statusbar.showMessage("Gata de calcularea aproximarii Bernstein.", 3000)

        # Initial static plot
        self.plot_manager.plot_approximation(self.ui.AB_SLIDER.value())


    # --- UI Event Handlers ---
    def calculeaza_func(self):
        self.stop_animation() # Stop any active animation

        punct = self.slider_manager.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
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

        # Plot the result, highlighting the point
        self.plot_manager.plot_approximation(n_degree=grad, punct_eval=punct)


    def set_interval(self):
        self.stop_animation() # Stop animation if interval changes

        intervalRegEx = r"^\[\d+,d+\]$"
        interval_str = self.ui.AB_INPUT_INTERVAL.text()
        match = re.fullmatch(intervalRegEx, interval_str)

        if not match:
            QMessageBox.warning(self, "Eroare Intrare",
                                  "Introduceti intervalul in formatul [start,end], "
                                  "ex: [-1.5, 10] sau [0, 5].")
            self.ui.statusbar.showMessage("Format interval invalid!", 3000)
            return

        try:
            parsed_interval_1 = float(match.group(1))
            parsed_interval_2 = float(match.group(2))

            if parsed_interval_1 >= parsed_interval_2:
                QMessageBox.warning(self, "Interval Invalid", "Inceputul intervalului trebuie sa fie strict mai mic decat sfarsitul.")
                self.ui.statusbar.showMessage("Inceput interval >= sfarsit!", 3000)
                return

            self.interval_1 = parsed_interval_1
            self.interval_2 = parsed_interval_2

            # Update the plot manager's interval
            self.plot_manager.set_interval(self.interval_1, self.interval_2)

            print(f"Interval set to: [{self.interval_1:.2f}, {self.interval_2:.2f}]")
            self.ui.statusbar.showMessage(f"Interval set to [{self.interval_1:.2f}, {self.interval_2:.2f}]", 3000)

            # Update the 'punct' slider's range based on the new float interval
            self.slider_manager.setup_float_slider(self.ui.AB_SLIDER_PUNCT, self.interval_1, self.interval_2)
            self.update_punct_label(self.ui.AB_SLIDER_PUNCT.value()) # Update label immediately

            # Re-plot the graph with the new interval
            self.plot_manager.plot_approximation(self.ui.AB_SLIDER.value())

        except ValueError as e:
            QMessageBox.critical(self, "Eroare de Parsare", f"Eroare la conversia numerelor intervalului: {e}")
            self.ui.statusbar.showMessage("Eroare la parsarea numerelor!", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Eroare Neasteptata", f"A aparut o eroare neasteptata: {e}")
            self.ui.statusbar.showMessage("A aparut o eroare neasteptata!", 3000)

    # --- Slider Label Update Functions ---
    def update_grad_label(self, value):
        self.ui.AB_LABEL_GRAD.setText(f"GRAD: {value}")

    def update_punct_label(self, value):
        float_value = self.slider_manager.get_slider_float_value(self.ui.AB_SLIDER_PUNCT)
        self.ui.AB_LABEL_PUNCT.setText(f"Punct: {float_value:.3f}")

    # --- Animation Control Methods ---
    def start_animation(self):
        self.ui.statusbar.showMessage("Pornire animatie...", 2000)
        if self.animation_manager is None or not self.animation_manager.is_running:
            # Initialize animation manager if not already, or after a stop
            frames_range = range(self.ui.AB_SLIDER.minimum(), self.ui.AB_SLIDER.maximum() + 1)
            self.animation_manager = AnimationManager(
                self.plot_manager.figure,
                self.plot_manager.update_plot_data, # Pass the update method of PlotManager
                frames_range,
                interval_ms=100
            )
            self.animation_manager.start()
        else:
            self.animation_manager.start() # If paused, resume
        print("Animation started/resumed.")


    def pause_animation(self):
        if self.animation_manager:
            #self.animation_manager.pause()
            self.ui.statusbar.showMessage("Animatie intrerupta.", 2000)
            print("Animation paused.")

    def stop_animation(self):
        if self.animation_manager:
            #self.animation_manager.stop()
            self.ui.statusbar.showMessage("Animatie oprita.", 2000)
            print("Animation stopped.")
            # Re-plot a static graph after stopping
            self.plot_manager.plot_approximation(self.ui.AB_SLIDER.value())
        else:
            self.animation_manager.cle()
