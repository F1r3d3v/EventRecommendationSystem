# gui/history_panel.py
import tkinter as tk
from tkinter import ttk
import matplotlib
# Ensure backend is TkAgg if needed (should be set in main.py)
# print(f"Backend in history_panel: {matplotlib.get_backend()}")
# matplotlib.use('TkAgg') # Force here only if main.py setting isn't working
from matplotlib.figure import Figure # Import Figure explicitly
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
from datetime import datetime, timedelta

class HistoryPanel(ttk.Frame):
    """Panel for displaying event history and visualizations."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator # Reference to the main app coordinator
        self.attended_events = [] # Local cache of history data

        # --- UI Elements ---
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side - History list
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)

        ttk.Label(list_frame, text="Attended Events History", font=("Helvetica", 12, "bold")).pack(pady=(10, 5))

        self.history_listbox = tk.Listbox(list_frame, font=("Helvetica", 11), selectmode=tk.SINGLE)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0), pady=5)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, padx=(0,5), pady=5)
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        ttk.Button(list_frame, text="Remove Selected from History",
                  command=self._remove_selected).pack(pady=5)

        # Right side - Visualizations
        viz_frame = ttk.Frame(paned)
        paned.add(viz_frame, weight=1)

        ttk.Label(viz_frame, text="Event History Analysis",
                 font=("Helvetica", 12, "bold")).pack(pady=(10, 5))

        viz_notebook = ttk.Notebook(viz_frame)
        viz_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab for category distribution
        self.cat_tab_frame = ttk.Frame(viz_notebook)
        viz_notebook.add(self.cat_tab_frame, text="Categories")

        # Tab for time distribution
        self.time_tab_frame = ttk.Frame(viz_notebook)
        viz_notebook.add(self.time_tab_frame, text="Time of Day")

        # --- FIX: Create Figures and Axes using OO interface ---
        # Create Figure objects directly
        self.cat_figure = Figure(figsize=(6, 4), dpi=100) # Control size/dpi if needed
        self.time_figure = Figure(figsize=(6, 4), dpi=100)

        # Add Axes (subplots) to each Figure
        self.cat_ax = self.cat_figure.add_subplot(111) # 1 row, 1 col, 1st subplot
        self.time_ax = self.time_figure.add_subplot(111)
        # --- End Fix ---

        # Add plots to the tkinter frames using the created Figures
        self.cat_canvas = self._create_canvas(self.cat_figure, self.cat_tab_frame)
        self.time_canvas = self._create_canvas(self.time_figure, self.time_tab_frame)

        # Load initial history data
        self.update_history_display()

    def _create_canvas(self, figure, parent):
        """Helper to create and pack a FigureCanvasTkAgg."""
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Ensure initial draw clears any potential placeholder content from Figure creation
        figure.clear() # Clear figure initially before first plot
        # Add axes back after clearing the figure if using add_subplot approach
        if not figure.get_axes(): # Add axes only if they don't exist
             if figure is self.cat_figure:
                 self.cat_ax = figure.add_subplot(111)
             elif figure is self.time_figure:
                 self.time_ax = figure.add_subplot(111)
        canvas.draw()
        return canvas

    def update_history_display(self):
        """Fetches latest history and updates the listbox and visualizations."""
        self.attended_events = self.app.get_history_data() # Get latest data
        self._update_history_listbox()
        self._update_category_visualization()
        self._update_time_visualization()

    def _update_history_listbox(self):
        """Updates the history listbox content."""
        self.history_listbox.delete(0, tk.END)
        # Sort history, e.g., by date attended if available, otherwise by name
        # Use a stable default attribute like name if 'attended_date' isn't present
        sorted_history = sorted(self.attended_events, key=lambda e: getattr(e, 'attended_date', e.name))
        for event in sorted_history:
            # Display relevant info, e.g., name and category
            cat_str = event.category if isinstance(event.category, str) else ", ".join(event.category) if isinstance(event.category, list) else "N/A"
            self.history_listbox.insert(tk.END, f"{event.name} ({cat_str})")


    def _remove_selected(self):
        """Removes the selected event from history via the app coordinator."""
        selected_indices = self.history_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            # Need to map listbox index back to the correct event object
            # Assuming the listbox order matches self.attended_events after sorting
            sorted_history = sorted(self.attended_events, key=lambda e: getattr(e, 'attended_date', e.name))
            if 0 <= index < len(sorted_history):
                event_to_remove = sorted_history[index]
                # Notify the app coordinator
                self.app.request_remove_from_history(event_to_remove)
                # The app coordinator will call update_history_display after service update
        else:
             # Optional: Show info message if nothing selected
             pass


    def _update_category_visualization(self):
        """Update the category distribution bar chart."""
        # Ensure the correct axes exist after potential clearing in _create_canvas
        if not self.cat_figure.get_axes():
             self.cat_ax = self.cat_figure.add_subplot(111)
        ax = self.cat_ax # Use local variable for clarity

        ax.clear() # Clear previous plot axes

        if not self.attended_events:
            ax.set_title("No Attended Events Yet")
            ax.text(0.5, 0.5, "Attend events to see analysis", ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.cat_canvas.draw()
            return

        # Aggregate categories
        categories = []
        for event in self.attended_events:
            if isinstance(event.category, list):
                categories.extend(event.category)
            elif isinstance(event.category, str):
                categories.append(event.category)

        if not categories: # Handle case where events have no categories
            ax.set_title("Attended Events Lack Categories")
            ax.text(0.5, 0.5, "No category data", ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.cat_canvas.draw()
            return

        category_counts = Counter(categories)
        if not category_counts: # If Counter is empty after processing
            ax.set_title("No Categories Found")
            ax.text(0.5, 0.5, "No category data", ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.cat_canvas.draw()
            return

        # Proceed only if there's data
        labels, values = zip(*category_counts.most_common()) # Get sorted labels and values

        bars = ax.bar(labels, values, color='skyblue')
        ax.set_ylabel("Number of Events Attended")
        ax.set_title("Category Preferences (Based on History)")

        # Add value labels on bars
        ax.bar_label(bars, padding=3)

        # Improve layout
        # Use figure's tight_layout
        try:
            self.cat_figure.tight_layout(pad=1.5) # Add padding
        except ValueError as e:
             print(f"Warning: tight_layout failed for category plot: {e}") # Can fail if axes empty etc.

        # Rotate labels AFTER plotting and layout
        if labels: # Only rotate if there are labels
             matplotlib.pyplot.setp(ax.get_xticklabels(), rotation=30, ha='right')

        self.cat_canvas.draw()


    def _update_time_visualization(self):
        """Update the time of day distribution bar chart."""
        # Ensure the correct axes exist
        if not self.time_figure.get_axes():
             self.time_ax = self.time_figure.add_subplot(111)
        ax = self.time_ax # Use local variable

        ax.clear() # Clear previous plot axes

        if not self.attended_events:
            ax.set_title("No Attended Events Yet")
            ax.text(0.5, 0.5, "Attend events to see analysis", ha='center', va='center', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            self.time_canvas.draw()
            return

        # Define time bins
        time_bins = {
            "Morning (6AM-12PM)": 0,
            "Afternoon (12PM-5PM)": 0,
            "Evening (5PM-9PM)": 0,
            "Night (9PM-6AM)": 0
        }
        bin_keys = list(time_bins.keys()) # Keep order

        events_with_time = 0
        for event in self.attended_events:
            # Use event start time
            if hasattr(event, 'start_time') and isinstance(event.start_time, datetime):
                events_with_time += 1
                hour = event.start_time.hour
                if 6 <= hour < 12: time_bins[bin_keys[0]] += 1
                elif 12 <= hour < 17: time_bins[bin_keys[1]] += 1
                elif 17 <= hour < 21: time_bins[bin_keys[2]] += 1
                else: time_bins[bin_keys[3]] += 1 # Includes 9PM up to 6AM

        if events_with_time == 0: # Handle case where events lack valid times
             ax.set_title("Attended Events Lack Time Data")
             ax.text(0.5, 0.5, "No time data available", ha='center', va='center', transform=ax.transAxes)
             ax.set_xticks([])
             ax.set_yticks([])
             self.time_canvas.draw()
             return

        values = [time_bins[key] for key in bin_keys]

        bars = ax.bar(bin_keys, values, color='lightcoral')
        ax.set_ylabel("Number of Events Attended")
        ax.set_title("Preferred Time of Day (Based on History)")

        # Add value labels
        ax.bar_label(bars, padding=3)

        # Improve layout
        try:
            self.time_figure.tight_layout(pad=1.5)
        except ValueError as e:
             print(f"Warning: tight_layout failed for time plot: {e}")

        # Rotate labels AFTER plotting and layout
        if bin_keys: # Only rotate if there are labels
            matplotlib.pyplot.setp(ax.get_xticklabels(), rotation=30, ha='right')

        self.time_canvas.draw()