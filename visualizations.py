import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from translations import get_text, get_activity_types, get_adaptations
import streamlit as st

@st.cache_data
def create_activity_chart(activities_df, dark_mode=False, lang='en'):
    """Create activity type distribution chart as horizontal bar chart with caching"""
    if activities_df.empty or 'type' not in activities_df.columns:
        return go.Figure()
    
    # Count activities by type
    activity_counts = activities_df['type'].value_counts()
    
    # Translate activity types for display
    activity_type_translations = {
        'Running': get_text('running', lang),
        'Walking': get_text('walking', lang),
        'Cycling': get_text('cycling', lang),
        'Swimming': get_text('swimming', lang),
        'Hiking': get_text('hiking', lang),
        'Weightlifting': get_text('weightlifting', lang),
        'Skiing': get_text('skiing', lang),
        'Back-country Skiing': get_text('back_country_skiing', lang),
        'Yoga': get_text('yoga', lang),
        'Rock Climbing': get_text('rock_climbing', lang),
        'Boxing': get_text('boxing', lang),
        'Basketball': get_text('basketball', lang),
        'Soccer': get_text('soccer', lang),
        'Tennis': get_text('tennis', lang),
        'CrossFit': get_text('crossfit', lang),
        'Pilates': get_text('pilates', lang),
        'Dancing': get_text('dancing', lang),
        'Martial Arts': get_text('martial_arts', lang),
        'Rowing': get_text('rowing', lang),
        'Other': get_text('other', lang)
    }
    
    # Create translated activity counts
    translated_counts = {}
    for activity, count in activity_counts.items():
        translated_name = activity_type_translations.get(activity, activity)
        translated_counts[translated_name] = count
    
    # Sort by count for consistent display
    sorted_activities = sorted(translated_counts.items(), key=lambda x: x[1], reverse=True)
    activity_names = [item[0] for item in sorted_activities]
    activity_values = [item[1] for item in sorted_activities]
    
    # Choose color palette based on theme
    if dark_mode:
        colors = ['#FF8C42', '#E76E42', '#CF5742', '#B74042', '#9F2942', '#871242', '#6F0042', '#570042']
        bg_color = '#1e1e1e'
        text_color = '#ffffff'
        grid_color = '#3d3d3d'
    else:
        colors = ['#8B9DC3', '#A8B8C8', '#C5D0D8', '#B5C4D1', '#9BACC0', '#D4DCE4', '#E1E8ED', '#F0F4F7']
        bg_color = 'white'
        text_color = '#333333'
        grid_color = '#e0e0e0'
    
    color_map = {activity: colors[i % len(colors)] for i, activity in enumerate(activity_names)}
    
    fig = go.Figure(data=[
        go.Bar(
            y=activity_names,
            x=activity_values,
            orientation='h',
            marker_color=[color_map[activity] for activity in activity_names],
            hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=get_text('activity_distribution', lang),
        xaxis_title=get_text('number_of_activities', lang),
        yaxis_title=get_text('activity_type_chart', lang),
        height=400,
        margin=dict(t=50, b=50, l=100, r=50),
        showlegend=False,
        font=dict(size=12, color=text_color),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        xaxis=dict(
            gridcolor=grid_color, 
            color=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color, 
            color=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        title_font_color=text_color
    )
    
    return fig

@st.cache_data
def create_weight_chart(weight_df, goal_weight=None, dark_mode=False, lang='en'):
    """Create weight progression chart with caching"""
    if weight_df.empty or 'weight' not in weight_df.columns or 'date' not in weight_df.columns:
        return go.Figure()
    
    # Choose colors based on theme
    if dark_mode:
        line_color = '#FF8C42'
        goal_color = '#E76E42'
        bg_color = '#1e1e1e'
        text_color = '#ffffff'
        grid_color = '#3d3d3d'
    else:
        line_color = '#8B9DC3'
        goal_color = '#A8B8C8'
        bg_color = 'white'
        text_color = '#333333'
        grid_color = '#e0e0e0'
    
    fig = go.Figure()
    
    # Weight progression line
    fig.add_trace(go.Scatter(
        x=weight_df['date'],
        y=weight_df['weight'],
        mode='lines+markers',
        name='Weight',
        line=dict(color=line_color, width=3),
        marker=dict(size=6, color=line_color),
        hovertemplate='<b>%{y:.1f} kg</b><br>%{x}<extra></extra>'
    ))
    
    # Goal line if set
    if goal_weight:
        fig.add_hline(
            y=goal_weight,
            line_dash="dash",
            line_color=goal_color,
            annotation_text=f"Goal: {goal_weight:.1f} kg",
            annotation_position="top right",
            annotation_font_color=text_color
        )
    
    fig.update_layout(
        title=get_text('weight_progress_chart', lang),
        xaxis_title=get_text('date_chart', lang),
        yaxis_title=get_text('weight_kg_chart', lang),
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        showlegend=False,
        hovermode='x unified',
        font=dict(size=12, color=text_color),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        xaxis=dict(
            gridcolor=grid_color, 
            color=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color, 
            color=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        title_font_color=text_color
    )
    
    return fig

@st.cache_data
def create_weekly_summary(activities_df, dark_mode=False, lang='en'):
    """Create weekly activity summary chart with caching"""
    if activities_df.empty or 'date' not in activities_df.columns or 'type' not in activities_df.columns or 'duration' not in activities_df.columns:
        return go.Figure()
    
    try:
        # Group by week and activity type
        activities_df_copy = activities_df.copy()
        activities_df_copy['week'] = activities_df_copy['date'].dt.to_period('W').dt.start_time
        
        # Translate activity types for display
        activity_type_translations = {
            'Running': get_text('running', lang),
            'Walking': get_text('walking', lang),
            'Cycling': get_text('cycling', lang),
            'Swimming': get_text('swimming', lang),
            'Hiking': get_text('hiking', lang),
            'Weightlifting': get_text('weightlifting', lang),
            'Skiing': get_text('skiing', lang),
            'Back-country Skiing': get_text('back_country_skiing', lang),
            'Yoga': get_text('yoga', lang),
            'Rock Climbing': get_text('rock_climbing', lang),
            'Boxing': get_text('boxing', lang),
            'Basketball': get_text('basketball', lang),
            'Soccer': get_text('soccer', lang),
            'Tennis': get_text('tennis', lang),
            'CrossFit': get_text('crossfit', lang),
            'Pilates': get_text('pilates', lang),
            'Dancing': get_text('dancing', lang),
            'Martial Arts': get_text('martial_arts', lang),
            'Rowing': get_text('rowing', lang),
            'Other': get_text('other', lang)
        }
        
        # Translate activity types in dataframe
        activities_df_copy['type_translated'] = activities_df_copy['type'].map(activity_type_translations).fillna(activities_df_copy['type'])
        
        weekly_data = activities_df_copy.groupby(['week', 'type_translated'])['duration'].sum().reset_index()
        weekly_data.rename(columns={'type_translated': 'type'}, inplace=True)
    except Exception:
        return go.Figure()
    
    # Choose colors based on theme
    if dark_mode:
        colors = ['#FF8C42', '#E76E42', '#CF5742', '#B74042', '#9F2942', '#871242', '#6F0042', '#570042']
        bg_color = '#1e1e1e'
        text_color = '#ffffff'
        grid_color = '#3d3d3d'
    else:
        colors = ['#8B9DC3', '#A8B8C8', '#C5D0D8', '#B5C4D1', '#9BACC0', '#D4DCE4', '#E1E8ED', '#F0F4F7']
        bg_color = 'white'
        text_color = '#333333'
        grid_color = '#e0e0e0'
    
    fig = px.bar(
        weekly_data,
        x='week',
        y='duration',
        color='type',
        title=get_text('weekly_activity_summary', lang),
        labels={'duration': get_text('duration_minutes_chart', lang), 'week': get_text('week_chart', lang)},
        color_discrete_sequence=colors
    )
    
    fig.update_layout(
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis_title=get_text('week_chart', lang),
        yaxis_title=get_text('duration_minutes_chart', lang),
        legend_title=get_text('legend_activity_type', lang),
        hovermode='x unified',
        font=dict(size=12, color=text_color),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        xaxis=dict(
            gridcolor=grid_color, 
            color=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color, 
            color=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        title_font_color=text_color,
        legend=dict(font=dict(color=text_color))
    )
    
    return fig

def create_intensity_chart(activities_df, lang='en'):
    """Create intensity distribution chart"""
    if activities_df.empty:
        return go.Figure()
    
    intensity_counts = activities_df['intensity'].value_counts()
    
    # Translate intensity levels for display
    intensity_translations = {
        'Low': get_text('low', lang),
        'Medium': get_text('medium', lang),
        'High': get_text('high', lang)
    }
    
    # Create translated intensity counts and maintain color mapping
    colors = {'Low': '#34C759', 'Medium': '#FF9500', 'High': '#FF3B30'}
    translated_intensities = []
    intensity_values = []
    intensity_colors = []
    
    for intensity, count in intensity_counts.items():
        translated_name = intensity_translations.get(intensity, intensity)
        translated_intensities.append(translated_name)
        intensity_values.append(count)
        intensity_colors.append(colors.get(intensity, '#007AFF'))
    
    fig = go.Figure(data=[
        go.Bar(
            x=translated_intensities,
            y=intensity_values,
            marker_color=intensity_colors,
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=get_text('activity_intensity_distribution', lang),
        xaxis_title=get_text('intensity_level', lang),
        yaxis_title=get_text('number_of_activities', lang),
        height=300,
        margin=dict(t=50, b=50, l=50, r=50),
        showlegend=False
    )
    
    return fig

def create_monthly_trend(activities_df):
    """Create monthly activity trend"""
    if activities_df.empty:
        return go.Figure()
    
    # Group by month
    activities_df['month'] = activities_df['date'].dt.to_period('M').dt.start_time
    monthly_data = activities_df.groupby('month').agg({
        'duration': 'sum',
        'type': 'count'
    }).reset_index()
    monthly_data.rename(columns={'type': 'count'}, inplace=True)
    
    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add duration bars
    fig.add_trace(
        go.Bar(
            x=monthly_data['month'],
            y=monthly_data['duration'],
            name="Total Duration",
            marker_color='#007AFF',
            opacity=0.7
        ),
        secondary_y=False,
    )
    
    # Add activity count line
    fig.add_trace(
        go.Scatter(
            x=monthly_data['month'],
            y=monthly_data['count'],
            mode='lines+markers',
            name="Activity Count",
            line=dict(color='#FF3B30', width=3),
            marker=dict(size=8)
        ),
        secondary_y=True,
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Duration (minutes)", secondary_y=False)
    fig.update_yaxes(title_text="Number of Activities", secondary_y=True)
    
    fig.update_layout(
        title="Monthly Activity Trends",
        xaxis_title="Month",
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
        hovermode='x unified'
    )
    
    return fig

@st.cache_data
def create_adaptation_chart(activities_df, dark_mode=False, lang='en'):
    """Create adaptation distribution chart with caching"""
    if activities_df.empty or 'adaptation' not in activities_df.columns:
        return go.Figure()
    
    try:
        # Filter out null adaptations and count
        adaptation_data = activities_df[activities_df['adaptation'].notna()]
        if adaptation_data.empty:
            return go.Figure()
            
        adaptation_counts = adaptation_data['adaptation'].value_counts()
        if adaptation_counts.empty:
            return go.Figure()
    except Exception:
        return go.Figure()
    
    # Translate adaptation names for display
    adaptation_translations = {
        'Maximal aerobic capacity': get_text('maximal_aerobic_capacity', lang),
        'Long duration submaximal work': get_text('long_duration_submaximal_work', lang),
        'Speed': get_text('speed', lang),
        'Power': get_text('power', lang),
        'Anaerobic capacity': get_text('anaerobic_capacity', lang),
        'Strength': get_text('strength', lang),
        'Muscular endurance': get_text('muscular_endurance', lang),
        'Muscle hypertrophy': get_text('muscle_hypertrophy', lang)
    }
    
    # Create translated adaptation counts
    translated_adaptation_counts = {}
    for adaptation, count in adaptation_counts.items():
        translated_name = adaptation_translations.get(adaptation, adaptation)
        translated_adaptation_counts[translated_name] = count
    
    # Sort by count for consistent display
    sorted_adaptations = sorted(translated_adaptation_counts.items(), key=lambda x: x[1], reverse=True)
    adaptation_names = [item[0] for item in sorted_adaptations]
    adaptation_values = [item[1] for item in sorted_adaptations]
    
    # Choose color mapping based on theme
    if dark_mode:
        colors = {
            'Maximal aerobic capacity': '#FF8C42',
            'Long duration submaximal work': '#E76E42', 
            'Speed': '#CF5742',
            'Power': '#B74042',
            'Anaerobic capacity': '#9F2942',
            'Strength': '#871242',
            'Muscular endurance': '#6F0042',
            'Muscle hypertrophy': '#570042'
        }
        bg_color = '#1e1e1e'
        text_color = '#ffffff'
        grid_color = '#3d3d3d'
    else:
        colors = {
            'Maximal aerobic capacity': '#8B9DC3',
            'Long duration submaximal work': '#A8B8C8', 
            'Speed': '#C5D0D8',
            'Power': '#B5C4D1',
            'Anaerobic capacity': '#9BACC0',
            'Strength': '#D4DCE4',
            'Muscular endurance': '#E1E8ED',
            'Muscle hypertrophy': '#F0F4F7'
        }
        bg_color = 'white'
        text_color = '#333333'
        grid_color = '#e0e0e0'
    
    # Create color mapping for translated names based on original names
    reverse_translation = {v: k for k, v in adaptation_translations.items()}
    adaptation_colors = []
    for translated_name in adaptation_names:
        original_name = reverse_translation.get(translated_name, translated_name)
        adaptation_colors.append(colors.get(original_name, '#FF8C42' if dark_mode else '#007AFF'))
    
    fig = go.Figure(data=[
        go.Bar(
            x=adaptation_names,
            y=adaptation_values,
            marker_color=adaptation_colors,
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=get_text('training_adaptations_focus', lang),
        xaxis_title=get_text('adaptation_type_chart', lang),
        yaxis_title=get_text('number_of_activities', lang),
        height=400,
        margin=dict(t=50, b=100, l=50, r=50),
        showlegend=False,
        xaxis=dict(
            tickangle=45, 
            color=text_color, 
            gridcolor=grid_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis=dict(
            color=text_color, 
            gridcolor=grid_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        font=dict(size=12, color=text_color),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        title_font_color=text_color
    )
    
    return fig
