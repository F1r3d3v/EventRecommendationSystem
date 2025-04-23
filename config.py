# config.py

# Default User Preferences
DEFAULT_LOCATION = {"latitude": 37.7749, "longitude": -122.4194}  # San Francisco
DEFAULT_MAX_DISTANCE = 30  # kilometers
DEFAULT_MAX_BUDGET = 100
DEFAULT_CATEGORIES_WITH_WEIGHTS = {
    "Technology": 0.5,
    "Music": 0.5,
    "Food": 0.5,
    "Art": 0.5,
    "Fitness": 0.5,
    "Business": 0.5,
    "Entertainment": 0.5,
    "Education": 0.5,
    "Sports": 0.5,
}
# Extract just the category names for UI consistency
AVAILABLE_CATEGORIES = list(DEFAULT_CATEGORIES_WITH_WEIGHTS.keys())

# Map visualization settings (Simplified)
MAP_DEFAULT_CENTER_LAT = 37.7749
MAP_DEFAULT_CENTER_LON = -122.4194
MAP_LON_LIMITS = (-123.0, -122.0)
MAP_LAT_LIMITS = (37.5, 38.0)

# Recommendation Score Thresholds for UI coloring
SCORE_HIGH_THRESHOLD = 70
SCORE_MEDIUM_THRESHOLD = 30

# Score Visualization Colors
SCORE_LOW_COLOR = "#FF6B6B"  # Red
SCORE_MEDIUM_COLOR = "#FFD166"  # Yellow
SCORE_HIGH_COLOR = "#06D6A0"  # Green