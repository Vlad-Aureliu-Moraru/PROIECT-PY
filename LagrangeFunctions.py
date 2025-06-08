import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import math


def target_function(val):
    return math.cos(math.pi * val)

def lagrange_interpolation(x_points: List[float], y_points: List[float], x_eval: float) -> float:
    n = len(x_points)
    result = 0.0
    for i in range(n):
        term = y_points[i]
        for j in range(n):
            if i != j:
                term *= (x_eval - x_points[j]) / (x_points[i] - x_points[j])
        result += term
    
    return result

def calculate_interpolation_error(x_points: List[float], y_points: List[float], num_eval_points: int = 1000) -> float:
    x_min, x_max = min(x_points), max(x_points)
    x_eval = np.linspace(x_min, x_max, num_eval_points)
    
    max_error = 0.0
    for x in x_eval:
        interpolated = lagrange_interpolation(x_points, y_points, x)
        actual = target_function(x)
        error = abs(interpolated - actual)
        max_error = max(max_error, error)
    
    return max_error

def plot_lagrange_interpolation(x_points: List[float], y_points: List[float], 
                              num_points: int = 1000) -> Tuple[plt.Figure, plt.Axes]:
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.scatter(x_points, y_points, color='red', label='Punctele de Interpolare')
    
    x_min, x_max = min(x_points), max(x_points)
    x_plot = np.linspace(x_min, x_max, num_points)
    y_plot = [lagrange_interpolation(x_points, y_points, x) for x in x_plot]
    ax.plot(x_plot, y_plot, 'b-', label='Interpolare Lagrange')
    
    y_target = [target_function(x) for x in x_plot]
    ax.plot(x_plot, y_target, 'g--', label='Functia in py')
    
    ax.grid(True)
    ax.legend()
    ax.set_title('Interpolare Lagrange')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    
    return fig, ax
