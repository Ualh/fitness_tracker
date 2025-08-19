"""
Constants and configuration for the fitness tracker application.
Centralizes all constant values to eliminate duplication and improve maintainability.
"""

from typing import Dict, List, Tuple

# Activity Types and Emojis
ACTIVITY_TYPES: List[str] = [
    'Running', 'Walking', 'Cycling', 'Swimming', 'Hiking', 'Weightlifting',
    'Skiing', 'Back-country Skiing', 'Yoga', 'Rock Climbing', 'Boxing',
    'Basketball', 'Soccer', 'Tennis', 'CrossFit', 'Pilates', 'Dancing',
    'Martial Arts', 'Rowing', 'Bodyweight', 'Other'
]

ACTIVITY_EMOJIS: Dict[str, str] = {
    'Running': '🏃‍♂️',
    'Walking': '🚶‍♂️',
    'Cycling': '🚴‍♂️',
    'Swimming': '🏊‍♂️',
    'Hiking': '🥾',
    'Weightlifting': '🏋️‍♂️',
    'Skiing': '⛷️',
    'Back-country Skiing': '🎿',
    'Yoga': '🧘‍♂️',
    'Rock Climbing': '🧗‍♂️',
    'Boxing': '🥊',
    'Basketball': '🏀',
    'Soccer': '⚽',
    'Tennis': '🎾',
    'CrossFit': '💪',
    'Pilates': '🤸‍♂️',
    'Dancing': '💃',
    'Martial Arts': '🥋',
    'Rowing': '🚣‍♂️',
    'Bodyweight' : '⚖️',
    'Other': '💪'
}

# Intensity Levels
INTENSITY_LEVELS: List[str] = ['Low', 'Medium', 'High']

INTENSITY_COLORS: Dict[str, str] = {
    'Low': '#34C759',
    'Medium': '#FF9500',
    'High': '#FF3B30'
}

# Calorie Estimates (per minute)
BASE_CALORIES_PER_MINUTE: Dict[str, int] = {
    'Running': 12,
    'Walking': 4,
    'Cycling': 8,
    'Swimming': 11,
    'Hiking': 6,
    'Weightlifting': 6,
    'Skiing': 10,
    'Back-country Skiing': 12,
    'Yoga': 3,
    'Rock Climbing': 8,
    'Boxing': 10,
    'Basketball': 8,
    'Soccer': 9,
    'Tennis': 7,
    'CrossFit': 9,
    'Pilates': 4,
    'Dancing': 5,
    'Martial Arts': 8,
    'Rowing': 9,
    'Bodyweight' : 4,
    'Other': 5
}

INTENSITY_MULTIPLIERS: Dict[str, float] = {
    'Low': 0.8,
    'Medium': 1.0,
    'High': 1.3
}

# Database Configuration
DATABASE_CONFIG = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 10,
    'max_overflow': 20,
    'echo': False
}

# UI Configuration
STREAMLIT_CONFIG = {
    'page_title': 'Fitness Tracker',
    'page_icon': '🏃‍♂️',
    'layout': 'wide',
    'initial_sidebar_state': 'collapsed'
}

# Theme Colors
DARK_THEME_COLORS = {
    'primary': '#FF8C42',
    'secondary': '#E76E42',
    'background': '#1e1e1e',
    'surface': '#2d2d2d',
    'text': '#ffffff',
    'grid': '#3d3d3d',
    'border': '#3d3d3d'
}

LIGHT_THEME_COLORS = {
    'primary': '#8B9DC3',
    'secondary': '#A8B8C8',
    'background': 'white',
    'surface': '#f8f9fa',
    'text': '#333333',
    'grid': '#e0e0e0',
    'border': '#dee2e6'
}

# Chart Color Palettes
DARK_CHART_COLORS = [
    '#FF8C42', '#E76E42', '#CF5742', '#B74042', 
    '#9F2942', '#871242', '#6F0042', '#570042'
]

LIGHT_CHART_COLORS = [
    '#8B9DC3', '#A8B8C8', '#C5D0D8', '#B5C4D1', 
    '#9BACC0', '#D4DCE4', '#E1E8ED', '#F0F4F7'
]

# Data Schema
ACTIVITY_COLUMNS = [
    'id', 'type', 'duration', 'intensity', 
    'date', 'description', 'adaptation'
]

WEIGHT_COLUMNS = ['id', 'weight', 'date']

# Time Periods
TIME_PERIODS = ['Week', 'Month', 'Season', 'All time']

# Cache Configuration
CACHE_CONFIG = {
    'file_check_interval': 1.0,  # seconds
    'max_cache_age': 300,  # 5 minutes
    'enable_streamlit_cache': True
}

# Validation Rules
VALIDATION_RULES = {
    'min_duration': 1,
    'max_duration': 1440,  # 24 hours in minutes
    'min_weight': 20.0,
    'max_weight': 500.0,
    'max_description_length': 500,
    'username_min_length': 3,
    'username_max_length': 50,
    'password_min_length': 6
}

# Language Support
SUPPORTED_LANGUAGES = ['en', 'fr']
DEFAULT_LANGUAGE = 'en'

# File Paths
DATA_PATHS = {
    'activities': 'data/activities.json',
    'weight': 'data/weight.json',
    'settings': 'data/settings.json',
    'data_dir': 'data'
}

# Error Messages
ERROR_MESSAGES = {
    'file_not_found': 'Data file not found',
    'invalid_data': 'Invalid data format',
    'save_failed': 'Failed to save data',
    'load_failed': 'Failed to load data',
    'database_error': 'Database operation failed',
    'auth_failed': 'Authentication failed'
}

def get_activity_emoji(activity_type: str) -> str:
    """Get emoji for activity type with fallback."""
    return ACTIVITY_EMOJIS.get(activity_type, '💪')

def get_intensity_color(intensity: str) -> str:
    """Get color for intensity level with fallback."""
    return INTENSITY_COLORS.get(intensity, '#007AFF')

def calculate_calories_estimate(activity_type: str, duration: int, intensity: str) -> int:
    """Calculate calorie estimate based on activity, duration, and intensity."""
    base_cal_per_min = BASE_CALORIES_PER_MINUTE.get(activity_type, 5)
    multiplier = INTENSITY_MULTIPLIERS.get(intensity, 1.0)
    return int(base_cal_per_min * duration * multiplier)

def get_theme_colors(dark_mode: bool) -> Dict[str, str]:
    """Get theme colors based on mode."""
    return DARK_THEME_COLORS if dark_mode else LIGHT_THEME_COLORS

def get_chart_colors(dark_mode: bool) -> List[str]:
    """Get chart color palette based on theme."""
    return DARK_CHART_COLORS if dark_mode else LIGHT_CHART_COLORS
