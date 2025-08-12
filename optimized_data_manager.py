"""
Optimized DataManager with improved performance and clean code practices.
"""

import json
import pandas as pd
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Union
from constants import (
    DATA_PATHS, ACTIVITY_COLUMNS, WEIGHT_COLUMNS, 
    CACHE_CONFIG, VALIDATION_RULES, ERROR_MESSAGES
)


class OptimizedDataManager:
    """
    Enhanced DataManager with performance optimizations and better error handling.
    """
    
    def __init__(self):
        """Initialize with configuration from constants."""
        self.activities_file = DATA_PATHS['activities']
        self.weight_file = DATA_PATHS['weight']
        self.settings_file = DATA_PATHS['settings']
        
        # Ensure data directory exists
        self._ensure_data_directory()
        self._init_data_files()
        
        # Cache configuration
        self._cache_config = CACHE_CONFIG
        self._activities_cache = None
        self._weight_cache = None
        self._activities_cache_timestamp = 0
        self._weight_cache_timestamp = 0
    
    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist."""
        os.makedirs(DATA_PATHS['data_dir'], exist_ok=True)
    
    def _init_data_files(self) -> None:
        """Initialize data files with proper error handling."""
        default_files = {
            self.activities_file: [],
            self.weight_file: [],
            self.settings_file: {"weight_goal": None}
        }
        
        for file_path, default_data in default_files.items():
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w') as f:
                        json.dump(default_data, f, indent=2)
                except OSError as e:
                    print(f"Error creating {file_path}: {e}")
    
    def _create_empty_activities_df(self) -> pd.DataFrame:
        """Create properly typed empty activities DataFrame."""
        return pd.DataFrame(columns=ACTIVITY_COLUMNS).astype({
            'id': 'string',
            'type': 'string', 
            'duration': 'int64',
            'intensity': 'string',
            'description': 'string',
            'adaptation': 'string'
        })
    
    def _create_empty_weight_df(self) -> pd.DataFrame:
        """Create properly typed empty weight DataFrame."""
        return pd.DataFrame(columns=WEIGHT_COLUMNS).astype({
            'id': 'string',
            'weight': 'float64'
        })
    
    def _is_cache_valid(self, file_path: str, cache_timestamp: float) -> bool:
        """Check if cache is still valid based on file modification time."""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_mtime = os.path.getmtime(file_path)
            cache_age = time.time() - cache_timestamp
            
            return (file_mtime <= cache_timestamp and 
                    cache_age < self._cache_config['max_cache_age'])
        except OSError:
            return False
    
    def load_activities(self) -> pd.DataFrame:
        """Load activities with intelligent caching and error handling."""
        try:
            # Check cache validity
            if (self._activities_cache is not None and 
                self._is_cache_valid(self.activities_file, self._activities_cache_timestamp)):
                return self._activities_cache.copy()
            
            # Load fresh data
            if not os.path.exists(self.activities_file):
                return self._create_empty_activities_df()
            
            with open(self.activities_file, 'r') as f:
                activities = json.load(f)
            
            if not activities:
                df = self._create_empty_activities_df()
            else:
                df = pd.DataFrame(activities)
                df['date'] = pd.to_datetime(df['date'])
                
                # Ensure backward compatibility
                if 'adaptation' not in df.columns:
                    df['adaptation'] = None
                    
                df = df.sort_values('date', ascending=False)
            
            # Update cache
            self._activities_cache = df.copy()
            self._activities_cache_timestamp = time.time()
            return df
            
        except (json.JSONDecodeError, OSError, KeyError) as e:
            print(f"{ERROR_MESSAGES['load_failed']}: {e}")
            return self._create_empty_activities_df()
    
    def save_activities(self, df: pd.DataFrame) -> bool:
        """Save activities with atomic write and cache update."""
        try:
            # Prepare data for JSON serialization
            activities_list = df.copy()
            if not activities_list.empty and 'date' in activities_list.columns:
                activities_list['date'] = activities_list['date'].astype(str)
            
            activities_data = activities_list.to_dict('records')
            
            # Atomic write using temporary file
            temp_file = f"{self.activities_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(activities_data, f, indent=2)
            
            # Replace original file atomically
            os.replace(temp_file, self.activities_file)
            
            # Update cache
            self._activities_cache = df.copy()
            self._activities_cache_timestamp = time.time()
            
            return True
            
        except (OSError, json.JSONEncodeError) as e:
            print(f"{ERROR_MESSAGES['save_failed']}: {e}")
            # Clean up temp file if it exists
            if os.path.exists(f"{self.activities_file}.tmp"):
                os.remove(f"{self.activities_file}.tmp")
            return False
    
    def add_activity(self, activity_data: Dict) -> bool:
        """Add activity with validation and proper error handling."""
        try:
            # Validate input data
            if not self._validate_activity_data(activity_data):
                return False
            
            df = self.load_activities()
            
            # Prepare activity data
            activity_data['id'] = str(uuid.uuid4())
            if isinstance(activity_data['date'], str):
                activity_data['date'] = datetime.fromisoformat(activity_data['date'])
            
            # Add to DataFrame efficiently
            new_row = pd.DataFrame([activity_data])
            df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
            
            return self.save_activities(df)
            
        except (ValueError, TypeError) as e:
            print(f"Error adding activity: {e}")
            return False
    
    def _validate_activity_data(self, data: Dict) -> bool:
        """Validate activity data according to rules."""
        required_fields = ['type', 'duration', 'intensity', 'date']
        
        # Check required fields
        if not all(field in data for field in required_fields):
            return False
        
        # Validate duration
        duration = data.get('duration')
        if not isinstance(duration, (int, float)) or not (
            VALIDATION_RULES['min_duration'] <= duration <= VALIDATION_RULES['max_duration']
        ):
            return False
        
        # Validate description length
        description = data.get('description', '')
        if len(description) > VALIDATION_RULES['max_description_length']:
            return False
        
        return True
    
    def delete_activity(self, activity_id: str) -> bool:
        """Delete activity with proper error handling."""
        try:
            df = self.load_activities()
            if df.empty or activity_id not in df['id'].values:
                return False
            
            df = df[df['id'] != activity_id]
            return self.save_activities(df)
            
        except Exception as e:
            print(f"Error deleting activity: {e}")
            return False
    
    def get_activities_for_period(self, period: str) -> pd.DataFrame:
        """Get activities for specified period with optimized filtering."""
        df = self.load_activities()
        if df.empty or period == "All time":
            return df
        
        # Period mapping for better performance
        period_days = {
            "Week": 7,
            "Month": 30,
            "Season": 90
        }
        
        days = period_days.get(period)
        if not days:
            return df
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Efficient vectorized filtering
        if 'date' in df.columns and not df.empty:
            mask = df['date'] >= cutoff_date
            return df[mask].copy()
        
        return df
    
    def get_recent_activities(self, limit: int = 10) -> pd.DataFrame:
        """Get most recent activities with limit."""
        df = self.load_activities()
        return df.head(limit) if not df.empty else df
    
    def clear_all_activities(self) -> bool:
        """Clear all activities with cache invalidation."""
        try:
            with open(self.activities_file, 'w') as f:
                json.dump([], f, indent=2)
            
            # Clear cache
            self._activities_cache = self._create_empty_activities_df()
            self._activities_cache_timestamp = 0
            return True
            
        except OSError as e:
            print(f"Error clearing activities: {e}")
            return False
    
    # Weight management methods with similar optimizations
    def load_weight_data(self) -> pd.DataFrame:
        """Load weight data with caching and error handling."""
        try:
            # Check cache validity
            if (self._weight_cache is not None and 
                self._is_cache_valid(self.weight_file, self._weight_cache_timestamp)):
                return self._weight_cache.copy()
            
            if not os.path.exists(self.weight_file):
                return self._create_empty_weight_df()
            
            with open(self.weight_file, 'r') as f:
                weight_data = json.load(f)
            
            if not weight_data:
                df = self._create_empty_weight_df()
            else:
                df = pd.DataFrame(weight_data)
                df['date'] = pd.to_datetime(df['date'])
                
                # Ensure backward compatibility
                if 'id' not in df.columns:
                    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                    
                df = df.sort_values('date', ascending=True)
            
            # Update cache
            self._weight_cache = df.copy()
            self._weight_cache_timestamp = time.time()
            return df
            
        except (json.JSONDecodeError, OSError, KeyError) as e:
            print(f"Error loading weight data: {e}")
            return self._create_empty_weight_df()
    
    def save_weight_data(self, df: pd.DataFrame) -> bool:
        """Save weight data with atomic write."""
        try:
            weight_list = df.copy()
            if not weight_list.empty and 'date' in weight_list.columns:
                weight_list['date'] = weight_list['date'].astype(str)
            
            weight_data = weight_list.to_dict('records')
            
            # Atomic write
            temp_file = f"{self.weight_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(weight_data, f, indent=2)
            
            os.replace(temp_file, self.weight_file)
            
            # Update cache
            self._weight_cache = df.copy()
            self._weight_cache_timestamp = time.time()
            
            return True
            
        except (OSError, json.JSONEncodeError) as e:
            print(f"Error saving weight data: {e}")
            if os.path.exists(f"{self.weight_file}.tmp"):
                os.remove(f"{self.weight_file}.tmp")
            return False
    
    def add_weight_entry(self, weight_data: Dict) -> bool:
        """Add weight entry with validation."""
        try:
            # Validate weight value
            weight = weight_data.get('weight')
            if not isinstance(weight, (int, float)) or not (
                VALIDATION_RULES['min_weight'] <= weight <= VALIDATION_RULES['max_weight']
            ):
                return False
            
            df = self.load_weight_data()
            
            weight_data['id'] = str(uuid.uuid4())
            if isinstance(weight_data['date'], str):
                weight_data['date'] = datetime.fromisoformat(weight_data['date'])
            
            new_row = pd.DataFrame([weight_data])
            df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
            
            return self.save_weight_data(df)
            
        except (ValueError, TypeError) as e:
            print(f"Error adding weight entry: {e}")
            return False
    
    def delete_weight_entry(self, entry_id: str) -> bool:
        """Delete weight entry by ID."""
        try:
            df = self.load_weight_data()
            if df.empty or entry_id not in df['id'].values:
                return False
            
            df = df[df['id'] != entry_id]
            return self.save_weight_data(df)
            
        except Exception as e:
            print(f"Error deleting weight entry: {e}")
            return False
    
    # Settings management
    def load_settings(self) -> Dict:
        """Load settings with error handling."""
        try:
            if not os.path.exists(self.settings_file):
                return {"weight_goal": None}
            
            with open(self.settings_file, 'r') as f:
                return json.load(f)
                
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading settings: {e}")
            return {"weight_goal": None}
    
    def save_settings(self, settings: Dict) -> bool:
        """Save settings with atomic write."""
        try:
            temp_file = f"{self.settings_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            os.replace(temp_file, self.settings_file)
            return True
            
        except (OSError, json.JSONEncodeError) as e:
            print(f"Error saving settings: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for debugging."""
        return {
            'activities_cached': self._activities_cache is not None,
            'activities_cache_age': time.time() - self._activities_cache_timestamp,
            'weight_cached': self._weight_cache is not None,
            'weight_cache_age': time.time() - self._weight_cache_timestamp,
        }