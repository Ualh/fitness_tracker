def get_activity_emoji(activity_type):
    """Get emoji for activity type"""
    from constants import get_activity_emoji as _get_emoji
    return _get_emoji(activity_type)

def format_duration(minutes):
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{int(minutes)}m"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {mins}m"

def get_intensity_color(intensity):
    """Get color for intensity level"""
    from constants import get_intensity_color as _get_color
    return _get_color(intensity)

def calculate_calories_estimate(activity_type, duration, intensity):
    """Rough calorie estimation based on activity type, duration and intensity"""
    from constants import calculate_calories_estimate as _calc_calories
    return _calc_calories(activity_type, duration, intensity)

def get_week_start(date):
    """Get the start of the week (Monday) for a given date"""
    from datetime import timedelta
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)

def format_date_range(start_date, end_date):
    """Format date range for display"""
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}"
        else:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    else:
        return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"

def validate_activity_data(activity_data):
    """Validate activity data before saving"""
    required_fields = ['type', 'duration', 'intensity', 'date']
    
    for field in required_fields:
        if field not in activity_data or activity_data[field] is None:
            return False, f"Missing required field: {field}"
    
    if activity_data['duration'] <= 0:
        return False, "Duration must be greater than 0"
    
    if activity_data['intensity'] not in ['Low', 'Medium', 'High']:
        return False, "Invalid intensity level"
    
    return True, "Valid"

def validate_weight_data(weight_data):
    """Validate weight data before saving"""
    required_fields = ['weight', 'date']
    
    for field in required_fields:
        if field not in weight_data or weight_data[field] is None:
            return False, f"Missing required field: {field}"
    
    if weight_data['weight'] <= 0 or weight_data['weight'] > 500:
        return False, "Weight must be between 0 and 500 kg"
    
    return True, "Valid"
