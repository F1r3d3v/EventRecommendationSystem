# gui/preference_panel.py
import tkinter as tk
from tkinter import ttk
from config import AVAILABLE_CATEGORIES, DEFAULT_CATEGORIES_WITH_WEIGHTS

class PreferencePanel(ttk.Frame):
    """Panel for setting category preferences."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator # Reference to the main app coordinator

        # Use categories from config
        self.categories = AVAILABLE_CATEGORIES

        # Get initial preferences from the service via app coordinator
        current_preferences = self.app.get_current_preferences().categories

        selection_frame = ttk.LabelFrame(self, text="Select Categories of Interest & Importance (Weight)")
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.category_vars = {}
        self.weight_vars = {}
        self.sliders = {} # To enable/disable sliders

        cols = 3 # Number of columns for categories
        for i, category in enumerate(self.categories):
            row = i // cols
            col = i % cols

            cat_frame = ttk.Frame(selection_frame)
            cat_frame.grid(row=row, column=col, padx=10, pady=5, sticky=tk.W+tk.E) # Use sticky

            # --- Checkbox ---
            # Initial state from current preferences or default
            is_selected = category in current_preferences
            self.category_vars[category] = tk.BooleanVar(value=is_selected)
            chk = ttk.Checkbutton(cat_frame, text=category,
                                 variable=self.category_vars[category],
                                 # Pass category to the command
                                 command=lambda c=category: self._on_preference_change(c))
            chk.grid(row=0, column=0, columnspan=2, sticky=tk.W)

            # --- Weight Slider ---
            # Initial weight from current preferences or default config
            initial_weight = current_preferences.get(category, DEFAULT_CATEGORIES_WITH_WEIGHTS.get(category, 0.5))
            self.weight_vars[category] = tk.DoubleVar(value=initial_weight)

            slider_frame = ttk.Frame(cat_frame)
            slider_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5))

            ttk.Label(slider_frame, text="Importance:").pack(side=tk.LEFT, padx=(0, 5))
            # ttk.Label(cat_frame, text="Importance:").grid(row=1, column=0, sticky=tk.W) # Old grid layout

            slider = ttk.Scale(slider_frame, from_=0.1, to=1.0,
                              variable=self.weight_vars[category],
                              orient=tk.HORIZONTAL, length=120, # Adjusted length
                              # Pass category to the command
                              command=lambda v, c=category: self._on_preference_change(c))
            # slider.grid(row=1, column=1, padx=5, sticky=tk.W+tk.E) # Old grid layout
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.sliders[category] = slider # Store slider to enable/disable

            # Set initial slider state based on checkbox
            self._update_slider_state(category)


    def _on_preference_change(self, category):
        """Callback when a category checkbox or slider changes."""
        is_selected = self.category_vars[category].get()
        weight = self.weight_vars[category].get()

        # Update slider enabled state
        self._update_slider_state(category)

        # Notify the app coordinator
        self.app.category_preference_updated(category, weight, is_selected)

    def _update_slider_state(self, category):
        """Enable/disable slider based on checkbox state."""
        slider = self.sliders.get(category)
        if slider:
            if self.category_vars[category].get():
                slider.config(state=tk.NORMAL)
            else:
                slider.config(state=tk.DISABLED)

    def load_preferences(self):
        """Reload preferences from the service (e.g., if reset externally)."""
        current_preferences = self.app.get_current_preferences().categories
        for category in self.categories:
            is_selected = category in current_preferences
            weight = current_preferences.get(category, DEFAULT_CATEGORIES_WITH_WEIGHTS.get(category, 0.5))
            self.category_vars[category].set(is_selected)
            self.weight_vars[category].set(weight)
            self._update_slider_state(category) # Update slider visibility