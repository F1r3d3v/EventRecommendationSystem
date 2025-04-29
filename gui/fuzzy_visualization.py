import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from skfuzzy import control as ctrl
from tkinter import messagebox
import functools

from config import VISUALIZATION_RESOLUTION

class FuzzyVisualizationPanel(ttk.Frame):
    """Panel for visualizing the fuzzy system components."""
    def __init__(self, parent, fuzzy_system_wrapper):
        super().__init__(parent)
        self.fuzzy_system_wrapper = fuzzy_system_wrapper
        try:
            self.fuzzy_system = fuzzy_system_wrapper.control_system
            self.control_simulation = fuzzy_system_wrapper.simulation
            if not isinstance(self.fuzzy_system, ctrl.ControlSystem):
                 raise TypeError("Passed wrapper lacks valid ControlSystem.")
            if not isinstance(self.control_simulation, ctrl.ControlSystemSimulation):
                 raise TypeError("Passed wrapper lacks valid ControlSystemSimulation.")
        except AttributeError as e:
             messagebox.showerror("Init Error", f"Failed to get fuzzy system/sim: {e}")
             return

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.var_plots_page = ttk.Frame(self.notebook)
        self.rules_page = ttk.Frame(self.notebook)
        self.surface_page = ttk.Frame(self.notebook)

        self.notebook.add(self.var_plots_page, text="Membership Functions")
        self.notebook.add(self.rules_page, text="Rules")
        self.notebook.add(self.surface_page, text="Control Surface")

        self.antecedent_vars = self._get_antecedent_vars()
        self.fixed_input_sliders = {}
        self.fixed_input_labels = {}

        self._setup_var_plots_page()
        self._setup_rules_page()
        self._setup_surface_page()


    def _get_antecedent_vars(self):
        """Helper to extract antecedent variables from the wrapper."""
        antecedents = []
        possible_attrs = [
            'interest_match', 'location_proximity', 'time_overlap', 'budget_alignment'
        ]
        for attr in possible_attrs:
             var = getattr(self.fuzzy_system_wrapper, attr, None)
             if isinstance(var, ctrl.Antecedent):
                 antecedents.append(var)
        return antecedents


    def _setup_var_plots_page(self):
        """Create plots for input and output variable membership functions manually."""
        plot_frame = ttk.Frame(self.var_plots_page)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        output_var = getattr(self.fuzzy_system_wrapper, 'recommendation', None)
        all_vars = self.antecedent_vars + ([output_var] if isinstance(output_var, ctrl.Consequent) else [])

        if not all_vars:
            ttk.Label(plot_frame, text="No fuzzy variables found to plot.").pack()
            return

        num_vars = len(all_vars)
        cols = 2
        rows = (num_vars + cols - 1) // cols
        fig_height = max(3 * rows, 3)
        fig_width = max(6 * cols, 6)

        fig = Figure(figsize=(fig_width, fig_height))
        axes = fig.subplots(rows, cols, squeeze=False)
        axes_flat = axes.flatten()

        for i, var in enumerate(all_vars):
            if i < len(axes_flat):
                ax = axes_flat[i]
                try:
                    if hasattr(var, 'terms') and hasattr(var, 'universe') and var.universe is not None:
                        x = var.universe
                        ax.set_title(var.label)
                        ax.set_ylabel("Membership")
                        ax.set_xlabel("Value")
                        ax.set_ylim(0, 1.05)
                        plot_successful = False
                        for term_name, term_obj in var.terms.items():
                             if hasattr(term_obj, 'mf') and isinstance(term_obj.mf, np.ndarray):
                                 y = term_obj.mf
                                 if x.shape == y.shape:
                                     ax.plot(x, y, label=term_name)
                                     plot_successful = True
                                 else:
                                     print(f"Warn: Shape mismatch '{term_name}' in '{var.label}'. X:{x.shape}, Y:{y.shape}")
                             else:
                                print(f"Warn: Term '{term_name}' in '{var.label}' missing 'mf'.")

                        if plot_successful: ax.legend(fontsize='small')
                        else: ax.text(0.5, 0.5, "No terms plotted", ha='center', va='center', transform=ax.transAxes)
                        ax.grid(True, linestyle='--', alpha=0.6)
                    else:
                        ax.set_title(f"{var.label} (No data)")
                        ax.text(0.5, 0.5, "Missing terms/universe", ha='center', va='center', transform=ax.transAxes)

                except Exception as e:
                    print(f"Error plotting var {var.label}: {e}")
                    import traceback; traceback.print_exc()
                    ax.set_title(f"Error plotting {var.label}")
                    ax.text(0.5, 0.5, "Plotting Error", ha='center', va='center', transform=ax.transAxes)
            else:
                print(f"Warn: Not enough axes for var {var.label}")

        for j in range(num_vars, len(axes_flat)):
             if j < len(axes_flat): axes_flat[j].set_visible(False)

        try: fig.tight_layout(pad=1.5)
        except Exception as e: print(f"Error during tight_layout: {e}")

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    def _setup_rules_page(self):
        """Display the list of fuzzy rules."""
        rules_text_frame = ttk.Frame(self.rules_page)
        rules_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        rules_text = tk.Text(rules_text_frame, wrap=tk.WORD, font=("Courier", 10), height=10)
        scrollbar = ttk.Scrollbar(rules_text_frame, orient=tk.VERTICAL, command=rules_text.yview)
        rules_text.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        rules_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        rules_text.insert(tk.END, "Fuzzy Inference System Rules:\n\n")
        if hasattr(self.fuzzy_system, 'rules') and self.fuzzy_system.rules:
            for i, rule in enumerate(self.fuzzy_system.rules):
                try:
                    rule_str = str(rule).replace("Accumulated", " ").replace("Activated", " ").strip()
                    rules_text.insert(tk.END, f"Rule {i+1}: {rule_str}\n\n")
                except Exception as e:
                    rules_text.insert(tk.END, f"Rule {i+1}: Error displaying rule - {e}\n\n")
        else:
             rules_text.insert(tk.END, "No rules found in the fuzzy system.")
        rules_text.config(state=tk.DISABLED)


    def _setup_surface_page(self):
        """Setup the control surface visualization page with sliders for fixed inputs."""
        page_frame = ttk.Frame(self.surface_page)
        page_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for selection controls (X/Y axis, Update button)
        control_frame = ttk.Frame(page_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        vars_list = [var.label for var in self.antecedent_vars]

        # Handle case with insufficient input variables
        if len(vars_list) < 2:
             ttk.Label(control_frame, text="Need at least 2 input variables for surface plot.").pack()
             self.surface_fig = Figure(figsize=(8, 6))
             self.surface_ax = self.surface_fig.add_subplot(111, projection='3d')
             self.surface_ax.text2D(0.5, 0.5, "Need >= 2 input variables", ha='center', va='center', transform=self.surface_ax.transAxes)
             self.surface_canvas = FigureCanvasTkAgg(self.surface_fig, master=page_frame) # Embed in page_frame
             self.surface_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
             self.surface_canvas.draw()
             return

        # --- X/Y Axis Selection ---
        ttk.Label(control_frame, text="X Axis:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.x_var_label = tk.StringVar(value=vars_list[0])
        x_combo = ttk.Combobox(control_frame, textvariable=self.x_var_label, values=vars_list, width=20, state="readonly")
        x_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        x_combo.bind("<<ComboboxSelected>>", self._on_axis_change)

        ttk.Label(control_frame, text="Y Axis:").grid(row=0, column=2, padx=(15,5), pady=5, sticky=tk.W)
        self.y_var_label = tk.StringVar(value=vars_list[1])
        y_combo = ttk.Combobox(control_frame, textvariable=self.y_var_label, values=vars_list, width=20, state="readonly")
        y_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        y_combo.bind("<<ComboboxSelected>>", self._on_axis_change)

        ttk.Button(control_frame, text="Update Surface View", command=self._update_surface).grid(
            row=0, column=4, padx=20, pady=5, sticky=tk.E)

        control_frame.columnconfigure(4, weight=1)

        self.fixed_inputs_frame = ttk.LabelFrame(page_frame, text="Fixed Input Values")
        self.fixed_inputs_frame.pack(fill=tk.X, padx=10, pady=(5,0), ipady=5)

        # --- Matplotlib Figure ---
        self.surface_fig = Figure(figsize=(8, 6))
        self.surface_ax = None
        self.surface_canvas = FigureCanvasTkAgg(self.surface_fig, master=page_frame)
        self.surface_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.surface_cbar = None

        # --- Initial Setup ---
        self._update_fixed_input_sliders()
        self._update_surface()


    def _on_axis_change(self, event=None):
        """Callback when X or Y axis selection changes."""
        # Prevent selecting the same axis
        x_val = self.x_var_label.get()
        y_val = self.y_var_label.get()
        if x_val == y_val:
            messagebox.showwarning("Axis Selection", "X and Y axes must be different variables.")
            # Reset one of them? Find the first available different one.
            other_vars = [v.label for v in self.antecedent_vars if v.label != x_val]
            if other_vars:
                if event and event.widget.cget('textvariable') == str(self.y_var_label): # If Y caused conflict
                     self.y_var_label.set(other_vars[0])
                elif event and event.widget.cget('textvariable') == str(self.x_var_label): # If X caused conflict
                     self.x_var_label.set(other_vars[0])
                # Else default to resetting Y if conflict detected without event info
                elif len(self.antecedent_vars) > 1 :
                     self.y_var_label.set(self.antecedent_vars[1].label if self.antecedent_vars[0].label == x_val else self.antecedent_vars[0].label)

        self._update_fixed_input_sliders()
        self._update_surface()


    def _update_fixed_input_sliders(self):
        """Dynamically create/update sliders for fixed input variables."""
        for widget in self.fixed_inputs_frame.winfo_children():
            widget.destroy()

        x_label = self.x_var_label.get()
        y_label = self.y_var_label.get()

        current_row = 0
        fixed_vars_exist = False
        for var in self.antecedent_vars:
            var_label = var.label
            if var_label != x_label and var_label != y_label:
                fixed_vars_exist = True

                row_frame = ttk.Frame(self.fixed_inputs_frame)
                row_frame.grid(row=current_row, column=0, sticky=tk.EW, padx=5, pady=2)
                row_frame.columnconfigure(1, weight=1)

                # Label for variable name
                ttk.Label(row_frame, text=f"{var_label}:", width=18).grid(row=0, column=0, sticky=tk.W)

                # Tk variable for slider value
                if var_label not in self.fixed_input_sliders:
                     default_val = 50.0
                     try: default_val = (var.universe.min() + var.universe.max()) / 2.0
                     except: pass
                     tk_var = tk.DoubleVar(value=default_val)
                     self.fixed_input_sliders[var_label] = {'var': tk_var, 'widget': None}
                else:
                     tk_var = self.fixed_input_sliders[var_label]['var']

                # Slider for variable value
                slider_cmd = functools.partial(self._on_slider_change, var_label)
                slider = ttk.Scale(row_frame, from_=0, to=100,
                                   variable=tk_var, orient=tk.HORIZONTAL,
                                   command=slider_cmd)
                slider.grid(row=0, column=1, sticky=tk.EW, padx=5)
                self.fixed_input_sliders[var_label]['widget'] = slider

                # Label to display current value
                value_label = ttk.Label(row_frame, text=f"{tk_var.get():.1f}", width=5)
                value_label.grid(row=0, column=2, sticky=tk.E, padx=(0, 5))
                self.fixed_input_labels[var_label] = value_label

                current_row += 1

        if not fixed_vars_exist:
             ttk.Label(self.fixed_inputs_frame, text="All input variables are plotted.").grid(row=0, column=0, padx=5, pady=5)

        # Remove slider entries for variables that are now X or Y
        vars_to_remove = [lbl for lbl in self.fixed_input_sliders if lbl == x_label or lbl == y_label]
        for lbl in vars_to_remove:
            if lbl in self.fixed_input_sliders: del self.fixed_input_sliders[lbl]
            if lbl in self.fixed_input_labels: del self.fixed_input_labels[lbl]


    def _on_slider_change(self, var_label, value_str):
        """Callback when a fixed input slider value changes."""
        if var_label in self.fixed_input_labels:
            try:
                 value = float(value_str)
                 self.fixed_input_labels[var_label].config(text=f"{value:.1f}")
            except ValueError: pass
            
        pass


    def _update_surface(self):
        """Update the 3D control surface plot by clearing the figure and recreating the axes."""
        # --- Get X/Y labels ---
        x_label = self.x_var_label.get()
        y_label = self.y_var_label.get()
        if not x_label or not y_label or x_label == y_label:
            return

        # --- Find variable objects ---
        try:
            x_var = next(v for v in self.antecedent_vars if v.label == x_label)
            y_var = next(v for v in self.antecedent_vars if v.label == y_label)
            output_var = getattr(self.fuzzy_system_wrapper, 'recommendation', None)
            if not isinstance(output_var, ctrl.Consequent): raise AttributeError
        except (StopIteration, AttributeError):
            messagebox.showerror("Surface Plot Error", "Failed to find variables for plotting.")
            return

        # --- Calculate data grid ---
        resolution = VISUALIZATION_RESOLUTION
        try:
             x_min, x_max = x_var.universe.min(), x_var.universe.max()
             y_min, y_max = y_var.universe.min(), y_var.universe.max()
             x_range = np.linspace(x_min, x_max, resolution)
             y_range = np.linspace(y_min, y_max, resolution)
        except AttributeError:
             messagebox.showerror("Surface Plot Error", f"Universe missing for {x_label} or {y_label}.")
             return

        X, Y = np.meshgrid(x_range, y_range)
        Z = np.zeros_like(X)

        # --- Get fixed input values from sliders ---
        fixed_inputs = {}
        for var in self.antecedent_vars:
             current_label = var.label
             if current_label != x_label and current_label != y_label:
                 if current_label in self.fixed_input_sliders:
                      tk_var = self.fixed_input_sliders[current_label]['var']
                      fixed_inputs[current_label] = tk_var.get()
                 else:
                      print(f"Warning: Slider var missing for fixed input {current_label}. Defaulting 50.")
                      fixed_inputs[current_label] = 50

        # --- Simulation loop ---
        sim = self.control_simulation
        output_label = output_var.label
        for i in range(resolution):
            for j in range(resolution):
                # Set inputs
                sim.input[x_label] = X[i, j]
                sim.input[y_label] = Y[i, j]
                for label, val in fixed_inputs.items():
                    sim.input[label] = val
                # Compute
                try:
                     sim.compute()
                     Z[i, j] = sim.output[output_label]
                except KeyError:
                    try: Z[i, j] = (output_var.universe.min() + output_var.universe.max()) / 2
                    except AttributeError: Z[i,j] = 50
                except Exception as e:
                     print(f"Sim compute error at ({X[i,j]:.1f}, {Y[i,j]:.1f}): {e}")
                     Z[i, j] = np.nan

        # --- Plotting ---
        self.surface_fig.clear()
        self.surface_ax = None
        self.surface_cbar = None
        try:
             self.surface_ax = self.surface_fig.add_subplot(111, projection='3d')
        except ValueError as e:
             print(f"Error adding subplot: {e}")
             messagebox.showerror("Plot Error", "Failed to recreate plot axes.")
             self.surface_fig.text(0.5, 0.5, "Error creating plot axes", ha='center', va='center')
             self.surface_canvas.draw()
             return

        Z_masked = np.ma.masked_invalid(Z)
        plot_successful = False
        if Z_masked.count() > 0:
            try:
                surf = self.surface_ax.plot_surface(X, Y, Z_masked, cmap='viridis', edgecolor='none', antialiased=True)
                plot_successful = True
            except Exception as plot_error:
                 print(f"Error during plot_surface: {plot_error}")
                 self.surface_ax.text2D(0.5, 0.5, "Error during plotting", ha='center', va='center', transform=self.surface_ax.transAxes)
        else:
             self.surface_ax.text2D(0.5, 0.5, "No valid output data", ha='center', va='center', transform=self.surface_ax.transAxes)

        self.surface_ax.set_xlabel(x_label)
        self.surface_ax.set_ylabel(y_label)
        self.surface_ax.set_zlabel(output_label)
        self.surface_ax.set_title(f"Surface: {output_label} vs ({x_label}, {y_label})")
        try:
            z_min_limit = output_var.universe.min()
            z_max_limit = output_var.universe.max() * 1.08
            self.surface_ax.set_zlim(z_min_limit, z_max_limit)
        except AttributeError:
             print("Warning: Output universe limits fail. Defaulting Z axis 0-100.")
             self.surface_ax.set_zlim(0, 100)

        # Add a color bar if plotting was successful
        if plot_successful:
            self.surface_cbar = self.surface_fig.colorbar(surf, ax=self.surface_ax, shrink=0.5, aspect=5)

        # Redraw the canvas containing the figure
        self.surface_canvas.draw()
