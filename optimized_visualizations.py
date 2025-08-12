"""
Optimized visualization functions with improved performance and clean code.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import streamlit as st

from translations import get_text, get_activity_types, get_adaptations
from constants import (
    get_theme_colors, get_chart_colors, ACTIVITY_EMOJIS,
    TIME_PERIODS, INTENSITY_COLORS
)


class VisualizationEngine:
    """
    Optimized visualization engine with caching and performance improvements.
    """
    
    def __init__(self):
        self.color_cache = {}
        
    def _get_colors_for_theme(self, dark_mode: bool) -> Dict[str, str]:
        """Get cached colors for theme mode."""
        if dark_mode not in self.color_cache:
            self.color_cache[dark_mode] = get_theme_colors(dark_mode)
        return self.color_cache[dark_mode]
    
    def _create_base_layout(self, title: str, dark_mode: bool, lang: str) -> Dict:
        """Create base layout configuration for charts."""
        colors = self._get_colors_for_theme(dark_mode)
        
        return {
            'title': title,
            'font': dict(size=12, color=colors['text']),
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'title_font_color': colors['text'],
            'showlegend': False
        }


@st.cache_data
def create_optimized_activity_chart(activities_df: pd.DataFrame, dark_mode: bool = False, lang: str = 'en') -> go.Figure:
    """Create optimized activity distribution chart with performance improvements."""
    if activities_df.empty or 'type' not in activities_df.columns:
        return go.Figure()
    
    # Get theme colors
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Efficiently count and translate activities
    activity_counts = activities_df['type'].value_counts()
    
    # Create translation mapping (cached at module level)
    activity_translations = _get_activity_translations(lang)
    
    # Apply translations and sort
    translated_data = [
        (activity_translations.get(activity, activity), count)
        for activity, count in activity_counts.items()
    ]
    translated_data.sort(key=lambda x: x[1], reverse=True)
    
    activity_names, activity_values = zip(*translated_data) if translated_data else ([], [])
    
    # Create color mapping
    color_map = {name: chart_colors[i % len(chart_colors)] 
                for i, name in enumerate(activity_names)}
    
    # Create optimized chart
    fig = go.Figure(data=[
        go.Bar(
            y=list(activity_names),
            x=list(activity_values),
            orientation='h',
            marker_color=[color_map[name] for name in activity_names],
            hovertemplate='<b>%{y}</b><br>' + get_text('count', lang) + ': %{x}<extra></extra>',
            text=activity_values,
            textposition='auto'
        )
    ])
    
    # Apply optimized layout
    fig.update_layout(
        title=get_text('activity_distribution', lang),
        xaxis_title=get_text('number_of_activities', lang),
        yaxis_title=get_text('activity_type_chart', lang),
        height=max(400, len(activity_names) * 25),  # Dynamic height
        margin=dict(t=50, b=50, l=150, r=50),
        font=dict(size=12, color=colors['text']),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        xaxis=dict(
            gridcolor=colors['grid'],
            color=colors['text'],
            tickfont=dict(color=colors['text']),
            title_font=dict(color=colors['text'])
        ),
        yaxis=dict(
            gridcolor=colors['grid'],
            color=colors['text'],
            tickfont=dict(color=colors['text']),
            title_font=dict(color=colors['text'])
        ),
        title_font_color=colors['text'],
        showlegend=False
    )
    
    return fig


@st.cache_data
def create_optimized_weight_chart(weight_df: pd.DataFrame, goal_weight: Optional[float] = None, 
                                dark_mode: bool = False, lang: str = 'en') -> go.Figure:
    """Create optimized weight progression chart."""
    if weight_df.empty or 'weight' not in weight_df.columns:
        return go.Figure()
    
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    fig = go.Figure()
    
    # Add weight progression line
    fig.add_trace(go.Scatter(
        x=weight_df['date'],
        y=weight_df['weight'],
        mode='lines+markers',
        name=get_text('weight_progress', lang),
        line=dict(color=chart_colors[0], width=3),
        marker=dict(
            color=chart_colors[0],
            size=8,
            line=dict(width=2, color=colors['background'])
        ),
        hovertemplate='<b>' + get_text('date', lang) + '</b>: %{x}<br>' +
                     '<b>' + get_text('weight_kg', lang) + '</b>: %{y:.1f}<extra></extra>'
    ))
    
    # Add goal line if specified
    if goal_weight:
        fig.add_hline(
            y=goal_weight,
            line_dash="dash",
            line_color=chart_colors[1],
            annotation_text=f"{get_text('target_weight', lang)}: {goal_weight}kg",
            annotation_position="top right"
        )
    
    # Calculate trend if enough data points
    if len(weight_df) >= 3:
        trend_line = _calculate_trend_line(weight_df)
        if trend_line is not None:
            fig.add_trace(trend_line)
    
    # Apply layout
    fig.update_layout(
        title=get_text('weight_progress', lang),
        xaxis_title=get_text('date', lang),
        yaxis_title=get_text('weight_kg', lang),
        height=400,
        margin=dict(t=50, b=50, l=80, r=50),
        font=dict(size=12, color=colors['text']),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        xaxis=dict(
            gridcolor=colors['grid'],
            color=colors['text'],
            tickfont=dict(color=colors['text']),
            title_font=dict(color=colors['text'])
        ),
        yaxis=dict(
            gridcolor=colors['grid'],
            color=colors['text'],
            tickfont=dict(color=colors['text']),
            title_font=dict(color=colors['text'])
        ),
        title_font_color=colors['text'],
        showlegend=False
    )
    
    return fig


@st.cache_data
def create_optimized_weekly_summary(activities_df: pd.DataFrame, dark_mode: bool = False, 
                                  lang: str = 'en') -> go.Figure:
    """Create optimized weekly activity summary."""
    if activities_df.empty:
        return go.Figure()
    
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Prepare data efficiently
    weekly_data = _prepare_weekly_data(activities_df)
    
    if not weekly_data:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=[
            get_text('weekly_duration', lang),
            get_text('weekly_intensity', lang)
        ],
        vertical_spacing=0.15
    )
    
    weeks, durations, intensities = zip(*weekly_data)
    
    # Add duration chart
    fig.add_trace(
        go.Bar(
            x=list(weeks),
            y=list(durations),
            name=get_text('duration_minutes', lang),
            marker_color=chart_colors[0],
            hovertemplate='<b>%{x}</b><br>' + get_text('duration_minutes', lang) + ': %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add intensity chart
    fig.add_trace(
        go.Scatter(
            x=list(weeks),
            y=list(intensities),
            mode='lines+markers',
            name=get_text('avg_intensity', lang),
            line=dict(color=chart_colors[1], width=3),
            marker=dict(color=chart_colors[1], size=8),
            hovertemplate='<b>%{x}</b><br>' + get_text('avg_intensity', lang) + ': %{y:.1f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        margin=dict(t=80, b=50, l=80, r=50),
        font=dict(size=12, color=colors['text']),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        title_font_color=colors['text'],
        showlegend=False
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor=colors['grid'],
        color=colors['text'],
        tickfont=dict(color=colors['text'])
    )
    fig.update_yaxes(
        gridcolor=colors['grid'],
        color=colors['text'],
        tickfont=dict(color=colors['text'])
    )
    
    return fig


@st.cache_data
def create_optimized_adaptation_chart(activities_df: pd.DataFrame, dark_mode: bool = False, 
                                    lang: str = 'en') -> go.Figure:
    """Create optimized training adaptation focus chart."""
    if activities_df.empty or 'adaptation' not in activities_df.columns:
        return go.Figure()
    
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Filter out null adaptations and count
    adaptation_data = activities_df[activities_df['adaptation'].notna() & 
                                  (activities_df['adaptation'] != '')]
    
    if adaptation_data.empty:
        return go.Figure()
    
    adaptation_counts = adaptation_data['adaptation'].value_counts()
    
    # Get translation mapping
    adaptation_translations = _get_adaptation_translations(lang)
    
    # Apply translations
    translated_labels = [
        adaptation_translations.get(adaptation, adaptation) 
        for adaptation in adaptation_counts.index
    ]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=translated_labels,
            values=adaptation_counts.values,
            hole=0.4,
            marker=dict(
                colors=chart_colors[:len(adaptation_counts)],
                line=dict(color=colors['background'], width=2)
            ),
            hovertemplate='<b>%{label}</b><br>' + 
                         get_text('count', lang) + ': %{value}<br>' +
                         get_text('percentage', lang) + ': %{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=get_text('training_focus', lang),
        height=500,
        margin=dict(t=80, b=50, l=50, r=50),
        font=dict(size=12, color=colors['text']),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        title_font_color=colors['text'],
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(color=colors['text'])
        )
    )
    
    return fig


# Helper functions
@st.cache_data
def _get_activity_translations(lang: str) -> Dict[str, str]:
    """Get cached activity type translations."""
    try:
        from constants import ACTIVITY_EMOJIS
        return {
            activity: get_text(activity.lower().replace('-', '_').replace(' ', '_'), lang)
            for activity in ACTIVITY_EMOJIS.keys()
        }
    except Exception:
        # Fallback for translation errors
        return {}


@st.cache_data
def _get_adaptation_translations(lang: str) -> Dict[str, str]:
    """Get cached adaptation translations."""
    try:
        adaptations = get_adaptations(lang)
        if isinstance(adaptations, list):
            return {
                adaptation['value']: adaptation['label']
                for adaptation in adaptations
                if isinstance(adaptation, dict) and 'value' in adaptation and 'label' in adaptation
            }
        else:
            # Fallback if adaptations is not in expected format
            return {}
    except Exception:
        # Fallback for any translation errors
        return {}


def _prepare_weekly_data(activities_df: pd.DataFrame) -> List[Tuple[str, int, float]]:
    """Prepare weekly summary data efficiently."""
    if activities_df.empty or 'date' not in activities_df.columns:
        return []
    
    # Group by week and calculate metrics
    activities_df['week'] = activities_df['date'].dt.to_period('W')
    weekly_groups = activities_df.groupby('week')
    
    weekly_data = []
    for week, group in weekly_groups:
        total_duration = group['duration'].sum()
        
        # Calculate average intensity (convert to numeric)
        intensity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
        numeric_intensities = group['intensity'].map(intensity_mapping)
        avg_intensity = numeric_intensities.mean() if not numeric_intensities.isna().all() else 0
        
        weekly_data.append((str(week), total_duration, avg_intensity))
    
    return sorted(weekly_data, key=lambda x: x[0])


def _calculate_trend_line(weight_df: pd.DataFrame) -> Optional[go.Scatter]:
    """Calculate and return trend line for weight data."""
    try:
        # Simple trend calculation without numpy dependency
        if len(weight_df) < 2:
            return None
            
        # Simple linear trend using basic math
        dates_numeric = [(d - weight_df['date'].min()).days for d in weight_df['date']]
        weights = weight_df['weight'].values
        
        n = len(dates_numeric)
        sum_x = sum(dates_numeric)
        sum_y = sum(weights)
        sum_xy = sum(x * y for x, y in zip(dates_numeric, weights))
        sum_x2 = sum(x * x for x in dates_numeric)
        
        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Calculate trend values
        trend_y = [slope * x + intercept for x in dates_numeric]
        
        return go.Scatter(
            x=weight_df['date'],
            y=trend_y,
            mode='lines',
            name='Trend',
            line=dict(color='gray', width=2, dash='dot'),
            opacity=0.7,
            showlegend=False
        )
        
    except Exception:
        return None


# Backward compatibility functions
def create_activity_chart(activities_df: pd.DataFrame, dark_mode: bool = False, lang: str = 'en') -> go.Figure:
    """Backward compatibility wrapper."""
    return create_optimized_activity_chart(activities_df, dark_mode, lang)

def create_weight_chart(weight_df: pd.DataFrame, goal_weight: Optional[float] = None, 
                       dark_mode: bool = False, lang: str = 'en') -> go.Figure:
    """Backward compatibility wrapper."""
    return create_optimized_weight_chart(weight_df, goal_weight, dark_mode, lang)

def create_weekly_summary(activities_df: pd.DataFrame, dark_mode: bool = False, lang: str = 'en') -> go.Figure:
    """Backward compatibility wrapper."""
    return create_optimized_weekly_summary(activities_df, dark_mode, lang)

def create_adaptation_chart(activities_df: pd.DataFrame, dark_mode: bool = False, lang: str = 'en') -> go.Figure:
    """Backward compatibility wrapper."""
    return create_optimized_adaptation_chart(activities_df, dark_mode, lang)