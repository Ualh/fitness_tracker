"""
Optimized app components for better maintainability and performance.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from constants import (
    ACTIVITY_TYPES, INTENSITY_LEVELS, TIME_PERIODS, VALIDATION_RULES,
    get_activity_emoji, calculate_calories_estimate
)
from translations import get_text, get_activity_types, get_adaptations
from utils import format_duration


class ActivityFormComponent:
    """Optimized activity form component with validation."""
    
    def __init__(self, lang: str = 'en'):
        self.lang = lang
    
    def render(self, data_manager, user_id: Optional[int] = None) -> bool:
        """Render activity form and handle submission."""
        st.header(get_text('add_activity', self.lang))
        
        with st.form("activity_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                activity_types = get_activity_types(self.lang)
                activity_type = st.selectbox(
                    get_text('activity_type', self.lang),
                    options=[item['value'] for item in activity_types],
                    format_func=lambda x: next(item['label'] for item in activity_types if item['value'] == x)
                )
            
            with col2:
                duration = st.number_input(
                    get_text('duration_minutes', self.lang),
                    min_value=VALIDATION_RULES['min_duration'],
                    max_value=VALIDATION_RULES['max_duration'],
                    value=30,
                    step=5
                )
            
            with col3:
                intensity = st.selectbox(
                    get_text('intensity', self.lang),
                    options=INTENSITY_LEVELS,
                    format_func=lambda x: get_text(x.lower(), self.lang)
                )
            
            # Date and description
            date = st.date_input(get_text('date', self.lang), value=datetime.now().date())
            description = st.text_area(
                get_text('description_optional', self.lang),
                max_chars=VALIDATION_RULES['max_description_length'],
                help=f"Maximum {VALIDATION_RULES['max_description_length']} characters"
            )
            
            # Adaptation selection
            adaptations = get_adaptations(self.lang)
            adaptation = st.selectbox(
                get_text('primary_adaptation', self.lang),
                options=[''] + [item['value'] for item in adaptations],
                format_func=lambda x: get_text('select_adaptation', self.lang) if x == '' 
                                    else next(item['label'] for item in adaptations if item['value'] == x)
            )
            
            # Submit button
            submitted = st.form_submit_button(get_text('add_activity_btn', self.lang))
            
            if submitted:
                return self._handle_submission(
                    data_manager, user_id, activity_type, duration, 
                    intensity, date, description, adaptation
                )
        
        return False
    
    def _handle_submission(self, data_manager, user_id: Optional[int], 
                          activity_type: str, duration: int, intensity: str,
                          date, description: str, adaptation: str) -> bool:
        """Handle form submission with validation."""
        try:
            # Create activity data
            activity_data = {
                'type': activity_type,
                'duration': duration,
                'intensity': intensity,
                'date': datetime.combine(date, datetime.min.time()),
                'description': description,
                'adaptation': adaptation if adaptation else None
            }
            
            # Add activity based on manager type
            if user_id:  # Database mode
                success = data_manager.add_activity(user_id, activity_data)
            else:  # Local mode
                success = data_manager.add_activity(activity_data)
            
            if success:
                # Calculate and show calorie estimate
                calories = calculate_calories_estimate(activity_type, duration, intensity)
                
                st.success(
                    f"✅ {get_text('activity_added', self.lang)}! "
                    f"({get_text('estimated_calories', self.lang)}: {calories})"
                )
                return True
            else:
                st.error(get_text('error_adding_activity', self.lang))
                return False
                
        except Exception as e:
            st.error(f"{get_text('error_adding_activity', self.lang)}: {str(e)}")
            return False


class WeightFormComponent:
    """Optimized weight entry form component."""
    
    def __init__(self, lang: str = 'en'):
        self.lang = lang
    
    def render(self, data_manager, user_id: Optional[int] = None) -> bool:
        """Render weight form and handle submission."""
        st.header(get_text('add_weight', self.lang))
        
        with st.form("weight_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                weight = st.number_input(
                    get_text('weight_kg', self.lang),
                    min_value=VALIDATION_RULES['min_weight'],
                    max_value=VALIDATION_RULES['max_weight'],
                    value=70.0,
                    step=0.1,
                    format="%.1f"
                )
            
            with col2:
                date = st.date_input(get_text('date', self.lang), value=datetime.now().date())
            
            submitted = st.form_submit_button(get_text('add_weight', self.lang))
            
            if submitted:
                return self._handle_submission(data_manager, user_id, weight, date)
        
        return False
    
    def _handle_submission(self, data_manager, user_id: Optional[int], 
                          weight: float, date) -> bool:
        """Handle weight form submission."""
        try:
            weight_data = {
                'weight': weight,
                'date': datetime.combine(date, datetime.min.time())
            }
            
            # Add weight entry based on manager type
            if user_id:  # Database mode
                success = data_manager.add_weight_entry(user_id, weight, weight_data['date'])
            else:  # Local mode
                success = data_manager.add_weight_entry(weight_data)
            
            if success:
                st.success(f"✅ {get_text('weight_added', self.lang)}!")
                return True
            else:
                st.error(get_text('error_adding_weight', self.lang))
                return False
                
        except Exception as e:
            st.error(f"{get_text('error_adding_weight', self.lang)}: {str(e)}")
            return False


class MetricsComponent:
    """Optimized metrics display component."""
    
    def __init__(self, lang: str = 'en'):
        self.lang = lang
    
    def render_activity_metrics(self, activities_df: pd.DataFrame) -> None:
        """Render activity metrics in a compact format."""
        if activities_df.empty:
            st.info(get_text('no_activities_yet', self.lang))
            return
        
        # Calculate metrics efficiently
        metrics = self._calculate_activity_metrics(activities_df)
        
        # Display in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                get_text('total_activities', self.lang),
                metrics['total_count']
            )
        
        with col2:
            st.metric(
                get_text('total_time', self.lang),
                format_duration(metrics['total_duration'])
            )
        
        with col3:
            st.metric(
                get_text('avg_duration', self.lang),
                format_duration(metrics['avg_duration'])
            )
        
        with col4:
            st.metric(
                get_text('most_common_activity', self.lang),
                f"{get_activity_emoji(metrics['most_common'])} {metrics['most_common']}"
            )
    
    def render_weight_metrics(self, weight_df: pd.DataFrame, goal_weight: Optional[float] = None) -> None:
        """Render weight metrics efficiently."""
        if weight_df.empty:
            st.info(get_text('no_weight_data', self.lang))
            return
        
        metrics = self._calculate_weight_metrics(weight_df, goal_weight)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                get_text('current_weight', self.lang),
                f"{metrics['current_weight']:.1f} kg"
            )
        
        with col2:
            if metrics['weight_change'] is not None:
                st.metric(
                    get_text('weight_change_30d', self.lang),
                    f"{metrics['weight_change']:+.1f} kg"
                )
        
        with col3:
            if goal_weight:
                remaining = goal_weight - metrics['current_weight']
                st.metric(
                    get_text('goal_remaining', self.lang),
                    f"{remaining:+.1f} kg"
                )
    
    def _calculate_activity_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate activity metrics efficiently."""
        return {
            'total_count': len(df),
            'total_duration': df['duration'].sum(),
            'avg_duration': df['duration'].mean(),
            'most_common': df['type'].mode().iloc[0] if not df.empty else 'None'
        }
    
    def _calculate_weight_metrics(self, df: pd.DataFrame, goal_weight: Optional[float]) -> Dict[str, Any]:
        """Calculate weight metrics efficiently."""
        current_weight = df.iloc[-1]['weight'] if not df.empty else 0
        
        # Calculate 30-day change
        weight_change = None
        if len(df) > 1:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_entries = df[df['date'] >= thirty_days_ago]
            if len(recent_entries) > 1:
                weight_change = current_weight - recent_entries.iloc[0]['weight']
        
        return {
            'current_weight': current_weight,
            'weight_change': weight_change,
            'goal_weight': goal_weight
        }


