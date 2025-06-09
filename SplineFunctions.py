import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets

def target_function(x):
    """Target function to approximate: cos(πx)"""
    return np.cos(np.pi * x)

def linear_spline(x_points, y_points, x_eval):
    """Calculate linear spline interpolation"""
    x_points = np.array(x_points)
    y_points = np.array(y_points)
    x_eval = np.array(x_eval)
    
    # Find the interval for each evaluation point
    i = np.searchsorted(x_points, x_eval) - 1
    i = np.clip(i, 0, len(x_points) - 2)
    
    # Calculate linear interpolation
    x0, x1 = x_points[i], x_points[i + 1]
    y0, y1 = y_points[i], y_points[i + 1]
    
    return y0 + (y1 - y0) * (x_eval - x0) / (x1 - x0)

def quadratic_spline(x_points, y_points, x_eval):
    """Calculate quadratic spline interpolation"""
    x_points = np.array(x_points)
    y_points = np.array(y_points)
    x_eval = np.array(x_eval)
    
    n = len(x_points) - 1
    h = np.diff(x_points)
    
    # Calculate coefficients
    a = y_points[:-1]
    b = np.zeros(n)
    c = np.zeros(n)
    
    # Set up system of equations
    A = np.zeros((n, n))
    rhs = np.zeros(n)
    
    # Interior points
    for i in range(1, n):
        A[i, i-1] = h[i-1]
        A[i, i] = 2 * (h[i-1] + h[i])
        A[i, i+1] = h[i]
        rhs[i] = 6 * ((y_points[i+1] - y_points[i])/h[i] - 
                      (y_points[i] - y_points[i-1])/h[i-1])
    
    # Natural spline conditions
    A[0, 0] = 1
    A[-1, -1] = 1
    
    # Solve for c coefficients
    c = np.linalg.solve(A, rhs)
    
    # Calculate b coefficients
    b = (y_points[1:] - y_points[:-1])/h - h/6 * (2*c[:-1] + c[1:])
    
    # Find intervals for evaluation points
    i = np.searchsorted(x_points, x_eval) - 1
    i = np.clip(i, 0, n-1)
    
    # Calculate interpolated values
    dx = x_eval - x_points[i]
    return a[i] + b[i]*dx + c[i]*dx**2/2

def cubic_spline(x_points, y_points, x_eval):
    """Calculate cubic spline interpolation"""
    x_points = np.array(x_points)
    y_points = np.array(y_points)
    x_eval = np.array(x_eval)
    
    # Use scipy's CubicSpline for natural boundary conditions
    cs = CubicSpline(x_points, y_points, bc_type='natural')
    return cs(x_eval)

def calculate_error(x_points, y_points, spline_type):
    """Calculate the maximum error of the spline interpolation"""
    # Generate dense points for error calculation
    x_min, x_max = np.min(x_points), np.max(x_points)
    x_dense = np.linspace(x_min, x_max, 1000)
    
    # Calculate actual values
    y_actual = target_function(x_dense)
    
    # Calculate interpolated values
    if spline_type == "linear":
        y_interp = linear_spline(x_points, y_points, x_dense)
    elif spline_type == "quadratic":
        y_interp = quadratic_spline(x_points, y_points, x_dense)
    else:  # cubic
        y_interp = cubic_spline(x_points, y_points, x_dense)
    
    # Calculate maximum absolute error
    return np.max(np.abs(y_actual - y_interp))

def update_table(table, x_points, y_points):
    """Update the table with interpolation points"""
    try:
        table.setRowCount(len(x_points))
        for i, (x, y) in enumerate(zip(x_points, y_points)):
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{x:.6f}"))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{y:.6f}"))
    except Exception as e:
        print(f"Error updating table: {str(e)}") 