# slider_manager.py

from PyQt5 import QtWidgets

class SliderManager:
    def __init__(self, scale_factor=1000):
        self.SLIDER_SCALE_FACTOR = scale_factor

    def setup_float_slider(self, slider_widget, min_val, max_val):
        """Configures a QSlider to represent float values using a scaling factor."""
        slider_widget.setMinimum(int(min_val * self.SLIDER_SCALE_FACTOR))
        slider_widget.setMaximum(int(max_val * self.SLIDER_SCALE_FACTOR))
        slider_widget.setSingleStep(1) # Smallest step in integer units
        slider_widget.setPageStep(self.SLIDER_SCALE_FACTOR) # Page step for ~1.0 unit

    def get_slider_float_value(self, slider_widget):
        """Converts the QSlider's integer value to its float representation."""
        return float(slider_widget.value()) / self.SLIDER_SCALE_FACTOR

    def set_slider_float_value(self, slider_widget, float_value):
        """Sets the QSlider's integer value based on a float representation."""
        # Ensure value is within bounds before setting
        clamped_value = max(slider_widget.minimum() / self.SLIDER_SCALE_FACTOR,
                            min(slider_widget.maximum() / self.SLIDER_SCALE_FACTOR, float_value))
        slider_widget.setValue(int(clamped_value * self.SLIDER_SCALE_FACTOR))
