import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

class TimePreferencePanel(ttk.Frame):
    """Panel for setting preferred time ranges."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator

        # Internal list of (start_datetime, end_datetime) tuples
        self.time_ranges = []

        # --- UI Elements ---
        time_frame = ttk.LabelFrame(self, text="Preferred Time Ranges")
        time_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.time_listbox = tk.Listbox(time_frame, height=6, selectmode=tk.SINGLE)
        self.time_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(5,0), pady=5)

        scrollbar = ttk.Scrollbar(time_frame, orient=tk.VERTICAL, command=self.time_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, padx=(0,5), pady=5)
        self.time_listbox.config(yscrollcommand=scrollbar.set)

        # Frame for Add/Remove buttons below listbox
        list_btn_frame = ttk.Frame(time_frame)
        list_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0,5))
        ttk.Button(list_btn_frame, text="Remove Selected", command=self._remove_time_range).pack(side=tk.LEFT)

        # Frame for adding a new time range
        add_frame = ttk.LabelFrame(self, text="Add New Time Range")
        add_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        add_frame.columnconfigure(1, weight=0)
        add_frame.columnconfigure(2, weight=0)
        add_frame.columnconfigure(3, weight=0)
        add_frame.columnconfigure(4, weight=0)

        # Start Time Label
        ttk.Label(add_frame, text="Start Time:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        # Create widgets and get variables back
        self.start_hour_var, self.start_min_var, self.start_period_var = \
            self._create_time_widgets(add_frame, 0, "9", "00", "AM") # Pass target row 0

        # End Time Label
        ttk.Label(add_frame, text="End Time:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        # Create widgets and get variables back
        self.end_hour_var, self.end_min_var, self.end_period_var = \
            self._create_time_widgets(add_frame, 1, "5", "00", "PM") # Pass target row 1

        # Add Button for the new range
        ttk.Button(add_frame, text="Add Time Range", command=self._add_time_range).grid(
            row=2, column=0, columnspan=5, pady=(5, 10)) # Span all columns

        # Load initial preferences
        self.load_preferences()


    def _create_time_widgets(self, parent, target_row, default_hour, default_min, default_period):
        """
        Helper to create hour, minute, period comboboxes and colon label,
        grid them in the parent, and return the associated tk Variables.
        """
        hour_var = tk.StringVar(value=default_hour)
        min_var = tk.StringVar(value=default_min)
        period_var = tk.StringVar(value=default_period)

        hour_values = [str(i) for i in range(1, 13)] # 1-12 for display
        min_values = [str(i).zfill(2) for i in range(0, 60, 5)] # 5-minute increments

        hour_combo = ttk.Combobox(parent, textvariable=hour_var, values=hour_values, width=3, state="readonly")
        colon_label = ttk.Label(parent, text=":")
        min_combo = ttk.Combobox(parent, textvariable=min_var, values=min_values, width=3, state="readonly")
        period_combo = ttk.Combobox(parent, textvariable=period_var, values=["AM", "PM"], width=3, state="readonly")

        hour_combo.grid(row=target_row, column=1, padx=(0, 2), pady=5, sticky=tk.W)
        colon_label.grid(row=target_row, column=2, padx=0, pady=5, sticky=tk.W)
        min_combo.grid(row=target_row, column=3, padx=2, pady=5, sticky=tk.W)
        period_combo.grid(row=target_row, column=4, padx=(2, 5), pady=5, sticky=tk.W)

        return hour_var, min_var, period_var


    def _parse_time_input(self, hour_var, min_var, period_var):
        """Parses time from combobox variables into 24-hour format hour and minute."""
        try:
            hour12 = int(hour_var.get())
            minute = int(min_var.get())
            period = period_var.get().upper()

            hour24 = hour12
            if period == "PM" and hour12 != 12:
                hour24 += 12
            elif period == "AM" and hour12 == 12: # Midnight case
                hour24 = 0

            return hour24, minute
        except ValueError:
            messagebox.showerror("Input Error", "Invalid time selected.")
            return None, None


    def _add_time_range(self):
        """Adds the time range specified in the input fields to the list."""
        start_hour, start_min = self._parse_time_input(self.start_hour_var, self.start_min_var, self.start_period_var)
        end_hour, end_min = self._parse_time_input(self.end_hour_var, self.end_min_var, self.end_period_var)

        if start_hour is None or end_hour is None:
            return

        now = datetime.now()
        try:
            start_time = now.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
            end_time = now.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
        except ValueError as e:
             messagebox.showerror("Time Error", f"Could not create time: {e}")
             return

        # Handle overnight ranges (e.g., 10 PM to 2 AM)
        if end_time <= start_time:
            end_time += timedelta(days=1)

        # Add to internal list and update UI
        self.time_ranges.append((start_time, end_time))
        self._update_time_listbox()
        self._notify_app()


    def _remove_time_range(self):
        """Removes the selected time range from the list."""
        selected_indices = self.time_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            if 0 <= index < len(self.time_ranges):
                del self.time_ranges[index]
                self._update_time_listbox()
                self._notify_app()
        else:
             messagebox.showinfo("Remove Time Range", "Please select a time range to remove.")


    def _update_time_listbox(self):
        """Updates the listbox display from the internal time_ranges list."""
        self.time_listbox.delete(0, tk.END)
        # Sort ranges by start time
        self.time_ranges.sort(key=lambda x: x[0])
        for start, end in self.time_ranges:
            # Format for display
            time_str = f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"
            # Indicate if it spans overnight
            if end.date() > start.date():
                 # Check if it's exactly 24 hours or more (unlikely but possible)
                 if (end - start) >= timedelta(days=1):
                     time_str += " (next day)"
                 else: # Standard overnight case
                     time_str += " (next day)"

            self.time_listbox.insert(tk.END, time_str)


    def _notify_app(self):
        """Inform the application coordinator about the updated time ranges."""
        self.app.time_preference_updated(self.time_ranges.copy())


    def load_preferences(self):
        """Loads time preferences from the service."""
        prefs = self.app.get_current_preferences()
        self.time_ranges = [(s, e) for s, e in prefs.preferred_times if isinstance(s, datetime) and isinstance(e, datetime)]
        self._update_time_listbox()