class SettingsComponent:
    """Optimized settings component."""
    
    def __init__(self, lang: str = 'en'):
        self.lang = lang
    
    def render(self, data_manager, user_id: Optional[int] = None) -> bool:
        """Render settings interface."""
        st.header(get_text('settings', self.lang))
        
        settings_changed = False
        
        # Language settings
        st.subheader(get_text('language_settings', self.lang))
        self._render_language_selector()
        
        # Theme settings  
        st.subheader(get_text('theme_settings', self.lang))
        dark_mode_changed = self._render_theme_selector()
        if dark_mode_changed:
            settings_changed = True
        
        # Weight goal settings
        st.subheader(get_text('weight_goal_settings', self.lang))
        goal_changed = self._render_weight_goal(data_manager, user_id)
        if goal_changed:
            settings_changed = True
        
        return settings_changed
    
    def _render_language_selector(self) -> None:
        """Render language selection."""
        current_lang = st.session_state.get('language', 'en')
        language_options = {
            'English': 'en',
            'Français': 'fr'
        }
        
        selected_language = st.selectbox(
            get_text('language', self.lang),
            options=list(language_options.keys()),
            index=0 if current_lang == 'en' else 1,
            key="settings_language_selector"
        )
        
        selected_lang_code = language_options[selected_language]
        if selected_lang_code != current_lang:
            st.session_state.language = selected_lang_code
            st.rerun()
    
    def _render_theme_selector(self) -> bool:
        """Render theme selection."""
        current_dark_mode = st.session_state.get('dark_mode', False)
        
        dark_mode = st.checkbox(
            get_text('dark_mode', self.lang),
            value=current_dark_mode,
            key="dark_mode_checkbox"
        )
        
        if dark_mode != current_dark_mode:
            st.session_state.dark_mode = dark_mode
            st.session_state.theme_changed = True
            return True
        
        return False
    
    def _render_weight_goal(self, data_manager, user_id: Optional[int]) -> bool:
        """Render weight goal settings."""
        # Get current goal
        if user_id:  # Database mode
            user = data_manager.get_user_by_id(user_id)
            current_goal = user.weight_goal if user else None
        else:  # Local mode
            settings = data_manager.load_settings()
            current_goal = settings.get('weight_goal')
        
        new_goal = st.number_input(
            get_text('target_weight', self.lang),
            min_value=VALIDATION_RULES['min_weight'],
            max_value=VALIDATION_RULES['max_weight'],
            value=current_goal if current_goal else 70.0,
            step=0.1,
            format="%.1f",
            key="weight_goal_input"
        )
        
        if st.button(get_text('set_goal', self.lang)):
            try:
                if user_id:  # Database mode
                    success = data_manager.update_user_preferences(user_id, weight_goal=new_goal)
                else:  # Local mode
                    settings = data_manager.load_settings()
                    settings['weight_goal'] = new_goal
                    success = data_manager.save_settings(settings)
                
                if success:
                    st.success(get_text('goal_updated', self.lang))
                    return True
                else:
                    st.error(get_text('error_updating_goal', self.lang))
                    
            except Exception as e:
                st.error(f"{get_text('error_updating_goal', self.lang)}: {str(e)}")
        
        return False


