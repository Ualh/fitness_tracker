"""
Performance optimization utilities for the fitness tracker app
"""
import streamlit as st
import pandas as pd
from functools import wraps
import time

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_dataframe_operations(df, operation, **kwargs):
    """Cache common DataFrame operations to avoid repeated computations"""
    if operation == "value_counts":
        column = kwargs.get('column')
        if column and column in df.columns:
            return df[column].value_counts()
    elif operation == "groupby_sum":
        group_col = kwargs.get('group_col')
        sum_col = kwargs.get('sum_col')
        if group_col and sum_col and group_col in df.columns and sum_col in df.columns:
            return df.groupby(group_col)[sum_col].sum()
    elif operation == "date_filter":
        date_col = kwargs.get('date_col', 'date')
        start_date = kwargs.get('start_date')
        if date_col in df.columns and start_date:
            return df[df[date_col] >= start_date]
    return df

def compute_summary_stats_v2(activities_df):
    """Compute summary statistics without caching to avoid cache issues"""
    if activities_df.empty:
        return {
            'total_activities': 0,
            'total_time': 0,
            'avg_intensity': 0,
            'most_common_activity': 'None'
        }
    
    total_activities = len(activities_df)
    total_time = activities_df['duration'].sum() if 'duration' in activities_df.columns else 0
    
    # Calculate intensity average safely
    avg_intensity = 0
    if 'intensity' in activities_df.columns and not activities_df.empty:
        try:
            # Map intensity strings to numeric values
            intensity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
            
            # Apply mapping and handle any unmapped values
            mapped_values = []
            for intensity in activities_df['intensity']:
                if intensity in intensity_mapping:
                    mapped_values.append(intensity_mapping[intensity])
            
            # Calculate average if we have valid values
            if mapped_values:
                avg_intensity = sum(mapped_values) / len(mapped_values)
        except Exception:
            avg_intensity = 0
    
    if 'type' in activities_df.columns:
        try:
            most_common = activities_df['type'].value_counts()
            most_common_activity = most_common.index[0] if not most_common.empty else 'None'
        except Exception:
            most_common_activity = 'None'
    else:
        most_common_activity = 'None'
    
    return {
        'total_activities': total_activities,
        'total_time': int(total_time),
        'avg_intensity': round(avg_intensity, 1),
        'most_common_activity': most_common_activity
    }

def efficient_dataframe_filter(df, period="All time"):
    """Efficiently filter DataFrame by period without repeated datetime operations"""
    if df.empty or period == "All time":
        return df
    
    from datetime import datetime, timedelta
    now = datetime.now()
    
    period_days = {
        "Week": 7,
        "Month": 30,
        "Season": 90
    }
    
    days = period_days.get(period)
    if not days:
        return df
    
    start_date = now - timedelta(days=days)
    
    if 'date' in df.columns:
        # Use pandas native filtering for better performance
        return df[df['date'] >= start_date].copy()
    
    return df

def performance_monitor(func):
    """Decorator to monitor function performance (development only)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if st.session_state.get('debug_mode', False):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            st.sidebar.caption(f"{func.__name__}: {(end_time - start_time):.3f}s")
            return result
        else:
            return func(*args, **kwargs)
    return wrapper