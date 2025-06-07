

import math
import numpy as np # NumPy is excellent for creating arrays of numbers and for mathematical operations
def map_to_unit_interval(y, a, b):
  
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
def aprox_berstein_on_interval(original_func, y_eval, n_degree, a, b):
    """
    Calculates the nth degree Bernstein approximation of an original_func(y)
    on an arbitrary interval [a, b] at a specific point y_eval.

    Args:
        original_func (callable): The function to be approximated, defined on [a, b].
                                  It should take a single numerical argument (y) and return its value.
        y_eval (float): The point in the interval [a, b] at which to evaluate
                        the Bernstein polynomial.
        n_degree (int): The degree of the Bernstein polynomial (n_degree >= 0).
        a (float): The start of the interval [a, b].
        b (float): The end of the interval [a, b].

    Returns:
        float: The value of the nth degree Bernstein polynomial for original_func(y)
               at point y_eval on the interval [a, b].
    """
    if a >= b:
        raise ValueError("Interval start 'a' must be less than interval end 'b'.")

    if not (a <= y_eval <= b):
        print(f"Warning: y_eval ({y_eval}) is outside the interval [{a}, {b}]. "
              f"The approximation might be less accurate outside the defined interval.")
        # You might choose to raise an error here instead of a warning.

    # 1. Transform the evaluation point from [a, b] to [0, 1]
    # This 'x_transformed_eval' is the 'punct' for the internal Bernstein calculation.
    x_transformed_eval = map_to_unit_interval(y_eval, a, b)

    # 2. Define an *inner* function that maps a point from [0, 1] back to [a, b]
    # before calling the original function.
    def transformed_func_for_bernstein(x_unit):
        # Map the unit interval point 'x_unit' back to the original interval [a, b]
        y_original = map_from_unit_interval(x_unit, a, b)
        # Evaluate the original function at this mapped point
        return original_func(y_original)

    # Now, the rest of the logic is similar to your original aprox_berstein,
    # but it uses 'transformed_func_for_bernstein' and 'x_transformed_eval'.

    if n_degree < 0:
        raise ValueError("The degree 'n_degree' must be a non-negative integer.")

    if n_degree == 0:
        # For n=0, the approximation is just the function value at the start of the interval.
        # This corresponds to evaluating original_func(a)
        # which is equivalent to transformed_func_for_bernstein(0)
        return transformed_func_for_bernstein(0.0) # Using 0.0 because it's from unit interval

    bernstein_sum = 0.0
    for k in range(n_degree + 1):
        # Binomial coefficient C(n, k)
        binomial_coeff = math.comb(n_degree, k)

        # Bernstein basis polynomial b_k,n(x_transformed_eval)
        bernstein_basis = (x_transformed_eval**k) * ((1 - x_transformed_eval)**(n_degree - k))

        # IMPORTANT: Call the 'transformed_func_for_bernstein' here
        # It takes k/n_degree (which is in [0,1]) and maps it to [a,b] for 'original_func'
        term = transformed_func_for_bernstein(k / n_degree) * binomial_coeff * bernstein_basis
        bernstein_sum += term

    # print(bernstein_sum) # You might want to remove this print in the final version
    print(bernstein_sum)
    return bernstein_sum
