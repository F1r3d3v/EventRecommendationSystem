# services/recommendation_service.py
from datetime import datetime
import math
import numpy as np

from fuzzy.fuzzy_system import EventFuzzySystem
from models.event import Event
from models.user_preferences import UserPreferences

class RecommendationService:
    """Handles the core logic for event recommendation and data management."""
    def __init__(self):
        self.fuzzy_system = EventFuzzySystem()
        self.user_preferences = UserPreferences()
        self.events = self._load_sample_events() # Store the canonical list of events

    def _load_sample_events(self):
        """Load sample events for testing"""
        now = datetime.now()
        # (Same sample event creation logic as before)
        events_data = [
             (1, "Tech Conference 2025", "The latest in technology trends and innovations",
                 "Technology", now.replace(hour=9), now.replace(hour=17),
                 37.7749, -122.4194, 150, 80),
             (2, "Summer Music Festival", "Outdoor music festival featuring top artists",
                 "Music", now.replace(hour=18), now.replace(hour=23),
                 37.7694, -122.4862, 75, 90),
             (3, "Farmers Market", "Local produce and handcrafted goods",
                 "Food", now.replace(hour=8), now.replace(hour=13),
                 37.7800, -122.4400, 0, 70),
             (4, "Cooking Workshop", "Learn to cook international cuisine",
                 "Food", now.replace(hour=14), now.replace(hour=16),
                 37.7844, -122.4079, 45, 60),
             (5, "Art Gallery Opening", "New exhibition featuring local artists",
                 "Art", now.replace(hour=19), now.replace(hour=22),
                 37.7861, -122.4025, 10, 75),
             (6, "Yoga in the Park", "Morning yoga session for all levels",
                 "Fitness", now.replace(hour=7), now.replace(hour=8),
                 37.7699, -122.4830, 5, 65),
             (7, "Business Networking", "Connect with professionals in your industry",
                 "Business", now.replace(hour=17), now.replace(hour=19),
                 37.7909, -122.4012, 20, 50),
             (8, "Film Festival", "Independent and international films",
                 "Entertainment", now.replace(hour=15), now.replace(hour=23),
                 37.7833, -122.4167, 15, 85),
             (9, "Science Museum Exhibition", "Interactive science exhibits for all ages",
                 "Education", now.replace(hour=10), now.replace(hour=16),
                 37.7692, -122.4669, 25, 60),
             (10, "Charity Run", "5K run to support local charity",
                 "Sports", now.replace(hour=8), now.replace(hour=11),
                 37.7812, -122.4230, 30, 40)
        ]
        return [Event(*data) for data in events_data]

    def get_preferences(self):
        """Return the current user preferences object."""
        return self.user_preferences

    def update_location_preference(self, lat, lon, max_distance):
        """Update location preferences."""
        self.user_preferences.set_location(lat, lon)
        self.user_preferences.set_max_distance(max_distance)

    def update_category_preference(self, category, weight, is_selected):
        """Update a single category preference."""
        self.user_preferences.set_category_preference(category, weight, is_selected)

    def update_time_preferences(self, time_ranges):
        """Update preferred time ranges."""
        self.user_preferences.set_preferred_times(time_ranges)

    def update_budget_preference(self, max_budget):
        """Update the maximum budget preference."""
        self.user_preferences.set_max_budget(max_budget)
        # TODO: Add logic for category-specific budgets if needed

    def get_history(self):
        """Return the list of attended events."""
        return self.user_preferences.attended_events

    def add_event_to_history(self, event):
        """Add an event to the user's history."""
        self.user_preferences.add_attended_event(event)

    def remove_event_from_history(self, event):
        """Remove an event from the user's history."""
        self.user_preferences.remove_attended_event(event)

    def get_recommended_events(self, sort_key="Recommendation", search_term=None):
        """
        Calculate recommendations for all events and return a sorted, filtered list.
        """
        processed_events = []
        for event in self.events:
            # 1. Calculate input scores (0-100) for the fuzzy system
            # Ensure we get both values back correctly
            interest_score, history_boost = self._calculate_interest_match_score(event) # Calls the updated UserPrefs method
            proximity_score = self._calculate_location_proximity_score(event)
            time_score = self._calculate_time_overlap_score(event)
            budget_score = self._calculate_budget_alignment_score(event)

            # Apply history boost directly to interest score before fuzzy logic
            interest_score_boosted = min(100, interest_score + history_boost) # Ensure capping at 100

            # --- Debug Print (Optional) ---
            # if history_boost > 0:
            #     print(f"Event: {event.name}, Base Interest: {interest_score:.1f}, Boost: {history_boost}, Boosted Interest: {interest_score_boosted:.1f}")
            # ---

            # 2. Evaluate through fuzzy system using the boosted score
            recommendation_score = self.fuzzy_system.evaluate(
                interest_score_boosted, # Use the boosted score here
                proximity_score,
                time_score,
                budget_score
            )

            # 3. Store results in the event object
            event.recommendation_score = recommendation_score
            # --- Ensure correct keys and values are stored ---
            event.scores_breakdown = {
                "interest_match": interest_score, # Store original score without boost for display
                "interest_match_boosted": interest_score_boosted, # Store boosted score used in fuzzy calc
                "location_proximity": proximity_score,
                "time_overlap": time_score,
                "budget_alignment": budget_score,
                "history_boost": history_boost, # Store the boost amount itself
            }
            # --- End Store Check ---
            processed_events.append(event)

        # 4. Filter events
        filtered_events = self._filter_events(processed_events, search_term)

        # 5. Sort events
        sorted_events = self._sort_events(filtered_events, sort_key)

        return sorted_events

    # --- Make sure _calculate_interest_match_score just passes through ---
    def _calculate_interest_match_score(self, event):
        """Calculate interest match score (0-100) and history boost."""
        # This correctly calls the UserPreferences method which does the work
        match_score, boost = self.user_preferences.get_interest_match_inputs(event)
        return match_score, boost

    def get_event_by_id(self, event_id):
        """Find an event by its ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    # --- Private Helper Methods for Score Calculation ---

    def _calculate_interest_match_score(self, event):
        """Calculate interest match score (0-100) and history boost."""
        match_score, boost = self.user_preferences.get_interest_match_inputs(event)
        # The raw score and boost are returned separately.
        # The boost will be added before feeding to the fuzzy system if desired.
        return match_score, boost

    def _calculate_location_proximity_score(self, event):
        """Calculate location proximity score (0-100, higher = closer)."""
        distance, max_distance = self.user_preferences.get_proximity_inputs(event)

        if max_distance <= 0: return 50 # Avoid division by zero, return neutral
        if distance <= 0: return 100

        # Linear scaling: score decreases as distance increases up to max_distance
        # Score is 100 at distance 0, 0 at distance max_distance
        score = 100 * (1 - min(distance / max_distance, 1.0))

        # Optional: Penalize further for distances beyond max_distance
        # if distance > max_distance:
        #    score = max(0, score - ((distance - max_distance) / max_distance * 50)) # Example penalty

        return max(0, min(100, score)) # Clamp score between 0 and 100


    def _calculate_time_overlap_score(self, event):
        """Calculate time overlap score (0-100)."""
        event_start, event_end, preferred_times = self.user_preferences.get_time_overlap_inputs(event)

        if not preferred_times:
            return 50  # Neutral if no preferences

        event_duration_sec = (event_end - event_start).total_seconds()
        if event_duration_sec <= 0:
            return 0 # Event has no duration

        total_overlap_sec = 0
        for pref_start, pref_end in preferred_times:
            # Ensure consistent timezone awareness or lack thereof if necessary
            # Calculate overlap interval
            overlap_start = max(event_start, pref_start)
            overlap_end = min(event_end, pref_end)

            # Calculate overlap duration in seconds
            if overlap_end > overlap_start:
                overlap_duration = (overlap_end - overlap_start).total_seconds()
                total_overlap_sec += overlap_duration

        # Normalize overlap by event duration
        overlap_percentage = (total_overlap_sec / event_duration_sec) * 100
        return max(0, min(100, overlap_percentage)) # Clamp score

    def _calculate_budget_alignment_score(self, event):
        """Calculate budget alignment score (0-100, higher = better fit)."""
        event_cost, max_budget = self.user_preferences.get_budget_inputs(event)

        if event_cost <= 0:
            return 100  # Free events are perfect matches

        if max_budget <= 0:
             # User has no budget, but event costs money
             return 0 if event_cost > 0 else 100

        if event_cost <= max_budget:
            # Within budget: Score higher for cheaper events relative to budget
            # Linear scale from 100 (cost=0) down to e.g., 70 (cost=max_budget)
            score = 100 - (event_cost / max_budget) * 30
        else:
            # Over budget: Score decreases rapidly
            # Linear scale from e.g., 30 (cost just over budget) down to 0
            over_ratio = (event_cost - max_budget) / max_budget
            score = 30 * (1 - min(over_ratio, 1.0)) # Example: Score hits 0 when cost is 2x budget

        return max(0, min(100, score)) # Clamp score

    # --- Private Helper Methods for Filtering/Sorting ---

    def _filter_events(self, events, search_term):
        """Filter events based on search term."""
        if not search_term:
            return events

        search_term_lower = search_term.lower()
        return [
            e for e in events if
            search_term_lower in e.name.lower() or
            search_term_lower in e.description.lower() or
            (isinstance(e.category, str) and search_term_lower in e.category.lower()) or
            (isinstance(e.category, list) and any(search_term_lower in cat.lower() for cat in e.category))
        ]

    def _sort_events(self, events, sort_key):
        """Sort events based on the specified key."""
        reverse_sort = False
        sort_lambda = None

        if sort_key == "Recommendation":
            sort_lambda = lambda e: e.recommendation_score
            reverse_sort = True
        elif sort_key == "Name":
            sort_lambda = lambda e: e.name
        elif sort_key == "Time":
            sort_lambda = lambda e: e.start_time
        elif sort_key == "Cost":
            sort_lambda = lambda e: e.cost
        elif sort_key == "Distance":
            user_lat = self.user_preferences.location["latitude"]
            user_lon = self.user_preferences.location["longitude"]
            # Calculate distance only for sorting if needed, or use a stored proximity score
            sort_lambda = lambda e: e.calculate_distance(user_lat, user_lon)
            # Alternatively use stored proximity score (lower score = further away)
            # sort_lambda = lambda e: e.scores_breakdown.get("location_proximity", 100) # Default 100 if score missing
            # reverse_sort = False # Lower score is further, sort ascending

        if sort_lambda:
            return sorted(events, key=sort_lambda, reverse=reverse_sort)
        else:
            return events # Return unsorted if key is unknown