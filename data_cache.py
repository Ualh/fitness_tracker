"""
Advanced caching layer for fitness tracker data operations
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from functools import lru_cache

# Global cache for frequently accessed data
@st.cache_data(ttl=600, max_entries=100)
def get_filtered_activities_cache(user_id, period, activities_hash=None):
    """Cache filtered activities by user and period with hash for invalidation"""
    # This function works with the hash of activities to ensure cache invalidation
    # when data changes. The actual filtering is done by the caller.
    return None

@st.cache_data(ttl=300)
def compute_activity_metrics(activities_count, total_duration, intensity_values):
    """Cache computation of activity metrics"""
    if activities_count == 0:
        return {
            'total_activities': 0,
            'total_time': 0,
            'avg_intensity': 0,
            'formatted_time': "0 min"
        }
    
    from utils import format_duration
    
    avg_intensity = sum(intensity_values) / len(intensity_values) if intensity_values else 0
    
    return {
        'total_activities': activities_count,
        'total_time': total_duration,
        'avg_intensity': avg_intensity,
        'formatted_time': format_duration(total_duration)
    }

@st.cache_data(ttl=1800)  # 30 minutes cache
def get_activity_type_distribution(activity_types_list):
    """Cache activity type distribution calculations"""
    if not activity_types_list:
        return {}
    
    # Count occurrences
    type_counts = {}
    for activity_type in activity_types_list:
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
    
    return type_counts

@st.cache_data(ttl=900)  # 15 minutes cache
def get_weekly_activity_summary(dates_list, types_list, durations_list):
    """Cache weekly activity summary calculations"""
    if not dates_list or not types_list or not durations_list:
        return pd.DataFrame()
    
    # Create temporary dataframe for processing
    temp_df = pd.DataFrame({
        'date': pd.to_datetime(dates_list),
        'type': types_list,
        'duration': durations_list
    })
    
    # Group by week
    temp_df['week'] = temp_df['date'].dt.to_period('W').dt.start_time
    weekly_summary = temp_df.groupby(['week', 'type'])['duration'].sum().reset_index()
    
    return weekly_summary

class DataCacheManager:
    """Manages data caching for optimal performance"""
    
    def __init__(self):
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    def get_cache_key(self, user_id, period, data_type):
        """Generate consistent cache keys"""
        return f"{data_type}_{user_id}_{period}_{int(time.time() / 300)}"  # 5-minute buckets
    
    def should_refresh_cache(self, last_update, ttl_minutes=5):
        """Check if cache should be refreshed"""
        if not last_update:
            return True
        return (datetime.now() - last_update).total_seconds() > (ttl_minutes * 60)
    
    @st.cache_data(ttl=180)  # 3 minutes for very frequently accessed data
    def get_user_summary_fast(_self, user_id, activities_data_hash):
        """Ultra-fast user summary for dashboard"""
        # This is called with a hash of the activities data
        # to ensure cache invalidation when data changes
        return {'cached': True, 'timestamp': datetime.now()}

# Singleton cache manager
cache_manager = DataCacheManager()