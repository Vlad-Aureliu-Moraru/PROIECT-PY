import math
import numpy as np 

def target_function(val):
    return math.cos(math.pi * val)

def map_to_unit_interval(y, a, b):
    if a == b:
        if y == a:
            return 0.0 
        else:
            raise ValueError("ERROARE")
    
    return (y - a) / (b - a)

def map_from_unit_interval(x, a, b):
    return a + (b - a) * x

#aprox_berstein
def aprox_berstein_on_interval(original_func, y_eval, n_degree, a, b):
    if a >= b:
        raise ValueError("Intervalul este ales gresit")

    x_transformed_eval = map_to_unit_interval(y_eval, a, b)

    def transformed_func_for_bernstein(x_unit):
        y_original = map_from_unit_interval(x_unit, a, b)
        return original_func(y_original)

    bernstein_sum = 0.0
    for k in range(n_degree + 1):
        binomial_coeff = math.comb(n_degree, k)

        bernstein_basis = (x_transformed_eval**k) * ((1 - x_transformed_eval)**(n_degree - k))

        term = transformed_func_for_bernstein(k / n_degree) * binomial_coeff * bernstein_basis
        bernstein_sum += term
    return bernstein_sum

def calculeaza_eroarea_abs(bernstein_sum,original_func_value):
    return abs(original_func_value-bernstein_sum)
    