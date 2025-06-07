# main_app.py

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox # Import QMessageBox for pop-up messages

# Import the generated UI class from your ui_proiect.py file
# Make sure ui_proiect.py is in the same directory or accessible via PYTHONPATH
from ui_proiect import Ui_MainWindow

import numpy as np
from scipy.special import binom
from sympy import sympify, symbols
from sympy.utilities.lambdify import lambdify # Crucial for numerical evaluation with numpy

# Matplotlib imports for plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# --- Custom Matplotlib Canvas Widget ---
# This class manages the Matplotlib figure and axes for plotting within PyQt.
class MplCanvas(FigureCanvasQTAgg):
    """
    A custom Matplotlib canvas for embedding into a PyQt5 application.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111) # 111 means 1 row, 1 column, first subplot
        
        super().__init__(self.fig)
        self.setParent(parent) 

        FigureCanvasQTAgg.setSizePolicy(self,
                                        QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def plot_data(self, x_eval_points, approximated_y_values, original_y_values):
        """
        Plots the approximation and original function data.
        """
        self.axes.clear() # Clear existing plot to draw a new one
        
        # Plot the original function
        self.axes.plot(x_eval_points, original_y_values, label='Original Function', color='blue', linestyle='-')
        
        # Plot the Bernstein approximation
        self.axes.plot(x_eval_points, approximated_y_values, label='Bernstein Approximation', color='red', linestyle='--')
        
        # Add labels, title, and legend
        self.axes.set_title('Bernstein Approximation vs. Original Function')
        self.axes.set_xlabel('x')
        self.axes.set_ylabel('f(x)')
        self.axes.legend()
        self.axes.grid(True)
        
        self.fig.tight_layout() # Adjust layout to prevent labels/titles from overlapping
        self.draw() # Redraw the canvas to update the plot

# --- Helper Functions for Bernstein Approximation ---
# These functions are defined globally as they are not specific to the MainWindow instance.
def bernstein_polynomial_on_0_1(f_callable, n, x_values):
    """
    Calculates the Bernstein polynomial for a function f on the interval [0, 1].
    Args:
        f_callable: A callable function f(t) (created with lambdify, handles scalar or numpy arrays).
        n: The degree of the Bernstein polynomial.
        x_values: A numpy array of x values (between 0 and 1) at which to evaluate B_n(f;x).
    Returns:
        A numpy array of the approximated y values.
    """
    approximated_y_values = np.zeros_like(x_values, dtype=float)

    for k in range(n + 1):
        f_k_n = f_callable(k / n)
        binom_coeff = binom(n, k)
        
        basis_polynomial_terms = binom_coeff * (x_values**k) * ((1 - x_values)**(n - k))
        approximated_y_values += f_k_n * basis_polynomial_terms
        
    return approximated_y_values

def bernstein_approximation_general_interval(function_str, a, b, n, num_points=200):
    """
    Calculates the Bernstein approximation of a function f(x) on a general interval [a, b].
    Args:
        function_str: The string representation of the function f(x) (e.g., "sin(x)").
        a: The start of the interval.
        b: The end of the interval.
        n: The degree of the Bernstein polynomial.
        num_points: Number of points to evaluate the approximation on within [a, b].
    Returns:
        tuple: A tuple containing:
            - x_eval_points: A numpy array of x values within [a, b].
            - approximated_y_values: A numpy array of the approximated y values.
            - original_y_values: A numpy array of the original function's y values.
            - parsed_function: The callable numerical function.
    Raises:
        ValueError: If the interval is invalid (a >= b) or degree is non-positive.
        TypeError: If the function string cannot be parsed or lambdified.
    """
    if a >= b:
        raise ValueError("Interval start 'a' must be less than 'b'.")
    if n <= 0:
        raise ValueError("The degree 'n' must be a positive integer.")
    
    x_symbol = symbols('x')
    t_symbol = symbols('t') 

    try:
        f_expr = sympify(function_str)
        f_original_callable = lambdify(x_symbol, f_expr, 'numpy') 
    except Exception as e:
        raise TypeError(f"Could not parse function string '{function_str}' or create numerical function: {e}")

    transformed_x_expr = a + t_symbol * (b - a)
    F_expr = f_expr.subs(x_symbol, transformed_x_expr)
    
    F_callable = lambdify(t_symbol, F_expr, 'numpy')
    
    t_eval_points = np.linspace(0, 1, num_points)
    
    approximated_F_t_values = bernstein_polynomial_on_0_1(F_callable, n, t_eval_points)
    
    x_eval_points = a + t_eval_points * (b - a)
    
    approximated_y_values = approximated_F_t_values
    
    original_y_values = f_original_callable(x_eval_points) 
    
    return x_eval_points, approximated_y_values, original_y_values, f_original_callable


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.CALCULEAZA_button.clicked.connect(self.CalculeazaMetoda)
        self.ui.verticalSlider.valueChanged.connect(self.update_grad_label)
        
        self.ui.verticalSlider.setMinimum(1) # Set minimum to 1 for degree 'n'
        self.ui.verticalSlider.setMaximum(50)
        self.ui.verticalSlider.setValue(5)
        
        self.update_grad_label(self.ui.verticalSlider.value())

        self.ui.OUTPUT_textfield.setReadOnly(True)
        self.ui.statusbar.showMessage("Ready to calculate Bernstein approximation.", 3000)

    def CalculeazaMetoda(self):
        """
        This method is a 'slot' that will be called when CALCULEAZA_button is clicked.
        It performs input validation, Bernstein approximation, and plotting.
        """
        print("Hello from CalculeazaMetoda!")

        function_str = self.ui.Input_textfield.text()
        degree = self.ui.verticalSlider.value()
        interval_str = self.ui.Interval_textfield.text()
        
        # --- Input Validation ---
        if not function_str.strip(): 
            QMessageBox.warning(self, "Input Error", "Please enter a function f(x).") 
            self.ui.statusbar.showMessage("Function input is empty.", 3000)
            self.ui.OUTPUT_textfield.setText("ERROR: Missing Function Input")
            return
        
        if not interval_str.strip():
            QMessageBox.warning(self, "Input Error", "Please enter the interval [a, b].")
            self.ui.statusbar.showMessage("Interval input is empty.", 3000)
            self.ui.OUTPUT_textfield.setText("ERROR: Missing Interval Input")
            return
        
        print(f"Degree (n): {degree}")
        print(f"Interval: {interval_str}")
        print(f"Function: {function_str}")
        
        try:
            interval_parts = interval_str.strip('[]').split(',')
            if len(interval_parts) != 2:
                raise ValueError("Invalid interval format. Please use [a,b] (e.g., [0,1] or [-5,5]).")

            a = float(interval_parts[0].strip())
            b = float(interval_parts[1].strip())

            if a >= b:
                raise ValueError("The start of the interval 'a' must be strictly less than 'b'.")
            
            if degree <= 0: 
                raise ValueError("The degree 'n' of the polynomial must be a positive integer (n > 0).")

            self.ui.statusbar.showMessage("Inputs validated. Calculating...", 2000)
            self.ui.OUTPUT_textfield.setText("Calculation initiated...")

            # --- Perform Bernstein Approximation ---
            x_values, approx_y_values, original_y_values, parsed_func = \
                bernstein_approximation_general_interval(function_str, a, b, degree, num_points=500)

            # --- Display Results ---
            self.ui.OUTPUT_textfield.setText(f"Approximation for f(x) = '{function_str}' (degree n={degree}) on interval [{a}, {b}] computed.")
            self.ui.statusbar.showMessage("Bernstein approximation successful!", 3000)

            # Calculate and display error (e.g., Maximum Absolute Error)
            error_values = np.abs(original_y_values - approx_y_values)
            max_error = np.max(error_values)
            # FIX: Use append instead of setText to add to existing text
            self.ui.OUTPUT_textfield.setText(f"\nMax Absolute Error (L_infinity norm): {max_error:.6f}")
            
            # --- Plotting ---
            # Call the plot_data method of your promoted MplCanvas widget
            # Assuming the objectName of your promoted MplCanvas widget in Qt Designer is 'plotWidget'
            self.ui.WIDGET_field.plot_data(x_values, approximated_y_values, original_y_values) 

        except ValueError as ve:
            QMessageBox.warning(self, "Input Error", str(ve))
            self.ui.statusbar.showMessage(f"Input Error: {ve}", 5000)
            self.ui.OUTPUT_textfield.setText(f"ERROR: {ve}")
        except TypeError as te:
            QMessageBox.warning(self, "Function Parsing Error", f"Cannot parse function: {te}\n"
                                                               "Please check syntax (e.g., use 'x**2', 'sin(x)').")
            self.ui.statusbar.showMessage(f"Function Error: {te}", 5000)
            self.ui.OUTPUT_textfield.setText(f"ERROR: Function Parsing Failed - {te}")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred during calculation: {e}")
            self.ui.statusbar.showMessage(f"Critical Error: {e}", 5000)
            self.ui.OUTPUT_textfield.setText(f"CRITICAL ERROR: {e}")

    def update_grad_label(self, value):
        """
        Updates the QLabel next to the slider to show its current value.
        This function is a slot connected to the slider's valueChanged signal.
        """
        self.ui.GRAD_textfield.setText(f"GRAD: {value}")
        self.ui.statusbar.showMessage(f"Degree (n) set to: {value}", 1000)

# --- Main Application Entry Point ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow() 
    window.show()
    
    sys.exit(app.exec_())