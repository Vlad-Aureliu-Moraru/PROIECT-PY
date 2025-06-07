# main_app.py

import sys
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox 


from ui_proiect import Ui_MainWindow


#funct
def target_function(val):
    return math.cos(math.pi * val)


#validate_input_func

def validate_input_func(input):
    if not input.strip():
        print("INPUT ERROR (EMPTY)")

#validate_interval

def validate_interval(interval):
    if not interval.strip():
        print("INTERVAL ERROR (EMPTY)")

#import_CSV

#import_TXT

#manual_input


#calculeaza_func

def map_to_unit_interval(y, a, b):
    """
    Maps a value 'y' from an arbitrary interval [a, b] to the
    corresponding value 'x' in the unit interval [0, 1].

    Args:
        y (float): The value from the interval [a, b].
        a (float): The start of the original interval.
        b (float): The end of the original interval.

    Returns:
        float: The mapped value 'x' in [0, 1].
    """
    if a == b:
        if y == a:
            return 0.0 # Or raise an error if a degenerate interval is not allowed
        else:
            raise ValueError("Cannot map to unit interval from a degenerate interval [a, a] unless y == a.")
    
    return (y - a) / (b - a)

def map_from_unit_interval(x, a, b):
    """
    Maps a value 'x' from the unit interval [0, 1] to the
    corresponding value 'y' in an arbitrary interval [a, b].

    Args:
        x (float): The value from the unit interval [0, 1].
        a (float): The start of the target interval.
        b (float): The end of the target interval.

    Returns:
        float: The mapped value 'y' in [a, b].
    """
    return a + (b - a) * x
#aprox_berstein
def aprox_berstein(func,punct,grad):
    """
    Calculates the nth degree Bernstein approximation of a function f(x)
    on the interval [0, 1] at a specific point x.

    Args:
        f (callable): The function to be approximated. It should take a single
                      numerical argument (x) and return its value.
        x (float): The point at which to evaluate the Bernstein polynomial.
                   Must be within the interval [0, 1].
        n (int): The degree of the Bernstein polynomial (n >= 0).

    Returns:
        float: The value of the nth degree Bernstein polynomial for f(x) at point x.
               Returns 0.0 if n is 0 and f(0) is not defined, or if x is outside [0, 1].
    """
    if not (0 <=punct <= 1):
        print("Warning: x should be in the interval [0, 1] for direct Bernstein approximation.")
        return 0.0

    if grad < 0:
        raise ValueError("The degree 'n' must be a non-negative integer.")

    if grad == 0:
        return func(0)

    bernstein_sum = 0.0
    for k in range(grad + 1):
        # Binomial coefficient C(n, k)
        binomial_coeff = math.comb(grad, k) # math.comb is available from Python 3.8+

        # Bernstein basis polynomial b_k,n(x)
        bernstein_basis = (punct**k) * ((1 - punct)**(grad - k))

        # Term in the sum
        term = func(k / grad) * binomial_coeff * bernstein_basis
        bernstein_sum += term
    
    print(bernstein_sum)    
    return bernstein_sum

#compare_func

#salveaza_graph

#salveaza_anim

#set_output

#set_Error

#play_anim

#back_anim

#front_anim







class MainWindow(QtWidgets.QMainWindow):
    def calculeaza_func(self):
        print("{input}:{interval};{grad}")
        aprox_berstein(target_function,0.2,4)
    
    
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.CALCULEAZA_button.clicked.connect(self.calculeaza_func)
      #  self.ui.verticalSlider.valueChanged.connect(self.update_grad_label)
        
        self.ui.verticalSlider.setMinimum(1) 
        self.ui.verticalSlider.setMaximum(50)
        self.ui.verticalSlider.setValue(5)
        
        #self.update_grad_label(self.ui.verticalSlider.value())

        self.ui.OUTPUT_textfield.setReadOnly(True)
        self.ui.statusbar.showMessage("Ready to calculate Bernstein approximation.", 3000)

   
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    window = MainWindow() 
    window.show()
    
    sys.exit(app.exec_())