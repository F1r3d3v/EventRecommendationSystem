# models/user_preferences.py
from config import (
    DEFAULT_LOCATION, DEFAULT_MAX_DISTANCE, DEFAULT_MAX_BUDGET,
    DEFAULT_CATEGORIES_WITH_WEIGHTS
)

class UserPreferences:
    """Stores user preferences for event recommendations"""
    def __init__(self):
        self.location = DEFAULT_LOCATION.copy()
        self.max_distance = DEFAULT_MAX_DISTANCE
        # Category -> weight (0-1). Store only selected categories.
        self.categories = {}
        self.preferred_times = []  # List of (start_time, end_time) tuples
        # Category -> max budget (Optional, not fully implemented in calc logic yet)
        self.budget_categories = {}
        self.max_budget = DEFAULT_MAX_BUDGET
        self.attended_events = []  # List of Event objects (or IDs if preferred)

    def set_location(self, lat, lon):
        self.location["latitude"] = lat
        self.location["longitude"] = lon

    def set_max_distance(self, distance):
        self.max_distance = distance

    def set_max_budget(self, budget):
        self.max_budget = budget

    def set_category_preference(self, category, weight, is_selected):
        if is_selected:
            self.categories[category] = weight
        elif category in self.categories:
            del self.categories[category]

    def set_preferred_times(self, time_ranges):
        # Expects a list of (start_datetime, end_datetime) tuples
        self.preferred_times = time_ranges

    def add_attended_event(self, event):
        if event not in self.attended_events:
            self.attended_events.append(event)

    def remove_attended_event(self, event_to_remove):
         # Assumes attended_events stores actual Event objects
         self.attended_events = [e for e in self.attended_events if e.id != event_to_remove.id]

    def get_interest_match_inputs(self, event):
        """
        Calculates interest match score components based on preferences.
        Separated from direct score calculation to keep model focused on data.

        Args:
            event: Event object to evaluate

        Returns:
            Tuple: (match_score based on weights, boost_from_history)
                   Score is 0-100, boost is typically a small bonus (e.g., 10).
                   Returns (50, 0) if no preferences set for base score,
                   boost is calculated independently.
        """
        # --- Calculate Base Score ---
        if not self.categories:
            match_score = 50  # Neutral score if no preferences set
        else:
            # Ensure current event categories are always treated as a set
            
            current_event_categories = list()
            if isinstance(event.category, str):
                current_event_categories.append(event.category)
            elif isinstance(event.category, list):
                current_event_categories = event.category
            
            # Compute a score for each matching category independently
            matched_scores = [self.categories[cat] * 100 if cat in self.categories else 50 for cat in current_event_categories]
            match_score = sum(matched_scores) / len(matched_scores)

        # --- Calculate History Boost ---
        boost = 0
        if self.attended_events: # Only calculate boost if history exists
            # Ensure current event categories are a set (might recalculate but safer)
            current_event_categories_for_boost = set()
            if isinstance(event.category, str):
                current_event_categories_for_boost.add(event.category)
            elif isinstance(event.category, list):
                current_event_categories_for_boost.update(event.category)

            # Build set of all categories from attended events
            attended_categories_set = set()
            for attended_event in self.attended_events:
                if isinstance(attended_event.category, str):
                    attended_categories_set.add(attended_event.category)
                elif isinstance(attended_event.category, list):
                    attended_categories_set.update(attended_event.category)

            # Check for intersection
            if not current_event_categories_for_boost.isdisjoint(attended_categories_set):
                boost = 10 # Assign boost value if there's any overlap

        return match_score, boost

    def get_proximity_inputs(self, event):
        """
        Calculates distance relative to max distance.
        Separated calculation logic.

        Args:
            event: Event object with location data

        Returns:
            Tuple: (distance, max_distance)
        """
        distance = event.calculate_distance(self.location["latitude"], self.location["longitude"])
        return distance, self.max_distance

    def get_budget_inputs(self, event):
        """
        Provides event cost and user's max budget.
        Separated calculation logic.

        Args:
            event: Event object with cost data

        Returns:
            Tuple: (event_cost, max_budget)
        """
        # TODO: Implement category-specific budget logic if needed
        # current_max_budget = self.budget_categories.get(event.category, self.max_budget)
        current_max_budget = self.max_budget
        return event.cost, current_max_budget

    def get_time_overlap_inputs(self, event):
        """
        Provides event time and preferred times for overlap calculation.
        Separated calculation logic.

        Args:
            event: Event object with time data

        Returns:
            Tuple: (event_start, event_end, list_of_preferred_ranges)
                   Preferred ranges is a list of (start, end) datetime tuples.
        """
        return event.start_time, event.end_time, self.preferred_times