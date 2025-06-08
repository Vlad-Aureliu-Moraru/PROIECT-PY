# ui_helpers.py

import re
from PyQt5.QtWidgets import QMessageBox

class UIHelpers:
    def __init__(self, slider_scale_factor=100):
        self.SLIDER_SCALE_FACTOR = slider_scale_factor

    def setup_float_slider(self, slider_widget, min_val, max_val):
        """Configures a QSlider to represent float values using a scaling factor."""
        slider_widget.setMinimum(int(min_val * self.SLIDER_SCALE_FACTOR))
        slider_widget.setMaximum(int(max_val * self.SLIDER_SCALE_FACTOR))
        slider_widget.setSingleStep(1)
        slider_widget.setPageStep(self.SLIDER_SCALE_FACTOR)

    def get_slider_float_value(self, slider_widget):
        """Converts the QSlider's integer value to its float representation."""
        return float(slider_widget.value()) / self.SLIDER_SCALE_FACTOR

    def set_slider_float_value(self, slider_widget, float_value):
        """Sets the QSlider's integer value based on a float representation."""
        clamped_value = max(slider_widget.minimum() / self.SLIDER_SCALE_FACTOR,
                            min(slider_widget.maximum() / self.SLIDER_SCALE_FACTOR, float_value))
        slider_widget.setValue(int(clamped_value * self.SLIDER_SCALE_FACTOR))

    def parse_interval_string(self, interval_str, parent_window):
        """Parses an interval string [a,b] and returns (a, b) floats or None on error."""
        # Corrected regex to handle floats and optional spaces, exactly as discussed.
        intervalRegEx = r"^\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]$"
        match = re.fullmatch(intervalRegEx, interval_str)

        if not match:
            QMessageBox.warning(parent_window, "Eroare Intrare",
                                  "Introduceti intervalul in formatul [start,end], "
                                  "ex: [-1.5, 10] sau [0, 5].")
            return None, None

        try:
            parsed_interval_1 = float(match.group(1))
            parsed_interval_2 = float(match.group(2))

            if parsed_interval_1 >= parsed_interval_2:
                QMessageBox.warning(parent_window, "Interval Invalid", "Inceputul intervalului trebuie sa fie strict mai mic decat sfarsitul.")
                return None, None

            return parsed_interval_1, parsed_interval_2
        except ValueError as e:
            QMessageBox.critical(parent_window, "Eroare de Parsare", f"Eroare la conversia numerelor intervalului: {e}")
            return None, None
        except Exception as e:
            QMessageBox.critical(parent_window, "Eroare Neasteptata", f"A aparut o eroare neasteptata: {e}")
            return None, None
