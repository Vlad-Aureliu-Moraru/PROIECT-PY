from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import SplineFunctions as sf

class SplineWindowImp:
    def __init__(self, ui, statusbar, main_window):
        self.ui = ui
        self.statusbar = statusbar
        self.main_window = main_window
        
        # Initialize variables
        self.x_points = np.array([])
        self.y_points = np.array([])
        
        # Set up the graph
        self.setup_spline_graph()
        
        # Connect signals
        self.ui.IS_BUTTON_CALCULEAZA.clicked.connect(self.calculate_spline)
        self.ui.IS_TEXTFIELD_INTERVAL.textChanged.connect(self.clear_points)
        self.ui.IS_TEXTFIELD_NODURI.textChanged.connect(self.clear_points)
        self.ui.IS_RADIO_LINIAR.toggled.connect(self.on_spline_type_changed)
        self.ui.IS_RADIO_PATRATIC.toggled.connect(self.on_spline_type_changed)
        self.ui.IS_RADIO_CUBIC.toggled.connect(self.on_spline_type_changed)
        
        # Set up table
        self.ui.IL_TABEL_2.setColumnCount(2)
        self.ui.IL_TABEL_2.setHorizontalHeaderLabels(['X', 'Y'])
        
        # Set default values and placeholders
        self.ui.IS_TEXTFIELD_INTERVAL.setPlaceholderText("Enter interval [a,b]")
        self.ui.IS_TEXTFIELD_NODURI.setPlaceholderText("Enter number of nodes")
        self.ui.IS_TEXTFIELD_OUTPUT.setPlaceholderText("Enter point to evaluate")
        self.ui.IS_TEXTFIELD_ERROR.setPlaceholderText("Error will be displayed here")
        
        # Set default spline type
        self.ui.IS_RADIO_LINIAR.setChecked(True)
        
        self.statusbar.showMessage("Ready to calculate spline interpolation.", 3000)

    def clear_points(self):
        """Clear the current points and reset the plot"""
        self.x_points = np.array([])
        self.y_points = np.array([])
        self.ui.IS_TEXTFIELD_OUTPUT.clear()
        self.ui.IS_TEXTFIELD_ERROR.clear()
        self.ui.IL_TABEL_2.setRowCount(0)
        self.axes.clear()
        self.axes.text(0.5, 0.5, 'Adaugă puncte pentru interpolare',
                      horizontalalignment='center',
                      verticalalignment='center',
                      transform=self.axes.transAxes)
        self.canvas.draw()

    def on_spline_type_changed(self):
        """Handle spline type changes"""
        if self.x_points.size > 0:
            spline_type = self.get_spline_type()
            self.plot_spline(spline_type)

    def setup_spline_graph(self):
        """Set up the graph for spline interpolation"""
        # Create new figure and canvas
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self.main_window)
        
        # Create new layout
        self.graph_layout = QtWidgets.QVBoxLayout()
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)
        
        # Set the layout to the widget
        self.ui.IS_WIG_GRAF.setLayout(self.graph_layout)
        
        # Add initial message to the plot
        self.axes.text(0.5, 0.5, 'Adaugă puncte pentru interpolare',
                      horizontalalignment='center',
                      verticalalignment='center',
                      transform=self.axes.transAxes)
        self.canvas.draw()

    def parse_interval_string(self, interval_str):
        """Parse interval string in format [a,b]"""
        try:
            # Remove brackets and split by comma
            interval_str = interval_str.strip('[]')
            a, b = map(float, interval_str.split(','))
            if a >= b:
                QMessageBox.warning(self.main_window, "Invalid Interval", 
                                  "Start of interval must be less than end")
                return None, None
            return a, b
        except (ValueError, IndexError):
            QMessageBox.warning(self.main_window, "Invalid Format", 
                              "Please use format [a,b] where a and b are numbers")
            return None, None

    def generate_points(self):
        """Generate interpolation points based on interval and number of nodes"""
        try:
            # Get interval
            interval_str = self.ui.IS_TEXTFIELD_INTERVAL.text().strip()
            if not interval_str:
                raise ValueError("Please enter the interval")
            a, b = self.parse_interval_string(interval_str)
            if a is None or b is None:
                return False
            
            # Get number of nodes
            num_nodes_text = self.ui.IS_TEXTFIELD_NODURI.text().strip()
            if not num_nodes_text:
                raise ValueError("Please enter the number of nodes")
            num_nodes = int(num_nodes_text)
            
            # Check minimum number of points based on spline type
            spline_type = self.get_spline_type()
            min_points = {"linear": 2, "quadratic": 3, "cubic": 4}[spline_type]
            if num_nodes < min_points:
                raise ValueError(f"Number of nodes must be at least {min_points} for {spline_type} spline")
            
            # Generate points
            self.x_points = np.linspace(a, b, num_nodes)
            self.y_points = np.array([sf.target_function(x) for x in self.x_points])
            
            # Update table
            sf.update_table(self.ui.IL_TABEL_2, self.x_points, self.y_points)
            
            # Plot initial points
            self.plot_spline(spline_type)
            
            return True
            
        except ValueError as e:
            self.statusbar.showMessage(str(e), 3000)
            return False

    def get_spline_type(self):
        """Get the selected spline type"""
        if self.ui.IS_RADIO_LINIAR.isChecked():
            return "linear"
        elif self.ui.IS_RADIO_PATRATIC.isChecked():
            return "quadratic"
        elif self.ui.IS_RADIO_CUBIC.isChecked():
            return "cubic"
        else:
            raise ValueError("No spline type selected")

    def calculate_spline(self):
        """Calculate spline interpolation at the given point"""
        try:
            # First, generate points if not already done
            if not self.x_points.size or not self.y_points.size:
                if not self.generate_points():
                    return
            
            # Get evaluation point
            x_eval_text = self.ui.IS_TEXTFIELD_OUTPUT.text().strip()
            if not x_eval_text:
                # If no evaluation point is entered, use the first point
                x_eval = self.x_points[0]
                self.ui.IS_TEXTFIELD_OUTPUT.setText(f"{x_eval:.6f}")
            else:
                try:
                    x_eval = float(x_eval_text)
                except ValueError:
                    self.statusbar.showMessage("Please enter a valid number for evaluation point", 3000)
                    return
            
            # Get spline type
            spline_type = self.get_spline_type()
            
            # Check if point is within range
            x_min, x_max = np.min(self.x_points), np.max(self.x_points)
            if not (x_min <= x_eval <= x_max):
                QMessageBox.warning(self.main_window, "Warning", 
                                  f"Point {x_eval} is outside the interpolation range [{x_min:.2f}, {x_max:.2f}]")
            
            # Calculate interpolation
            try:
                if spline_type == "linear":
                    result = sf.linear_spline(self.x_points, self.y_points, x_eval)
                elif spline_type == "quadratic":
                    result = sf.quadratic_spline(self.x_points, self.y_points, x_eval)
                else:  # cubic
                    result = sf.cubic_spline(self.x_points, self.y_points, x_eval)
                
                # Calculate error
                error = sf.calculate_error(self.x_points, self.y_points, spline_type)
                
                # Format results with 6 decimal places
                result_str = f"{result:.6f}"
                error_str = f"{error:.6f}"
                
                # Update text fields
                self.ui.IS_TEXTFIELD_OUTPUT.setText(result_str)
                self.ui.IS_TEXTFIELD_ERROR.setText(error_str)
                
                # Update plot
                self.plot_spline(spline_type)
                
                # Show success message with values
                self.statusbar.showMessage(
                    f"{spline_type.capitalize()} spline: f({x_eval:.2f}) = {result_str}, Error = {error_str}", 
                    3000
                )
                
            except Exception as e:
                self.statusbar.showMessage(f"Error calculating spline: {str(e)}", 3000)
                return
            
        except Exception as e:
            self.statusbar.showMessage(f"Error: {str(e)}", 3000)

    def plot_spline(self, spline_type):
        """Plot the spline interpolation"""
        try:
            # Clear the current plot
            self.axes.clear()
            
            # Generate points for plotting
            x_min, x_max = np.min(self.x_points), np.max(self.x_points)
            x_plot = np.linspace(x_min, x_max, 1000)
            
            # Calculate interpolated values
            if spline_type == "linear":
                y_interp = np.array([sf.linear_spline(self.x_points, self.y_points, x) for x in x_plot])
            elif spline_type == "quadratic":
                y_interp = np.array([sf.quadratic_spline(self.x_points, self.y_points, x) for x in x_plot])
            else:  # cubic
                y_interp = sf.cubic_spline(self.x_points, self.y_points, x_plot)
            
            # Calculate actual values
            y_actual = np.array([sf.target_function(x) for x in x_plot])
            
            # Plot the results
            self.axes.plot(x_plot, y_interp, 'b-', label=f'{spline_type.capitalize()} Spline')
            self.axes.plot(x_plot, y_actual, 'g--', label='Original Function')
            self.axes.scatter(self.x_points, self.y_points, color='red', label='Interpolation Points')
            
            # Add labels and grid
            self.axes.grid(True)
            self.axes.legend()
            self.axes.set_title(f'{spline_type.capitalize()} Spline Interpolation')
            self.axes.set_xlabel('x')
            self.axes.set_ylabel('y')
            
            # Refresh the canvas
            self.canvas.draw()
            
        except Exception as e:
            self.statusbar.showMessage(f"Failed to update plot: {str(e)}", 3000)
