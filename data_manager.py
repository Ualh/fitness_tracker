import json
import pandas as pd
import os
from datetime import datetime, timedelta
import uuid

class DataManager:
    def __init__(self):
        self.activities_file = 'data/activities.json'
        self.weight_file = 'data/weight.json'
        self.settings_file = 'data/settings.json'
        self.ensure_data_directory()
        self.init_data_files()
        
        # Cache for loaded data to avoid repeated file I/O
        self._activities_cache = None
        self._weight_cache = None
        self._activities_cache_timestamp = 0
        self._weight_cache_timestamp = 0
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs('data', exist_ok=True)
    
    def init_data_files(self):
        """Initialize data files if they don't exist"""
        if not os.path.exists(self.activities_file):
            with open(self.activities_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.weight_file):
            with open(self.weight_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w') as f:
                json.dump({"weight_goal": None}, f)
    
    def load_activities(self):
        """Load activities from JSON file with caching"""
        import time
        
        try:
            # Check if file exists and get modification time
            if not os.path.exists(self.activities_file):
                return pd.DataFrame(columns=['id', 'type', 'duration', 'intensity', 'date', 'description', 'adaptation']).astype({
                    'id': 'string',
                    'type': 'string', 
                    'duration': 'int64',
                    'intensity': 'string',
                    'description': 'string',
                    'adaptation': 'string'
                })
            
            file_mtime = os.path.getmtime(self.activities_file)
            
            # Return cached data if file hasn't been modified
            if (self._activities_cache is not None and 
                file_mtime <= self._activities_cache_timestamp):
                return self._activities_cache.copy()
            
            # Load fresh data
            with open(self.activities_file, 'r') as f:
                activities = json.load(f)
            
            if activities:
                df = pd.DataFrame(activities)
                df['date'] = pd.to_datetime(df['date'])
                # Ensure adaptation column exists for backward compatibility
                if 'adaptation' not in df.columns:
                    df['adaptation'] = None
                df = df.sort_values('date', ascending=False)
                
                # Cache the loaded data
                self._activities_cache = df.copy()
                self._activities_cache_timestamp = time.time()
                return df
            else:
                empty_df = pd.DataFrame(columns=['id', 'type', 'duration', 'intensity', 'date', 'description', 'adaptation']).astype({
                    'id': 'string',
                    'type': 'string', 
                    'duration': 'int64',
                    'intensity': 'string',
                    'description': 'string',
                    'adaptation': 'string'
                })
                self._activities_cache = empty_df.copy()
                self._activities_cache_timestamp = time.time()
                return empty_df
        except Exception as e:
            print(f"Error loading activities: {e}")
            return pd.DataFrame(columns=['id', 'type', 'duration', 'intensity', 'date', 'description', 'adaptation']).astype({
                'id': 'string',
                'type': 'string', 
                'duration': 'int64',
                'intensity': 'string',
                'description': 'string',
                'adaptation': 'string'
            })
    
    def save_activities(self, df):
        """Save activities DataFrame to JSON file and update cache"""
        import time
        try:
            activities_list = df.copy()
            if not activities_list.empty and 'date' in activities_list.columns:
                activities_list['date'] = activities_list['date'].astype(str)
            activities_list = activities_list.to_dict('records')
            
            with open(self.activities_file, 'w') as f:
                json.dump(activities_list, f, indent=2)
            
            # Update cache after successful save
            self._activities_cache = df.copy()
            self._activities_cache_timestamp = time.time()
            
            return True
        except Exception as e:
            print(f"Error saving activities: {e}")
            return False
    
    def add_activity(self, activity_data):
        """Add new activity"""
        try:
            df = self.load_activities()
            
            # Add unique ID and ensure datetime
            activity_data['id'] = str(uuid.uuid4())
            if isinstance(activity_data['date'], str):
                activity_data['date'] = datetime.fromisoformat(activity_data['date'])
            
            # Add to DataFrame
            new_row = pd.DataFrame([activity_data])
            if df.empty:
                df = new_row
            else:
                df = pd.concat([df, new_row], ignore_index=True)
            
            return self.save_activities(df)
        except Exception as e:
            print(f"Error adding activity: {e}")
            return False
    
    def delete_activity(self, activity_id):
        """Delete activity by ID"""
        try:
            df = self.load_activities()
            df = df[df['id'] != activity_id]
            return self.save_activities(df)
        except Exception as e:
            print(f"Error deleting activity: {e}")
            return False
    
    def update_activity(self, activity_id, activity_data):
        """Update existing activity"""
        try:
            df = self.load_activities()
            
            # Find the activity by ID
            activity_index = df[df['id'] == activity_id].index
            if len(activity_index) == 0:
                return False
            
            idx = activity_index[0]
            
            # Update the activity data
            df.at[idx, 'type'] = activity_data['type']
            df.at[idx, 'duration'] = activity_data['duration']
            df.at[idx, 'intensity'] = activity_data['intensity']
            df.at[idx, 'date'] = activity_data['date']
            df.at[idx, 'description'] = activity_data.get('description', '')
            df.at[idx, 'adaptation'] = activity_data.get('adaptation', '')
            
            return self.save_activities(df)
        except Exception as e:
            print(f"Error updating activity: {e}")
            return False
    
    def get_activities_for_period(self, period):
        """Get activities for specified time period with efficient filtering"""
        df = self.load_activities()  # Now uses cached data
        if df.empty:
            return df
        
        if period == "All time":
            return df
        
        now = datetime.now()
        
        if period == "Week":
            start_date = now - timedelta(days=7)
        elif period == "Month":
            start_date = now - timedelta(days=30)
        elif period == "Season":
            start_date = now - timedelta(days=90)
        else:
            return df
        
        # Efficient date filtering using pandas functionality
        if 'date' in df.columns and not df.empty:
            # Date column should already be datetime from load_activities
            mask = df['date'] >= start_date
            return df[mask].copy()
        else:
            return df
    
    def get_recent_activities(self, limit=10):
        """Get most recent activities"""
        df = self.load_activities()
        return df.head(limit)
    
    def get_all_activities(self):
        """Get all activities"""
        return self.load_activities()
    
    def clear_all_activities(self):
        """Clear all activities and update cache"""
        try:
            with open(self.activities_file, 'w') as f:
                json.dump([], f)
            # Clear cache
            self._activities_cache = pd.DataFrame(columns=['id', 'type', 'duration', 'intensity', 'date', 'description', 'adaptation']).astype({
                'id': 'string',
                'type': 'string', 
                'duration': 'int64',
                'intensity': 'string',
                'description': 'string',
                'adaptation': 'string'
            })
            self._activities_cache_timestamp = 0
            return True
        except Exception as e:
            print(f"Error clearing activities: {e}")
            return False
    
    # Weight management methods
    def load_weight_data(self):
        """Load weight data from JSON file with caching"""
        import time
        
        try:
            # Check if file exists and get modification time
            if not os.path.exists(self.weight_file):
                return pd.DataFrame(columns=['id', 'weight', 'date']).astype({
                    'id': 'string',
                    'weight': 'float64'
                })
            
            file_mtime = os.path.getmtime(self.weight_file)
            
            # Return cached data if file hasn't been modified
            if (self._weight_cache is not None and 
                file_mtime <= self._weight_cache_timestamp):
                return self._weight_cache.copy()
            
            # Load fresh data
            with open(self.weight_file, 'r') as f:
                weight_data = json.load(f)
            
            if weight_data:
                df = pd.DataFrame(weight_data)
                df['date'] = pd.to_datetime(df['date'])
                # Ensure id column exists for backward compatibility
                if 'id' not in df.columns:
                    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                df = df.sort_values('date', ascending=True)
                
                # Cache the loaded data
                self._weight_cache = df.copy()
                self._weight_cache_timestamp = time.time()
                return df
            else:
                empty_df = pd.DataFrame(columns=['id', 'weight', 'date']).astype({
                    'id': 'string',
                    'weight': 'float64'
                })
                self._weight_cache = empty_df.copy()
                self._weight_cache_timestamp = time.time()
                return empty_df
        except Exception as e:
            print(f"Error loading weight data: {e}")
            return pd.DataFrame(columns=['id', 'weight', 'date']).astype({
                'id': 'string',
                'weight': 'float64'
            })
    
    def save_weight_data(self, df):
        """Save weight DataFrame to JSON file and update cache"""
        import time
        try:
            weight_list = df.copy()
            if not weight_list.empty and 'date' in weight_list.columns:
                weight_list['date'] = weight_list['date'].astype(str)
            weight_list = weight_list.to_dict('records')
            
            with open(self.weight_file, 'w') as f:
                json.dump(weight_list, f, indent=2)
            
            # Update cache after successful save
            self._weight_cache = df.copy()
            self._weight_cache_timestamp = time.time()
            
            return True
        except Exception as e:
            print(f"Error saving weight data: {e}")
            return False
    
    def add_weight_entry(self, weight_data):
        """Add new weight entry"""
        try:
            df = self.load_weight_data()
            
            # Add unique ID
            weight_data['id'] = str(uuid.uuid4())
            if isinstance(weight_data['date'], str):
                weight_data['date'] = datetime.fromisoformat(weight_data['date'])
            
            # Add to DataFrame
            new_row = pd.DataFrame([weight_data])
            if df.empty:
                df = new_row
            else:
                df = pd.concat([df, new_row], ignore_index=True)
            
            return self.save_weight_data(df)
        except Exception as e:
            print(f"Error adding weight entry: {e}")
            return False
    
    def delete_weight_entry(self, entry_id):
        """Delete weight entry by ID"""
        try:
            df = self.load_weight_data()
            df = df[df['id'] != entry_id]
            return self.save_weight_data(df)
        except Exception as e:
            print(f"Error deleting weight entry: {e}")
            return False
    
    def update_weight_entry(self, entry_id, weight, date):
        """Update weight entry by ID"""
        try:
            df = self.load_weight_data()
            
            # Find the entry to update
            entry_index = df[df['id'] == entry_id].index
            if len(entry_index) > 0:
                # Update the entry
                idx = entry_index[0]
                df.loc[idx, 'weight'] = weight
                df.loc[idx, 'date'] = date
                return self.save_weight_data(df)
            return False
        except Exception as e:
            print(f"Error updating weight entry: {e}")
            return False
    
    def get_weight_data(self):
        """Get all weight data with forward fill for missing dates"""
        df = self.load_weight_data()
        if df.empty:
            return df
        
        # Forward fill weights for missing dates
        df = df.sort_values('date')
        df['weight'] = df['weight'].ffill()
        return df
    
    def clear_all_weight_data(self):
        """Clear all weight data"""
        try:
            with open(self.weight_file, 'w') as f:
                json.dump([], f)
            return True
        except Exception as e:
            print(f"Error clearing weight data: {e}")
            return False
    
    # Settings management
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {"weight_goal": None}
    
    def save_settings(self, settings):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_weight_goal(self):
        """Get weight goal from settings"""
        settings = self.load_settings()
        return settings.get('weight_goal')
    
    def set_weight_goal(self, goal):
        """Set weight goal in settings"""
        settings = self.load_settings()
        settings['weight_goal'] = goal
        return self.save_settings(settings)
