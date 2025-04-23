# gui/budget_panel.py
import tkinter as tk
from tkinter import ttk
from config import AVAILABLE_CATEGORIES

class BudgetPanel(ttk.Frame):
    """Panel for setting general and category-specific budget preferences."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator # Reference to the main app coordinator

        # Get initial preferences
        prefs = self.app.get_current_preferences()
        initial_budget = prefs.max_budget
        # initial_cat_budgets = prefs.budget_categories # TODO: Use if implementing cat budgets

        # --- General Budget ---
        budget_frame = ttk.LabelFrame(self, text="Maximum Budget (Overall)")
        budget_frame.pack(fill=tk.X, padx=10, pady=10)

        self.budget_var = tk.IntVar(value=initial_budget)
        # Update label width for consistent alignment
        self.budget_label = ttk.Label(budget_frame, text=f"${initial_budget}", width=8, anchor=tk.E)
        self.budget_label.pack(side=tk.RIGHT, padx=(5, 10), pady=5)

        budget_slider = ttk.Scale(budget_frame, from_=0, to=500, # Adjusted range if needed
                                 variable=self.budget_var, orient=tk.HORIZONTAL,
                                 command=self._on_general_budget_change)
        budget_slider.pack(fill=tk.X, padx=10, pady=5, expand=True)

        # --- Category-Specific Budgets (Optional - Placeholder) ---
        # This section is kept minimal as the core calculation logic doesn't use it yet.
        cat_budget_frame = ttk.LabelFrame(self, text="Category-Specific Budgets (Future Feature)")
        cat_budget_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(cat_budget_frame, text="Category-specific budget overrides are not yet fully implemented.").pack(pady=10)

        # Example setup if you were to implement it fully:
        # categories = AVAILABLE_CATEGORIES
        # self.cat_budget_vars = {}
        # self.cat_enabled_vars = {}
        # cols = 2
        # for i, category in enumerate(categories):
        #     row, col = divmod(i, cols)
        #     cat_frame = ttk.Frame(cat_budget_frame)
        #     cat_frame.grid(row=row, column=col, padx=10, pady=5, sticky=tk.W)
        #     # ... Checkbox, Spinbox/Entry for each category ...
        #     # Ensure command calls self._notify_app_category_budget(category)

    def _on_general_budget_change(self, value_str):
        """Handle general budget slider change."""
        budget = int(float(value_str))
        self.budget_label.config(text=f"${budget}")
        self._notify_app_general_budget()

    def _notify_app_general_budget(self):
        """Inform the app coordinator about the general budget change."""
        budget = self.budget_var.get()
        self.app.budget_preference_updated(budget) # Single callback for now

    # def _notify_app_category_budget(self, category):
    #     """Inform the app about a category-specific budget change (if implemented)."""
    #     # Get enabled status and budget value for the category
    #     # Call a dedicated app method like:
    #     # self.app.category_budget_updated(category, budget, is_enabled)
    #     pass # Placeholder

    def load_preferences(self):
        """Loads general budget preference from the service."""
        prefs = self.app.get_current_preferences()
        budget = prefs.max_budget
        self.budget_var.set(budget)
        self.budget_label.config(text=f"${budget}")
        # TODO: Load category-specific budgets if implemented