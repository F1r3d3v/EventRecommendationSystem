import os

# Default settings for the application
DEFAULT_LOCATION = {"latitude": 51.81, "longitude": 22.0}  # Warsaw
DEFAULT_MAX_DISTANCE = 200  # kilometers
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

AVAILABLE_CATEGORIES = list(DEFAULT_CATEGORIES_WITH_WEIGHTS.keys())

# Map visualization settings
MAP_LON_LIMITS = (14.1, 24.2)  # Poland's approximate longitude limits
MAP_LAT_LIMITS = (49.0, 54.5)  # Poland's approximate latitude limits

# Recommendation Score Thresholds for UI coloring
SCORE_HIGH_THRESHOLD = 70
SCORE_MEDIUM_THRESHOLD = 30

# Score Visualization Colors
SCORE_LOW_COLOR = "#FF6B6B"  # Red
SCORE_MEDIUM_COLOR = "#FFD166"  # Yellow
SCORE_HIGH_COLOR = "#06D6A0"  # Green

# Resolution for 3d visualization
VISUALIZATION_RESOLUTION = 15 

# Path to the root directory of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))