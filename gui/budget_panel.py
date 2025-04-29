import tkinter as tk
from tkinter import ttk

class BudgetPanel(ttk.Frame):
    """Panel for setting general and category-specific budget preferences."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator

        # Get initial preferences
        prefs = self.app.get_current_preferences()
        initial_budget = prefs.max_budget

        # --- General Budget ---
        budget_frame = ttk.LabelFrame(self, text="Maximum Budget (Overall)")
        budget_frame.pack(fill=tk.X, padx=10, pady=10)

        self.budget_var = tk.IntVar(value=initial_budget)
        self.budget_label = ttk.Label(budget_frame, text=f"${initial_budget}", width=8, anchor=tk.E)
        self.budget_label.pack(side=tk.RIGHT, padx=(5, 10), pady=5)

        budget_slider = ttk.Scale(budget_frame, from_=0, to=500,
                                 variable=self.budget_var, orient=tk.HORIZONTAL,
                                 command=self._on_general_budget_change)
        budget_slider.pack(fill=tk.X, padx=10, pady=5, expand=True)

    def _on_general_budget_change(self, value_str):
        """Handle general budget slider change."""
        budget = int(float(value_str))
        self.budget_label.config(text=f"${budget}")
        self._notify_app_general_budget()

    def _notify_app_general_budget(self):
        """Inform the app coordinator about the general budget change."""
        budget = self.budget_var.get()
        self.app.budget_preference_updated(budget)

    def load_preferences(self):
        """Loads general budget preference from the service."""
        prefs = self.app.get_current_preferences()
        budget = prefs.max_budget
        self.budget_var.set(budget)
        self.budget_label.config(text=f"${budget}")
