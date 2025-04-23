# models/event.py
from datetime import datetime
import math

class Event:
    """Represents an event in the system"""
    def __init__(self, id, name, description, category, start_time, end_time,
                 latitude, longitude, cost, popularity=0):
        self.id = id
        self.name = name
        self.description = description
        self.category = category  # Category string or list of categories
        self.start_time = start_time  # datetime object
        self.end_time = end_time  # datetime object
        self.latitude = latitude
        self.longitude = longitude
        self.cost = cost
        self.popularity = popularity # Currently unused but kept

        # Results from recommendation calculation - managed by RecommendationService
        self.recommendation_score = 0
        self.scores_breakdown = {
            "interest_match": 0,
            "location_proximity": 0,
            "time_overlap": 0,
            "budget_alignment": 0,
        }

    def calculate_distance(self, user_lat, user_lon):
        """Calculate distance in kilometers between event location and user location"""
        # Haversine formula
        R = 6371.0  # Earth radius in kilometers

        lat1_rad = math.radians(user_lat)
        lon1_rad = math.radians(user_lon)
        lat2_rad = math.radians(self.latitude)
        lon2_rad = math.radians(self.longitude)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def __eq__(self, other):
        if not isinstance(other, Event):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"Event(id={self.id}, name='{self.name}')"

    def __repr__(self):
        return self.__str__()