class DataFilterComponent:
    """Optimized data filtering component."""
    
    def __init__(self, lang: str = 'en'):
        self.lang = lang
    
    def render_period_filter(self, key: str = "period_filter") -> str:
        """Render period selection filter."""
        return st.selectbox(
            get_text('view_period', self.lang),
            options=TIME_PERIODS,
            index=0,
            key=key,
            format_func=lambda x: get_text(x.lower().replace(' ', '_'), self.lang)
        )
    
    def render_activity_type_filter(self, activities_df: pd.DataFrame, 
                                  key: str = "activity_filter") -> Optional[str]:
        """Render activity type filter."""
        if activities_df.empty:
            return None
        
        available_types = ['All'] + sorted(activities_df['type'].unique().tolist())
        
        return st.selectbox(
            get_text('filter_by_activity', self.lang),
            options=available_types,
            index=0,
            key=key,
            format_func=lambda x: get_text('all_activities', self.lang) if x == 'All' 
                                 else f"{get_activity_emoji(x)} {x}"
        )


def render_error_boundary(func, *args, **kwargs):
    """Error boundary wrapper for components."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page or contact support if the issue persists.")
        return None


def create_summary_box(title: str, content: str, color: str = "#f0f2f6") -> None:
    """Create a styled summary box."""
    st.markdown(
        f"""
        <div class="summary-box" style="
            background-color: {color};
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #1f77b4;
            margin: 1rem 0;
        ">
            <h4 style="margin-top: 0; color: #1f77b4;">{title}</h4>
            <p style="margin-bottom: 0;">{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )