import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import math

def lagrange_interpolation(x_points: List[float], y_points: List[float], x_eval: float) -> float:
    """
    Calculate the Lagrange interpolation polynomial value at point x_eval.
    
    Args:
        x_points: List of x-coordinates of the interpolation points
        y_points: List of y-coordinates of the interpolation points
        x_eval: Point at which to evaluate the interpolation polynomial
        
    Returns:
        float: The interpolated value at x_eval
    """
    if len(x_points) != len(y_points):
        raise ValueError("x_points and y_points must have the same length")
    
    n = len(x_points)
    result = 0.0
    
    for i in range(n):
        term = y_points[i]
        for j in range(n):
            if i != j:
                term *= (x_eval - x_points[j]) / (x_points[i] - x_points[j])
        result += term
    
    return result

def lagrange_derivative(x_points: List[float], y_points: List[float], x_eval: float) -> float:
    """
    Calculate the derivative of the Lagrange interpolation polynomial at point x_eval.
    
    Args:
        x_points: List of x-coordinates of the interpolation points
        y_points: List of y-coordinates of the interpolation points
        x_eval: Point at which to evaluate the derivative
        
    Returns:
        float: The derivative value at x_eval
    """
    if len(x_points) != len(y_points):
        raise ValueError("x_points and y_points must have the same length")
    
    n = len(x_points)
    result = 0.0
    
    for i in range(n):
        term = y_points[i]
        for j in range(n):
            if i != j:
                # Calculate the derivative of the Lagrange basis polynomial
                numerator = 1.0
                denominator = 1.0
                for k in range(n):
                    if k != i and k != j:
                        numerator *= (x_eval - x_points[k])
                        denominator *= (x_points[i] - x_points[k])
                term *= numerator / denominator
        result += term
    
    return result

def calculate_error(x_points: List[float], y_points: List[float], original_func: callable) -> float:
    """
    Calculate the maximum error between the Lagrange interpolation and the original function.
    
    Args:
        x_points: List of x-coordinates of the interpolation points
        y_points: List of y-coordinates of the interpolation points
        original_func: The original function to compare against
        
    Returns:
        float: The maximum error
    """
    if len(x_points) != len(y_points):
        raise ValueError("x_points and y_points must have the same length")
    
    # Create a dense set of points for error evaluation
    x_min, x_max = min(x_points), max(x_points)
    x_eval = np.linspace(x_min, x_max, 1000)
    
    max_error = 0.0
    for x in x_eval:
        interpolated = lagrange_interpolation(x_points, y_points, x)
        original = original_func(x)
        error = abs(interpolated - original)
        max_error = max(max_error, error)
    
    return max_error

def plot_lagrange_interpolation(x_points: List[float], y_points: List[float], 
                              original_func: Optional[callable] = None,
                              num_points: int = 1000) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot the Lagrange interpolation polynomial and optionally the original function.
    
    Args:
        x_points: List of x-coordinates of the interpolation points
        y_points: List of y-coordinates of the interpolation points
        original_func: Optional original function to plot for comparison
        num_points: Number of points to use for plotting the interpolation
        
    Returns:
        Tuple[plt.Figure, plt.Axes]: The figure and axes objects
    """
    if len(x_points) != len(y_points):
        raise ValueError("x_points and y_points must have the same length")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot interpolation points
    ax.scatter(x_points, y_points, color='red', label='Interpolation Points')
    
    # Plot interpolation polynomial
    x_min, x_max = min(x_points), max(x_points)
    x_plot = np.linspace(x_min, x_max, num_points)
    y_plot = [lagrange_interpolation(x_points, y_points, x) for x in x_plot]
    ax.plot(x_plot, y_plot, 'b-', label='Lagrange Interpolation')
    
    # Plot original function if provided
    if original_func is not None:
        y_original = [original_func(x) for x in x_plot]
        ax.plot(x_plot, y_original, 'g--', label='Original Function')
    
    ax.grid(True)
    ax.legend()
    ax.set_title('Lagrange Interpolation')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    
    return fig, ax
