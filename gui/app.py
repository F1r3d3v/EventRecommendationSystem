# gui/app.py
import tkinter as tk
from tkinter import ttk

# Assuming RecommendationService handles Event loading now
from services.recommendation_service import RecommendationService
from models.event import Event # May not be needed directly here anymore

from gui.location_panel import LocationPanel
from gui.preference_panel import PreferencePanel
from gui.event_list_panel import EventListPanel
from gui.event_details_panel import EventDetailsPanel # New Panel
from gui.time_panel import TimePreferencePanel
from gui.budget_panel import BudgetPanel
from gui.history_panel import HistoryPanel
from gui.fuzzy_visualization import FuzzyVisualizationPanel


class EventRecommenderApp:
    """Main application class for the Event Recommender System (Coordinator)"""
    def __init__(self, root):
        self.root = root
        # Core service layer holds state and logic
        self.service = RecommendationService()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tab frames
        self.main_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.system_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.main_tab, text="Recommendations")
        self.notebook.add(self.settings_tab, text="Preferences")
        self.notebook.add(self.history_tab, text="History")
        self.notebook.add(self.system_tab, text="System")

        # Setup main recommendation tab
        self._setup_main_tab()

        # Setup preferences tab
        self._setup_preferences_tab()

        # Setup history tab
        self._setup_history_tab()

        # Setup system tab
        self._setup_system_tab()

        # Initial population of recommendations
        self.refresh_recommendations()
        # Select the first event initially if any
        self.event_list_panel.select_first()


    def _setup_main_tab(self):
        """Setup the main recommendations tab"""
        main_paned = ttk.PanedWindow(self.main_tab, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - Event list
        # Pass 'self' (the app coordinator) to the panels for callbacks
        self.event_list_panel = EventListPanel(main_paned, self)
        main_paned.add(self.event_list_panel, weight=1) # Add list first

        # Right panel - Event details (Now a separate panel)
        self.event_details_panel = EventDetailsPanel(main_paned, self)
        main_paned.add(self.event_details_panel, weight=1)


    def _setup_preferences_tab(self):
        """Setup the preferences tab"""
        pref_notebook = ttk.Notebook(self.settings_tab)
        pref_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Panels now take `self` (app coordinator)
        self.location_panel = LocationPanel(pref_notebook, self)
        pref_notebook.add(self.location_panel, text="Location")

        self.preference_panel = PreferencePanel(pref_notebook, self)
        pref_notebook.add(self.preference_panel, text="Categories")

        self.time_panel = TimePreferencePanel(pref_notebook, self)
        pref_notebook.add(self.time_panel, text="Time")

        self.budget_panel = BudgetPanel(pref_notebook, self)
        pref_notebook.add(self.budget_panel, text="Budget")

        # Apply button removed - changes apply more dynamically via callbacks
        # We might add an explicit "Refresh Recommendations" button if needed
        # apply_frame = ttk.Frame(self.settings_tab)
        # apply_frame.pack(fill=tk.X, padx=10, pady=10)
        # ttk.Button(apply_frame, text="Apply Preferences",
        #           command=self.refresh_recommendations).pack(side=tk.RIGHT)


    def _setup_history_tab(self):
        """Setup the event history tab"""
        self.history_panel = HistoryPanel(self.history_tab, self)
        self.history_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


    def _setup_system_tab(self):
        """Setup the system visualization tab"""
        # Pass the fuzzy system instance from the service
        self.system_panel = FuzzyVisualizationPanel(self.system_tab, self.service.fuzzy_system)
        self.system_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Callback Methods for UI Panels ---

    def refresh_recommendations(self):
        """Requests new recommendations from the service and updates the UI."""
        # Get sort/filter criteria from the event list panel
        sort_key = self.event_list_panel.get_sort_key()
        search_term = self.event_list_panel.get_search_term()

        # Get recommendations from the service
        recommended_events = self.service.get_recommended_events(sort_key, search_term)

        # Update the event list panel
        self.event_list_panel.display_events(recommended_events)

        # Clear details panel if no events match
        if not recommended_events:
             self.event_details_panel.clear_details()
        # else: # Optionally select the first one after refresh
        #     self.event_list_panel.select_first()


    def event_selected(self, event):
        """Called by EventListPanel when an event is selected."""
        if event:
            self.event_details_panel.display_event_details(event)
        else:
            self.event_details_panel.clear_details()

    def request_add_to_history(self, event):
        """Called by EventDetailsPanel to add the event to history."""
        if event:
            self.service.add_event_to_history(event)
            # Update history view
            self.history_panel.update_history_display()
            # Re-calculate recommendations as history influences scores
            self.refresh_recommendations()

    def request_remove_from_history(self, event):
        """Called by HistoryPanel to remove an event."""
        if event:
             self.service.remove_event_from_history(event)
             self.history_panel.update_history_display()
             self.refresh_recommendations() # History changed, update recommendations

    def location_preference_updated(self, lat, lon, max_distance):
        """Called by LocationPanel when location/distance changes."""
        self.service.update_location_preference(lat, lon, max_distance)
        self.refresh_recommendations()

    def category_preference_updated(self, category, weight, is_selected):
         """Called by PreferencePanel."""
         self.service.update_category_preference(category, weight, is_selected)
         self.refresh_recommendations()

    def time_preference_updated(self, time_ranges):
        """Called by TimePreferencePanel."""
        self.service.update_time_preferences(time_ranges)
        self.refresh_recommendations()

    def budget_preference_updated(self, max_budget):
        """Called by BudgetPanel."""
        self.service.update_budget_preference(max_budget)
        self.refresh_recommendations()

    def get_current_preferences(self):
        """Provide access to preferences for panels that need initial state."""
        return self.service.get_preferences()

    def get_history_data(self):
        """Provide history data for the HistoryPanel."""
        return self.service.get_history()

    # --- End Callback Methods ---

# Note: _load_sample_events is removed from App, now handled by RecommendationService