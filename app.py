import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# Import optimized modules
from constants import STREAMLIT_CONFIG, get_activity_emoji, calculate_calories_estimate
from optimized_data_manager import OptimizedDataManager
from visualizations import create_activity_chart, create_weight_chart, create_weekly_summary, create_adaptation_chart
from utils import format_duration
from optimized_database import OptimizedDatabaseManager
from translations import get_text, get_activity_types, get_activity_type_mapping, get_adaptations, get_adaptation_mapping
from auth_utils_simple import save_remember_credentials, clear_remember_credentials, setup_auto_login

# Backward compatibility imports
from data_manager import DataManager
from database import DatabaseManager

# Initialize managers with caching for performance
@st.cache_resource
def get_data_manager():
    return DataManager()  # Use original for stability

@st.cache_resource
def get_database_manager():
    return DatabaseManager()  # Use original for compatibility

# Backward compatibility
@st.cache_resource
def get_legacy_data_manager():
    return DataManager()

@st.cache_resource
def get_legacy_database_manager():
    return DatabaseManager()

@st.cache_data
def apply_theme(dark_mode=False):
    """Apply theme based on dark mode setting with caching"""
    if dark_mode:
        st.markdown("""
        <style>
        /* Main app styling */
        .stApp {
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #2d2d2d !important;
        }
        
        /* Text and headers */
        .stMarkdown, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown p, .stMarkdown div {
            color: #ffffff !important;
        }
        
        /* All text elements */
        p, h1, h2, h3, h4, h5, h6, span, div, label {
            color: #ffffff !important;
        }
        
        /* Streamlit specific text elements */
        .stText, .stCaption, .stCode {
            color: #ffffff !important;
        }
        
        /* Metrics and cards */
        .stMetric {
            background: #2d2d2d !important;
            color: #ffffff !important;
            border: 1px solid #3d3d3d !important;
            border-radius: 12px !important;
        }
        
        .stMetric [data-testid="metric-container"] {
            background: #2d2d2d !important;
            border: 1px solid #3d3d3d !important;
            padding: 1rem !important;
            border-radius: 12px !important;
        }
        
        /* Summary boxes */
        .summary-box {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
            border: 1px solid #3d3d3d !important;
        }
        
        /* Form elements and inputs */
        .stSelectbox > div > div, .stSelectbox div[data-baseweb="select"] {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
            border: 1px solid #3d3d3d !important;
        }
        
        .stSelectbox label, .stSelectbox > label {
            color: #ffffff !important;
        }
        
        .stNumberInput > div > div > input, .stNumberInput input {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
            border: 1px solid #3d3d3d !important;
        }
        
        .stNumberInput label, .stNumberInput > label {
            color: #ffffff !important;
        }
        
        .stTextInput > div > div > input, .stTextInput input {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
            border: 1px solid #3d3d3d !important;
        }
        
        .stTextInput label, .stTextInput > label {
            color: #ffffff !important;
        }
        
        .stTextArea > div > div > textarea, .stTextArea textarea {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
            border: 1px solid #3d3d3d !important;
        }
        
        .stTextArea label, .stTextArea > label {
            color: #ffffff !important;
        }
        
        .stDateInput > div > div > input, .stDateInput input {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
            border: 1px solid #3d3d3d !important;
        }
        
        .stDateInput label, .stDateInput > label {
            color: #ffffff !important;
        }
        
        /* Form labels and descriptions */
        .stSelectbox > label, .stNumberInput > label, .stTextInput > label, 
        .stTextArea > label, .stDateInput > label, .stSlider > label {
            color: #ffffff !important;
        }
        
        /* Radio and checkbox labels */
        .stRadio label, .stCheckbox label {
            color: #ffffff !important;
        }
        
        /* Widget labels */
        [data-testid="stWidgetLabel"] {
            color: #ffffff !important;
        }
        
        /* Additional text elements */
        .element-container label, .element-container p, .element-container div {
            color: #ffffff !important;
        }
        
        /* Headers and descriptions */
        .stHeader, .stSubheader {
            color: #ffffff !important;
        }
        
        /* Tab content text */
        .stTabs [data-baseweb="tab-panel"] {
            color: #ffffff !important;
        }
        
        /* Column text */
        .stColumn p, .stColumn div, .stColumn span {
            color: #ffffff !important;
        }
        
        /* Form help text */
        .stHelp, .help {
            color: #cccccc !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #FF8C42, #8B1538) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
        }
        
        /* Form submit buttons */
        .stFormSubmitButton > button {
            background: linear-gradient(135deg, #FF8C42, #8B1538) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
        }
        
        /* Number input increment/decrement buttons */
        .stNumberInput button {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #4d4d4d !important;
        }
        
        /* Number input buttons specifically */
        .stNumberInput [data-testid="stNumberInputStepUp"], 
        .stNumberInput [data-testid="stNumberInputStepDown"] {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #4d4d4d !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #2d2d2d !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #3d3d3d !important;
            color: #ffffff !important;
            border: 1px solid #4d4d4d !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #FF8C42, #8B1538) !important;
            color: white !important;
        }
        
        /* Container backgrounds */
        .block-container {
            background-color: #1e1e1e !important;
        }
        
        /* Main content area */
        .main .block-container {
            background-color: #1e1e1e !important;
        }
        
        /* Top header area */
        header[data-testid="stHeader"] {
            background-color: #1e1e1e !important;
        }
        
        /* All containers and divs */
        .stContainer, .element-container {
            background-color: transparent !important;
        }
        
        /* Remove white backgrounds from any remaining elements */
        div[data-testid="stVerticalBlock"] {
            background-color: transparent !important;
        }
        
        /* Ensure no white backgrounds on main elements */
        .main, .appview-container {
            background-color: #1e1e1e !important;
        }
        
        /* Fix any remaining white backgrounds */
        .stMarkdown > div, .css-1kyxreq, .css-12oz5g7 {
            background-color: transparent !important;
        }
        
        /* Ensure toolbar and top elements are dark */
        .css-1dp5vir, .css-17eq0hr {
            background-color: #1e1e1e !important;
        }
        
        /* Fix dropdown and select backgrounds */
        .stSelectbox > div > div > div {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        /* Additional button styling */
        button[kind="primary"], button[kind="secondary"] {
            background: linear-gradient(135deg, #FF8C42, #8B1538) !important;
            color: white !important;
            border: none !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        .streamlit-expanderContent {
            background-color: #2d2d2d !important;
            border: 1px solid #3d3d3d !important;
        }
        
        /* Info boxes */
        .stInfo {
            background-color: #1a3d5c !important;
            color: #ffffff !important;
        }
        
        .stWarning {
            background-color: #5c3a1a !important;
            color: #ffffff !important;
        }
        
        .stSuccess {
            background-color: #1a5c1a !important;
            color: #ffffff !important;
        }
        
        .stError {
            background-color: #5c1a1a !important;
            color: #ffffff !important;
        }
        
        /* Custom text colors for better readability */
        .dark-text {
            color: #ffffff !important;
        }
        
        .dark-subtext {
            color: #cccccc !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #000000;
        }
        
        .summary-box {
            background-color: #f8f9fa !important;
        }
        
        .dark-text {
            color: #000000 !important;
        }
        
        .dark-subtext {
            color: #666666 !important;
        }
        </style>
        """, unsafe_allow_html=True)

def show_auth():
    """Show login/register interface"""
    db = get_database_manager()
    
    # Language selector at the top of the page - should respect current app language setting
    current_lang = st.session_state.get('language', 'en')
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        language_options = {"English": "en", "Français": "fr"}
        selected_language = st.selectbox(
            "🌐 Language / Langue", 
            options=list(language_options.keys()),
            index=0 if current_lang == 'en' else 1,
            key="auth_language_selector"
        )
        # Store the selected language immediately
        selected_lang_code = language_options[selected_language]
        if selected_lang_code != current_lang:
            st.session_state.language = selected_lang_code
            st.rerun()
    
    lang = st.session_state.get('language', 'en')
    
    # Add some spacing after language selector
    st.markdown("---")
    
    st.title(get_text('app_title', lang))
    
    tab1, tab2 = st.tabs([get_text('login', lang), get_text('register', lang)])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input(get_text('username', lang))
            password = st.text_input(get_text('password', lang), type="password")
            remember_me = st.checkbox(get_text('remember_me', lang), help="Keep me logged in on this device")
            submit = st.form_submit_button(get_text('login', lang))
            
            if submit:
                if username and password:  # Basic validation
                    user = db.authenticate_user(username, password)
                    if user:
                        # Extract values immediately while session is active to avoid DetachedInstanceError
                        user_id = user.id
                        user_username = user.username
                        user_dark_mode = user.dark_mode
                        user_preferred_language = user.preferred_language
                        
                        # Store extracted values in session state (don't store the user object itself)
                        st.session_state.user_id = user_id
                        st.session_state.username = user_username
                        st.session_state.dark_mode = user_dark_mode
                        # Use user's preferred language, but if user changed language on login page, update their preference
                        login_page_lang = st.session_state.get('language', 'en')
                        if user_preferred_language and user_preferred_language != login_page_lang:
                            # Update user's language preference to match login page selection
                            db.update_user_preferences(user_id, preferred_language=login_page_lang)
                            st.session_state.language = login_page_lang
                        else:
                            st.session_state.language = user_preferred_language
                        
                        # Handle remember me functionality
                        if remember_me:
                            # Save remember credentials using query parameters
                            save_remember_credentials(db, user_id, username)
                            st.success(f"Welcome back, {user_username}! You will be remembered on this device.")
                        else:
                            # Clear any existing remember credentials
                            db.set_remember_token(user_id, generate_token=False)
                            clear_remember_credentials()
                            st.success(f"Welcome back, {user_username}!")
                        
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input(get_text('username', lang), key="reg_username")
            new_email = st.text_input(get_text('email', lang))
            new_password = st.text_input(get_text('password', lang), type="password", key="reg_password")
            submit_reg = st.form_submit_button(get_text('register', lang))
            
            if submit_reg:
                user, message = db.create_user(new_username, new_email, new_password)
                if user:
                    st.success(message)
                    st.info("Please login with your new account")
                else:
                    st.error(message)

def show_friends(db, lang):
    """Show friends interface"""
    st.header(get_text('friends', lang))
    
    user_id = st.session_state.user_id
    
    # Add friend section
    with st.form("add_friend_form"):
        st.subheader(get_text('add_friend', lang))
        friend_username = st.text_input(get_text('friend_username', lang))
        submit = st.form_submit_button(get_text('add_friend', lang))
        
        if submit and friend_username.strip():
            success, message = db.add_friend(user_id, friend_username.strip())
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        elif submit:
            st.warning("Please enter a username")
    
    # Show current friends and their recent activities
    session = db.get_session()
    try:
        from database import User
        user = session.query(User).filter(User.id == user_id).first()
        if user and user.friends:
            st.subheader(get_text('your_friends', lang))
            
            for friend in user.friends:
                with st.expander(f"👤 {friend.username}"):
                    # Get friend's recent activities
                    friend_activities = db.get_user_activities(friend.id, "Week")
                    
                    if friend_activities:
                        st.write(get_text('friend_activities', lang))
                        for activity in friend_activities[:5]:  # Show last 5 activities
                            st.write(f"• {activity.type} - {format_duration(activity.duration)} ({activity.intensity})")
                            st.caption(activity.date.strftime('%b %d, %Y'))
                    else:
                        st.write("No recent activities")
        else:
            st.info("No friends added yet")
    finally:
        session.close()

def show_settings(db, lang):
    """Show settings interface"""
    st.header(get_text('settings', lang))
    
    user_id = st.session_state.user_id
    
    # Initialize change flags
    if 'settings_changed' not in st.session_state:
        st.session_state.settings_changed = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dark mode toggle
        current_dark_mode = st.session_state.get('dark_mode', False)
        dark_mode = st.checkbox(get_text('dark_mode', lang), value=current_dark_mode, key="settings_dark_mode")
        
        if dark_mode != current_dark_mode and not st.session_state.settings_changed:
            st.session_state.dark_mode = dark_mode
            st.session_state.theme_changed = True
            db.update_user_preferences(user_id, dark_mode=dark_mode)
            st.session_state.settings_changed = True
    
    with col2:
        # Language selector
        current_lang = st.session_state.get('language', 'en')
        language = st.selectbox(get_text('language', lang), ["en", "fr"], 
                               index=0 if current_lang == 'en' else 1,
                               key="settings_language")
        
        if language != current_lang and not st.session_state.settings_changed:
            st.session_state.language = language
            db.update_user_preferences(user_id, preferred_language=language)
            st.session_state.settings_changed = True
    
    # Only rerun once if changes were made
    if st.session_state.settings_changed:
        st.session_state.settings_changed = False
        st.rerun()
    
    # Logout button
    if st.button(get_text('logout', lang)):
        # Clear remember me credentials and tokens from database
        if st.session_state.get('user_id'):
            db.set_remember_token(st.session_state.user_id, generate_token=False)
        clear_remember_credentials()
        
        # Clear session state
        for key in ['user', 'user_id', 'dark_mode', 'language']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

def main():
    st.set_page_config(**STREAMLIT_CONFIG)
    
    # Clear cache on app restart to ensure fresh data after updates
    if 'cache_cleared_v2' not in st.session_state:
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.cache_cleared_v2 = True
    
    # Apply theme only when needed - cached for performance
    current_dark_mode = st.session_state.get('dark_mode', False)
    if ('theme_applied' not in st.session_state or 
        st.session_state.get('theme_changed', False) or
        st.session_state.get('last_dark_mode') != current_dark_mode):
        apply_theme(current_dark_mode)
        st.session_state.theme_applied = True
        st.session_state.theme_changed = False
        st.session_state.last_dark_mode = current_dark_mode
    
    # Try to initialize database, fallback to local storage
    db = None
    dm = None
    try:
        db = get_database_manager()
        database_available = True
    except Exception as e:
        st.warning("⚠️ Database not available - Using local storage mode")
        st.info("To enable user accounts and friends: Configure your DATABASE_URL in Secrets")
        with st.expander("Database Setup Instructions"):
            st.markdown("""
            **To set up the database:**
            1. Go to [Supabase](https://supabase.com/dashboard/projects)
            2. Create a new project
            3. Click "Connect" → Copy "Transaction pooler" URI
            4. Replace `[YOUR-PASSWORD]` with your actual password
            5. Add it to Replit Secrets as `DATABASE_URL`
            6. Refresh the app
            """)
        database_available = False
        dm = get_data_manager()
    
    # Check authentication mode
    if database_available and db:
        # Database mode - require login
        if 'user_id' not in st.session_state:
            # Try auto-login first using remember me credentials
            if setup_auto_login(db):
                # Successfully auto-logged in, refresh the page to show logged in interface
                st.rerun()
            else:
                # No auto-login possible, show auth interface
                show_auth()
                return
        lang = st.session_state.get('language', 'en')
        show_logged_in_interface(db, lang)
    else:
        # Local mode - use original interface
        if dm is None:
            dm = get_data_manager()
        lang = st.session_state.get('language', 'en')
        show_local_interface(dm, lang)
    
def show_logged_in_interface(db, lang):
    """Show interface for logged-in users with database"""
    # Navigation
    tabs = st.tabs([
        get_text('dashboard', lang), 
        get_text('add_activity', lang), 
        get_text('weight_tracking', lang),
        get_text('friends', lang),
        get_text('settings', lang)
    ])
    
    with tabs[0]:
        show_dashboard_db(db, lang)
    with tabs[1]:
        add_activity_db(db, lang)
    with tabs[2]:
        weight_tracking_db(db, lang)
    with tabs[3]:
        show_friends(db, lang)
    with tabs[4]:
        show_settings(db, lang)

def show_local_interface(dm, lang):
    """Show interface for local storage mode"""
    # Language selector in sidebar
    with st.sidebar:
        # Initialize local change flag
        if 'local_settings_changed' not in st.session_state:
            st.session_state.local_settings_changed = False
        
        current_lang = st.session_state.get('language', 'en')
        new_lang = st.selectbox("Language", ["en", "fr"], index=0 if current_lang == 'en' else 1, key="local_lang_selector")
        if new_lang != current_lang and not st.session_state.local_settings_changed:
            st.session_state.language = new_lang
            st.session_state.local_settings_changed = True
        
        # Dark mode toggle
        current_dark = st.session_state.get('dark_mode', False)
        dark_mode = st.checkbox("Dark Mode", value=current_dark, key="local_dark_mode")
        if dark_mode != current_dark and not st.session_state.local_settings_changed:
            st.session_state.dark_mode = dark_mode
            st.session_state.theme_changed = True
            st.session_state.local_settings_changed = True
        
        # Only rerun once if any changes were made
        if st.session_state.local_settings_changed:
            st.session_state.local_settings_changed = False
            st.rerun()
    
    st.title(get_text('app_title', lang))
    
    # Navigation (without friends tab in local mode)
    tabs = st.tabs([
        get_text('dashboard', lang), 
        get_text('add_activity', lang), 
        get_text('weight_tracking', lang)
    ])
    
    with tabs[0]:
        show_dashboard_local(dm, lang)
    with tabs[1]:
        add_activity_local(dm, lang)
    with tabs[2]:
        weight_tracking_local(dm, lang)

def show_dashboard_local(dm, lang):
    """Display dashboard using local data manager"""
    st.header(get_text('dashboard', lang))
    
    # Get dark mode setting
    dark_mode = st.session_state.get('dark_mode', False)
    
    # Time period selector
    period_options = [get_text('week', lang), get_text('month', lang), get_text('season', lang), get_text('all_time', lang)]
    period = st.selectbox(get_text('view_period', lang), period_options, index=0)
    
    # Convert to English for data manager
    period_map = {
        get_text('week', lang): "Week",
        get_text('month', lang): "Month", 
        get_text('season', lang): "Season",
        get_text('all_time', lang): "All time"
    }
    period_en = period_map.get(period, "Week")
    
    # Get data for selected period
    activities_df = dm.get_activities_for_period(period_en)
    weight_df = dm.get_weight_data()
    
    # Summary metrics in compact box - safe calculation
    if not activities_df.empty:
        total_activities = len(activities_df)
        total_minutes = activities_df['duration'].sum() if 'duration' in activities_df.columns else 0
        
        # Calculate intensity safely
        intensity_label = 'N/A'
        if 'intensity' in activities_df.columns:
            try:
                intensity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
                mapped_values = [intensity_mapping.get(val, 0) for val in activities_df['intensity'] if val in intensity_mapping]
                if mapped_values:
                    avg_intensity = sum(mapped_values) / len(mapped_values)
                    intensity_index = max(0, min(2, int(avg_intensity) - 1))
                    intensity_label = ['Low', 'Medium', 'High'][intensity_index]
            except Exception:
                intensity_label = 'N/A'
        
        current_weight = None
        if not weight_df.empty and 'weight' in weight_df.columns:
            current_weight = weight_df.iloc[-1]['weight']
        
        # Summary box with key metrics
        with st.container():
            dark_mode = st.session_state.get('dark_mode', False)
            summary_class = "summary-box" if dark_mode else ""
            bg_color = "#2d2d2d" if dark_mode else "#f8f9fa"
            text_color = "#ffffff" if dark_mode else "#8B9DC3"
            subtitle_color = "#cccccc" if dark_mode else "#666"
            
            st.markdown(f"""
            <div class="{summary_class}" style="background-color: {bg_color}; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid {'#3d3d3d' if dark_mode else '#f0f0f0'};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{total_activities}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('activities', lang)}</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{format_duration(total_minutes)}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('total_time', lang)}</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{get_text(intensity_label.lower(), lang)}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('avg_intensity', lang)}</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{f"{current_weight:.1f} kg" if current_weight else get_text('no_data', lang)}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('current_weight', lang)}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts
    chart_tabs = st.tabs([
        get_text('activity_summary', lang), 
        get_text('weight_progress', lang), 
        get_text('weekly_summary', lang), 
        get_text('training_focus', lang)
    ])
    
    with chart_tabs[0]:
        if not activities_df.empty:
            fig = create_activity_chart(activities_df, dark_mode, lang)
            fig.update_layout(title=f"{get_text('activity_summary', lang)} - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activities recorded yet. Add your first activity!")
    
    with chart_tabs[1]:
        if not weight_df.empty:
            fig = create_weight_chart(weight_df, dm.get_weight_goal(), dark_mode, lang)
            fig.update_layout(title=f"{get_text('weight_progress', lang)} - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_text('no_data', lang))
    
    with chart_tabs[2]:
        if not activities_df.empty:
            fig = create_weekly_summary(activities_df, dark_mode, lang)
            fig.update_layout(title=f"{get_text('weekly_summary', lang)} - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activities recorded yet.")
    
    with chart_tabs[3]:
        if not activities_df.empty:
            fig = create_adaptation_chart(activities_df, dark_mode, lang)
            fig.update_layout(title=f"{get_text('training_focus', lang)} - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activities recorded yet.")

def add_activity_local(dm, lang):
    """Add activity using local data manager"""
    st.header(get_text('add_activity', lang))
    
    with st.form("add_activity_local_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            activity_type = st.selectbox(
                get_text('activity_type', lang),
                get_activity_types(lang)
            )
            
            duration = st.number_input(get_text('duration_minutes', lang), min_value=1, value=30)
            
            # Primary adaptation selection
            adaptations = get_adaptations(lang)
            
            selected_adaptation = st.selectbox(
                get_text('primary_adaptation', lang),
                list(adaptations.keys()),
                key="adaptation_select_local"
            )
        
        with col2:
            intensity_options = [get_text('low', lang), get_text('medium', lang), get_text('high', lang)]
            intensity = st.selectbox(get_text('intensity', lang), intensity_options)
            
            date = st.date_input(get_text('date', lang), value=datetime.now().date())
        
        description = st.text_area(
            get_text('description_optional', lang),
            placeholder=get_text("description_example", lang)
        )
        
        submit = st.form_submit_button(get_text('add_activity_btn', lang), use_container_width=True)
        
        if submit:
            # Convert intensity back to English
            intensity_map = {
                get_text('low', lang): "Low",
                get_text('medium', lang): "Medium", 
                get_text('high', lang): "High"
            }
            intensity_en = intensity_map.get(intensity, "Low")
            
            activity_data = {
                'type': activity_type,
                'duration': duration,
                'intensity': intensity_en,
                'date': datetime.combine(date, datetime.now().time()),
                'description': description.strip(),
                'adaptation': selected_adaptation
            }
            
            success = dm.add_activity(activity_data)
            if success:
                st.success("Activity added successfully!")
                st.rerun()
            else:
                st.error("Failed to add activity. Please try again.")
    
    # Expandable section with all adaptation descriptions
    st.markdown("---")
    with st.expander(f"📖 {get_text('adaptation_reference_title', lang)}", expanded=False):
        st.markdown(f"**{get_text('adaptation_reference_subtitle', lang)}**")
        st.markdown("")
        
        for adaptation_name, description in adaptations.items():
            st.markdown(f"**{adaptation_name}**")
            st.markdown(f"*{description}*")
            st.markdown("")
    
    # Activity History Section
    show_activity_history_local(dm, lang)

def weight_tracking_local(dm, lang):
    """Weight tracking using local data manager"""
    st.header(get_text('weight_tracking', lang))
    
    # Weight goal setting
    st.subheader(get_text('weight_goal', lang))
    col1, col2 = st.columns(2)
    
    with col1:
        current_goal = dm.get_weight_goal()
        # Get last weight for default value
        weight_df = dm.get_weight_data()
        default_weight = 70.0
        if not weight_df.empty and 'weight' in weight_df.columns:
            default_weight = weight_df.iloc[-1]['weight']
        
        # Initialize session state for goal input to prevent auto-refresh
        if 'local_goal_input' not in st.session_state:
            st.session_state.local_goal_input = current_goal if current_goal else default_weight
        
        # Use form to prevent immediate refresh on number input changes
        with st.form("goal_setting_form"):
            new_goal = st.number_input(
                get_text('target_weight', lang),
                min_value=30.0,
                max_value=200.0,
                value=st.session_state.local_goal_input,
                step=0.1,
                key="local_weight_goal_input"
            )
            
            submitted = st.form_submit_button(get_text('set_goal', lang))
            
            if submitted:
                if new_goal != current_goal:
                    dm.set_weight_goal(new_goal)
                    st.session_state.local_goal_input = new_goal
                    st.success(f"Weight goal set to {new_goal:.1f} kg")
                    st.rerun()
                else:
                    st.info("Goal unchanged")
    
    with col2:
        weight_df = dm.get_weight_data()
        if not weight_df.empty and current_goal and 'weight' in weight_df.columns:
            current_weight = weight_df.iloc[-1]['weight']
            difference = current_weight - current_goal
            if difference > 0:
                st.metric(get_text("distance_to_goal", lang), f"+{difference:.1f} kg", get_text("above_target", lang))
            else:
                st.metric(get_text("distance_to_goal", lang), f"{difference:.1f} kg", get_text("below_target", lang))
    
    # Add weight entry
    st.subheader(get_text('add_weight', lang))
    
    with st.form("weight_form"):
        weight = st.number_input(
            get_text('weight_kg', lang),
            min_value=30.0,
            max_value=200.0,
            value=default_weight,
            step=0.1
        )
        
        weight_date = st.date_input(get_text('date', lang), value=datetime.now().date())
        
        submit = st.form_submit_button(get_text('add_weight', lang))
        
        if submit:
            weight_data = {
                'weight': weight,
                'date': datetime.combine(weight_date, datetime.now().time())
            }
            success = dm.add_weight_entry(weight_data)
            if success:
                st.success("Weight entry added successfully!")
                st.rerun()
            else:
                st.error("Failed to add weight entry.")
    
    # Weight History section with Apple-style design
    show_weight_history_local(dm, lang)

def show_dashboard_db(db, lang):
    """Display dashboard using database"""
    st.header(get_text('dashboard', lang))
    
    user_id = st.session_state.user_id
    
    # Time period selector
    period = st.selectbox(
        get_text('view_period', lang), 
        [get_text('week', lang), get_text('month', lang), get_text('season', lang), get_text('all_time', lang)], 
        index=0
    )
    
    # Convert to English for database query
    period_map = {
        get_text('week', lang): "Week",
        get_text('month', lang): "Month", 
        get_text('season', lang): "Season",
        get_text('all_time', lang): "All time"
    }
    period_en = period_map.get(period, "Week")
    
    # Get activities from database
    activities = db.get_user_activities(user_id, period_en)
    
    if activities:
        # Convert to DataFrame for processing
        activities_data = []
        for activity in activities:
            activities_data.append({
                'type': activity.type,
                'duration': activity.duration,
                'intensity': activity.intensity,
                'date': activity.date,
                'adaptation': activity.adaptation
            })
        
        activities_df = pd.DataFrame(activities_data)
        
        # Calculate metrics safely without external dependencies
        total_activities = len(activities_df)
        total_minutes = activities_df['duration'].sum() if 'duration' in activities_df.columns else 0
        
        # Calculate intensity safely
        intensity_label = 'N/A'
        if 'intensity' in activities_df.columns:
            try:
                intensity_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
                mapped_values = [intensity_mapping.get(val, 0) for val in activities_df['intensity'] if val in intensity_mapping]
                if mapped_values:
                    avg_intensity = sum(mapped_values) / len(mapped_values)
                    intensity_index = max(0, min(2, int(avg_intensity) - 1))
                    intensity_label = ['Low', 'Medium', 'High'][intensity_index]
            except Exception:
                intensity_label = 'N/A'
        
        # Get current weight
        weight_entries = db.get_user_weight_data(user_id)
        current_weight = weight_entries[-1].weight if weight_entries else None
        
        # Summary box with key metrics
        with st.container():
            dark_mode = st.session_state.get('dark_mode', False)
            summary_class = "summary-box" if dark_mode else ""
            bg_color = "#2d2d2d" if dark_mode else "#f8f9fa"
            text_color = "#ffffff" if dark_mode else "#8B9DC3"
            subtitle_color = "#cccccc" if dark_mode else "#666"
            
            st.markdown(f"""
            <div class="{summary_class}" style="background-color: {bg_color}; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid {'#3d3d3d' if dark_mode else '#f0f0f0'};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{total_activities}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('activities', lang)}</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{format_duration(total_minutes)}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('total_time', lang)}</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{get_text(intensity_label.lower(), lang)}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('avg_intensity', lang)}</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: {text_color};">{f"{current_weight:.1f} kg" if current_weight else get_text('no_data', lang)}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: {subtitle_color};">{get_text('current_weight', lang)}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        chart_tabs = st.tabs([
            get_text('activity_summary', lang), 
            get_text('weight_progress', lang), 
            get_text('weekly_summary', lang), 
            get_text('training_focus', lang)
        ])
        
        with chart_tabs[0]:
            fig = create_activity_chart(activities_df, dark_mode, lang)
            fig.update_layout(title=f"{get_text('activity_summary', lang)} - {period}")
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_tabs[1]:
            if weight_entries:
                weight_data = [{'date': entry.date, 'weight': entry.weight} for entry in weight_entries]
                weight_df = pd.DataFrame(weight_data)
                
                # Get weight goal
                session = db.get_session()
                from database import User
                user = session.query(User).filter(User.id == user_id).first()
                goal_weight = user.weight_goal if user else None
                session.close()
                
                fig = create_weight_chart(weight_df, goal_weight, dark_mode, lang)
                fig.update_layout(title=f"{get_text('weight_progress', lang)} - {period}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(get_text('no_data', lang))
        
        with chart_tabs[2]:
            fig = create_weekly_summary(activities_df, dark_mode, lang)
            fig.update_layout(title=f"{get_text('weekly_summary', lang)} - {period}")
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_tabs[3]:
            fig = create_adaptation_chart(activities_df, dark_mode, lang)
            fig.update_layout(title=f"{get_text('training_focus', lang)} - {period}")
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.info("No activities recorded yet. Add your first activity!")

def add_activity_db(db, lang):
    """Add activity using database"""
    st.header(get_text('add_activity', lang))
    
    with st.form("add_activity_db_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            activity_type = st.selectbox(
                get_text('activity_type', lang),
                get_activity_types(lang)
            )
            
            duration = st.number_input(get_text('duration_minutes', lang), min_value=1, value=30)
            
            # Primary adaptation selection
            adaptations = get_adaptations(lang)
            
            selected_adaptation = st.selectbox(
                get_text('primary_adaptation', lang),
                list(adaptations.keys()),
                key="adaptation_select_db"
            )
        
        with col2:
            intensity = st.selectbox(get_text('intensity', lang), [
                get_text('low', lang), 
                get_text('medium', lang), 
                get_text('high', lang)
            ])
            
            date = st.date_input(get_text('date', lang), value=datetime.now().date())
        
        description = st.text_area(
            get_text('description_optional', lang),
            placeholder=get_text("description_example", lang)
        )
        
        submit = st.form_submit_button(get_text('add_activity_btn', lang), use_container_width=True)
        
        if submit:
            # Convert intensity back to English
            intensity_map = {
                get_text('low', lang): "Low",
                get_text('medium', lang): "Medium", 
                get_text('high', lang): "High"
            }
            intensity_en = intensity_map.get(intensity, "Low")
            
            # Convert activity type and adaptation back to English for storage
            activity_type_map = get_activity_type_mapping(lang)
            adaptation_map = get_adaptation_mapping(lang)
            
            activity_data = {
                'type': activity_type_map.get(activity_type, activity_type),
                'duration': duration,
                'intensity': intensity_en,
                'date': datetime.combine(date, datetime.now().time()),
                'description': description.strip(),
                'adaptation': adaptation_map.get(selected_adaptation, selected_adaptation)
            }
            
            success = db.add_activity(st.session_state.user_id, activity_data)
            if success:
                st.success("Activity added successfully!")
                st.rerun()
            else:
                st.error("Failed to add activity. Please try again.")
    
    # Expandable section with all adaptation descriptions
    st.markdown("---")
    with st.expander(f"📖 {get_text('adaptation_reference_title', lang)}", expanded=False):
        st.markdown(f"**{get_text('adaptation_reference_subtitle', lang)}**")
        st.markdown("")
        
        for adaptation_name, description in adaptations.items():
            st.markdown(f"**{adaptation_name}**")
            st.markdown(f"*{description}*")
            st.markdown("")
    
    # Activity History Section
    show_activity_history_db(db, lang)

def weight_tracking_db(db, lang):
    """Weight tracking using database"""
    st.header(get_text('weight_tracking', lang))
    
    user_id = st.session_state.user_id
    
    # Weight goal setting
    st.subheader(get_text('weight_goal', lang))
    col1, col2 = st.columns(2)
    
    with col1:
        # Get current goal
        session = db.get_session()
        from database import User
        user = session.query(User).filter(User.id == user_id).first()
        current_goal = user.weight_goal if user else None
        session.close()
        
        # Get last weight for default value
        weight_entries = db.get_user_weight_data(user_id)
        default_weight = weight_entries[-1].weight if weight_entries else 70.0
        
        # Initialize session state for goal input to prevent auto-refresh
        if 'db_goal_input' not in st.session_state:
            st.session_state.db_goal_input = current_goal if current_goal else default_weight
        
        # Use form to prevent immediate refresh on number input changes
        with st.form("db_goal_setting_form"):
            new_goal = st.number_input(
                get_text('target_weight', lang),
                min_value=30.0,
                max_value=200.0,
                value=st.session_state.db_goal_input,
                step=0.1,
                key="db_weight_goal_input"
            )
            
            submitted = st.form_submit_button(get_text('set_goal', lang))
            
            if submitted:
                if new_goal != current_goal:
                    db.update_user_preferences(user_id, weight_goal=new_goal)
                    st.session_state.db_goal_input = new_goal
                    st.success(f"Weight goal set to {new_goal:.1f} kg")
                    st.rerun()
                else:
                    st.info("Goal unchanged")
    
    with col2:
        if weight_entries and current_goal:
            current_weight = weight_entries[-1].weight
            difference = current_weight - current_goal
            if difference > 0:
                st.metric(get_text("distance_to_goal", lang), f"+{difference:.1f} kg", get_text("above_target", lang))
            else:
                st.metric(get_text("distance_to_goal", lang), f"{difference:.1f} kg", get_text("below_target", lang))
    
    # Add weight entry
    st.subheader(get_text('add_weight', lang))
    
    with st.form("weight_form"):
        weight = st.number_input(
            get_text('weight_kg', lang),
            min_value=30.0,
            max_value=200.0,
            value=default_weight,
            step=0.1,
            key="db_weight_entry_input"
        )
        
        weight_date = st.date_input(get_text('date', lang), value=datetime.now().date())
        
        submit = st.form_submit_button(get_text('add_weight', lang))
        
        if submit:
            success = db.add_weight_entry(user_id, weight, datetime.combine(weight_date, datetime.now().time()))
            if success:
                st.success("Weight entry added successfully!")
                st.rerun()
            else:
                st.error("Failed to add weight entry.")
    
    # Weight History section with Apple-style design
    show_weight_history_db(db, lang)
    
    # Custom CSS for Apple-like minimal design with better colors
    st.markdown("""
    <style>
    .main > div {
        padding-top: 1rem;
    }
    .stMetric {
        background: white;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
    }
    .stMetric:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1px solid #e5e5e7;
    }
    .stNumberInput > div > div {
        border-radius: 8px;
        border: 1px solid #e5e5e7;
    }
    .stTextArea > div > div {
        border-radius: 8px;
        border: 1px solid #e5e5e7;
    }
    .stButton > button {
        border-radius: 8px;
        border: none;
        font-weight: 500;
        transition: all 0.2s ease;
        background: linear-gradient(135deg, #FF8C42, #8B1538);
        color: white;
    }
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(255, 140, 66, 0.3);
        transform: translateY(-1px);
    }
    /* Force horizontal layout for button containers */
    div[data-testid="column"] > div > div[style*="display: flex"] {
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
    }
    /* Ensure columns are side by side */
    div[data-testid="column"] {
        display: inline-block !important;
        vertical-align: top !important;
    }
    /* Make buttons more compact */
    .stButton > button {
        padding: 0.25rem 0.5rem !important;
        margin: 0 !important;
        font-size: 14px !important;
        height: 32px !important;
        min-height: 32px !important;
    }
    /* Reduce column spacing for button areas */
    div[data-testid="column"]:nth-child(n+2) {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }
    .stExpander {
        border: 1px solid #f0f0f0;
        border-radius: 8px;
        background: white;
        margin-top: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background: #f8f9fa;
        border: 1px solid #e5e5e7;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF8C42, #8B1538);
        color: white;
        border-color: #FF8C42;
    }
    </style>
    """, unsafe_allow_html=True)

def show_dashboard(dm):
    """Display the main dashboard with activities and weight progress"""
    st.header("Dashboard")
    
    # Time period selector with callback
    period = st.selectbox(
        "View period", 
        ["Week", "Month", "Season", "All time"], 
        index=0,
        key="dashboard_period_selector"
    )
    
    # Get data for selected period - force refresh by creating unique key
    activities_df = dm.get_activities_for_period(period)
    weight_df = dm.get_weight_data()
    
    # Force page refresh if period changes by using unique container key
    container_key = f"dashboard_container_{period}_{len(activities_df) if not activities_df.empty else 0}"
    
    # Summary metrics as carousel tabs
    if not activities_df.empty and 'duration' in activities_df.columns and 'intensity' in activities_df.columns:
        total_activities = len(activities_df)
        total_minutes = activities_df['duration'].sum() if 'duration' in activities_df.columns else 0
        
        if 'intensity' in activities_df.columns:
            avg_intensity = activities_df['intensity'].map({'Low': 1, 'Medium': 2, 'High': 3}).mean()
            intensity_label = ['Low', 'Medium', 'High'][int(avg_intensity) - 1] if not pd.isna(avg_intensity) else 'N/A'
        else:
            intensity_label = 'N/A'
        
        current_weight = None
        if not weight_df.empty and 'weight' in weight_df.columns:
            current_weight = weight_df.iloc[-1]['weight']
        
        # Summary box with key metrics
        with st.container():
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: #8B9DC3;">{}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">Activities</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: #8B9DC3;">{}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">Total Time</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: #8B9DC3;">{}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">Avg Intensity</p>
                    </div>
                    <div style="text-align: center; flex: 1; min-width: 100px;">
                        <h3 style="margin: 0; color: #8B9DC3;">{}</h3>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">Current Weight</p>
                    </div>
                </div>
            </div>
            """.format(
                total_activities,
                format_duration(total_minutes),
                intensity_label,
                f"{current_weight:.1f} kg" if current_weight else "No data"
            ), unsafe_allow_html=True)
    
    # Dashboard sections as tabs for easy navigation
    chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(["📊 Activity Summary", "⚖️ Weight Progress", "📅 Weekly Summary", "🎯 Training Focus"])
    
    with chart_tab1:
        if not activities_df.empty:
            # Force chart recreation by including period in title
            fig = create_activity_chart(activities_df)
            fig.update_layout(title=f"Activity Distribution - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activities recorded yet. Add your first activity!")
    
    with chart_tab2:
        if not weight_df.empty:
            fig = create_weight_chart(weight_df, dm.get_weight_goal())
            fig.update_layout(title=f"Weight Progress - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No weight data recorded yet.")
    
    with chart_tab3:
        if not activities_df.empty:
            fig = create_weekly_summary(activities_df)
            fig.update_layout(title=f"Weekly Summary - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activities recorded yet.")
    
    with chart_tab4:
        if not activities_df.empty:
            fig = create_adaptation_chart(activities_df)
            fig.update_layout(title=f"Training Focus - {period}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activities recorded yet.")
    
    # Recent activities
    st.subheader("Recent Activities")
    recent_activities = dm.get_recent_activities(limit=10)
    
    if not recent_activities.empty:
        for _, activity in recent_activities.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                
                with col1:
                    st.write(get_activity_emoji(activity['type']))
                
                with col2:
                    st.write(f"**{activity['type']}**")
                    if 'adaptation' in activity and pd.notna(activity['adaptation']):
                        st.caption(f"🎯 {activity['adaptation']}")
                    if activity['description']:
                        st.caption(activity['description'])
                
                with col3:
                    st.write(f"{format_duration(activity['duration'])} • {activity['intensity']}")
                    st.caption(activity['date'].strftime('%b %d, %Y'))
                
                with col4:
                    if st.button("🗑️", key=f"del_{activity['id']}", help="Delete activity"):
                        dm.delete_activity(activity['id'])
                        st.rerun()
                
                st.divider()
    else:
        st.info("No activities recorded yet.")

def add_activity(dm):
    """Form to add new activities"""
    st.header("Add New Activity")
    
    with st.form("add_activity_legacy_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            activity_type = st.selectbox(
                "Activity Type",
                ["Running", "Walking", "Cycling", "Swimming", "Hiking", "Weightlifting", 
                 "Skiing", "Back-country Skiing", "Yoga", "Rock Climbing", "Boxing", 
                 "Basketball", "Soccer", "Tennis", "CrossFit", "Pilates", "Dancing", 
                 "Martial Arts", "Rowing", "Other"]
            )
            
            duration = st.number_input("Duration (minutes)", min_value=1, value=30)
            
            # Primary adaptation selection
            adaptations = {
                "Maximal aerobic capacity": "VO2 max - maximum oxygen uptake during intense exercise",
                "Long duration submaximal work": "Aerobic endurance - sustained effort at moderate intensity",
                "Speed": "Rate of movement - how fast you can move",
                "Power": "Force × velocity - explosive strength and speed combined",
                "Anaerobic capacity": "High-intensity work without oxygen - lactate system",
                "Strength": "Maximum force production - how much weight you can move",
                "Muscular endurance": "Ability to repeat contractions over time",
                "Muscle hypertrophy": "Increase in muscle size and mass"
            }
            
            selected_adaptation = st.selectbox(
                "Primary Targeted Adaptation",
                list(adaptations.keys()),
                help=f"{adaptations[list(adaptations.keys())[0]]}",
                key="adaptation_selector"
            )
            
            # Update help text dynamically based on selection  
            st.markdown(f"<small>💡 {adaptations[selected_adaptation]}</small>", unsafe_allow_html=True)
        
        with col2:
            intensity = st.selectbox("Intensity", ["Low", "Medium", "High"])
            
            date = st.date_input("Date", value=datetime.now().date())
        
        description = st.text_area(
            "Description (optional)",
            placeholder="e.g., 5km run, 1000m elevation gain, bench press workout..."
        )
        
        submit = st.form_submit_button("Add Activity", use_container_width=True)
        
        if submit:
            activity_data = {
                'type': activity_type,
                'duration': duration,
                'intensity': intensity,
                'date': datetime.combine(date, datetime.now().time()),
                'description': description.strip(),
                'adaptation': selected_adaptation
            }
            
            success = dm.add_activity(activity_data)
            if success:
                st.success("Activity added successfully!")
                st.rerun()
            else:
                st.error("Failed to add activity. Please try again.")

def weight_tracking(dm):
    """Weight tracking and goal setting"""
    st.header("Weight Tracking")
    
    # Weight goal setting
    st.subheader("Weight Goal")
    col1, col2 = st.columns(2)
    
    with col1:
        current_goal = dm.get_weight_goal()
        # Get last weight for default value
        weight_df = dm.get_weight_data()
        default_weight = 70.0
        if not weight_df.empty and 'weight' in weight_df.columns:
            default_weight = weight_df.iloc[-1]['weight']
        
        new_goal = st.number_input(
            "Target Weight (kg)",
            min_value=30.0,
            max_value=200.0,
            value=current_goal if current_goal else default_weight,
            step=0.1,
            key="local_weight_goal_input"
        )
        
        if st.button("Set Goal", key="local_set_goal_btn"):
            dm.set_weight_goal(new_goal)
            st.success(f"Weight goal set to {new_goal:.1f} kg")
            st.rerun()
    
    with col2:
        weight_df = dm.get_weight_data()
        if not weight_df.empty and current_goal and 'weight' in weight_df.columns:
            current_weight = weight_df.iloc[-1]['weight']
            difference = current_weight - current_goal
            if difference > 0:
                st.metric("Goal Progress", f"+{difference:.1f} kg", delta=f"{difference:.1f} kg above goal")
            else:
                st.metric("Goal Progress", f"{difference:.1f} kg", delta=f"{abs(difference):.1f} kg to goal")
    
    # Add weight entry
    st.subheader("Log Weight")
    with st.form("add_weight_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get last weight for default value
            weight_df = dm.get_weight_data()
            default_weight = 70.0
            if not weight_df.empty and 'weight' in weight_df.columns:
                default_weight = weight_df.iloc[-1]['weight']
            
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, step=0.1, value=default_weight, key="local_weight_entry_input")
        
        with col2:
            weight_date = st.date_input("Date", value=datetime.now().date())
        
        submit_weight = st.form_submit_button("Log Weight", use_container_width=True)
        
        if submit_weight:
            weight_data = {
                'weight': weight,
                'date': datetime.combine(weight_date, datetime.now().time())
            }
            
            success = dm.add_weight_entry(weight_data)
            if success:
                st.success("Weight logged successfully!")
                st.rerun()
            else:
                st.error("Failed to log weight. Please try again.")
    
    # Recent weight entries
    st.subheader("Recent Weight Entries")
    weight_df = dm.get_weight_data()
    
    if not weight_df.empty:
        recent_weights = weight_df.tail(10).sort_values('date', ascending=False)
        
        for _, entry in recent_weights.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{entry['weight']:.1f} kg**")
            
            with col2:
                st.write(entry['date'].strftime('%b %d, %Y'))
            
            with col3:
                if 'id' in entry:
                    if st.button("🗑️", key=f"del_weight_{entry['id']}", help="Delete entry"):
                        dm.delete_weight_entry(entry['id'])
                        st.rerun()
                else:
                    st.write("")  # Placeholder for entries without ID
    else:
        st.info("No weight entries recorded yet.")

def settings_page(dm):
    """Settings and data management"""
    st.header("Settings")
    
    # Data export
    st.subheader("Data Export")
    col1, col2 = st.columns(2)
    
    with col1:
        activities_df = dm.get_all_activities()
        if not activities_df.empty:
            csv = activities_df.to_csv(index=False)
            st.download_button(
                label="📁 Export Activities as CSV",
                data=csv,
                file_name=f"fitness_activities_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No activities to export yet.")
    
    with col2:
        weight_df = dm.get_weight_data()
        if not weight_df.empty:
            csv = weight_df.to_csv(index=False)
            st.download_button(
                label="📊 Export Weight Data as CSV",
                data=csv,
                file_name=f"weight_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No weight data to export yet.")
    
    # Data statistics
    st.subheader("Data Statistics")
    activities_df = dm.get_all_activities()
    weight_df = dm.get_weight_data()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Activities", len(activities_df))
    
    with col2:
        st.metric("Weight Entries", len(weight_df))
    
    with col3:
        if not activities_df.empty:
            total_hours = activities_df['duration'].sum() / 60
            st.metric("Total Hours", f"{total_hours:.1f}")
    
    # Data reset warning
    st.subheader("⚠️ Danger Zone")
    st.warning("The following actions cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear All Activities", type="secondary"):
            if st.session_state.get('confirm_clear_activities'):
                dm.clear_all_activities()
                st.success("All activities cleared.")
                st.session_state.confirm_clear_activities = False
                st.rerun()
            else:
                st.session_state.confirm_clear_activities = True
                st.error("Click again to confirm clearing all activities.")
    
    with col2:
        if st.button("Clear All Weight Data", type="secondary"):
            if st.session_state.get('confirm_clear_weight'):
                dm.clear_all_weight_data()
                st.success("All weight data cleared.")
                st.session_state.confirm_clear_weight = False
                st.rerun()
            else:
                st.session_state.confirm_clear_weight = True
                st.error("Click again to confirm clearing all weight data.")

def show_weight_history_db(db, lang):
    """Show weight history section for database version with Apple-style minimalistic design"""
    
    with st.expander(f"⚖️ {get_text('weight_history', lang)}", expanded=False):
        st.markdown(f"*{get_text('weight_history_subtitle', lang)}*")
        
        # Get recent weight entries and reverse for display (newest first)
        all_weight_entries = db.get_user_weight_data(st.session_state.user_id)
        weight_entries = list(reversed(all_weight_entries[-10:]))
        
        if not weight_entries:
            st.info(get_text('no_weight_entries', lang))
            return
        
        # Apple-style minimalistic weight list
        for i, entry in enumerate(weight_entries):
            # Check if this entry is being edited
            is_editing = st.session_state.get(f'editing_weight_db_{entry.id}', False)
            
            if is_editing:
                # Show edit form inline
                show_edit_weight_form_db(db, entry, lang)
            else:
                # Complete weight card with integrated buttons - no columns
                weight_value = getattr(entry, 'weight', 0.0)
                date_str = entry.date.strftime('%b %d, %Y')
                
                # Single integrated card with buttons - using columns for buttons
                if st.session_state.get(f'confirm_delete_weight_db_{entry.id}', False):
                    # Confirmation mode
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{weight_value:.1f} kg</strong></div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{date_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for confirmation buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✓", key=f'confirm_yes_weight_db_{entry.id}', help="Confirm", use_container_width=True):
                            if db.delete_weight_entry(entry.id):
                                st.success(get_text('weight_deleted', lang))
                                st.session_state[f'confirm_delete_weight_db_{entry.id}'] = False
                                st.rerun()
                            else:
                                st.error("Failed to delete weight entry")
                    with col3:
                        if st.button("✗", key=f'confirm_no_weight_db_{entry.id}', help="Cancel", use_container_width=True):
                            st.session_state[f'confirm_delete_weight_db_{entry.id}'] = False
                            st.rerun()
                else:
                    # Normal mode - integrated card with buttons
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{weight_value:.1f} kg</strong></div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{date_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✏️", key=f'edit_weight_db_{entry.id}', help="Edit", use_container_width=True):
                            st.session_state[f'editing_weight_db_{entry.id}'] = True
                            st.session_state['preserve_tab_state'] = True
                            st.rerun()
                    with col3:
                        if st.button("🗑️", key=f'delete_weight_db_{entry.id}', help="Delete", use_container_width=True):
                            st.session_state[f'confirm_delete_weight_db_{entry.id}'] = True
                            st.rerun()

def show_weight_history_local(dm, lang):
    """Show weight history section for local version with Apple-style minimalistic design"""
    
    with st.expander(f"⚖️ {get_text('weight_history', lang)}", expanded=False):
        st.markdown(f"*{get_text('weight_history_subtitle', lang)}*")
        
        # Get recent weight entries (limit to 10 for display)
        weight_df = dm.get_weight_data()
        
        if weight_df.empty:
            st.info(get_text('no_weight_entries', lang))
            return
        
        recent_weights = weight_df.tail(10).sort_values('date', ascending=False)
        
        # Apple-style minimalistic weight list
        for i, (_, entry) in enumerate(recent_weights.iterrows()):
            entry_id = entry.get('id', i)  # Use index if no ID available
            
            # Check if this entry is being edited
            is_editing = st.session_state.get(f'editing_weight_local_{entry_id}', False)
            
            if is_editing:
                # Show edit form inline
                show_edit_weight_form_local(dm, entry, lang)
            else:
                # Complete weight card with integrated buttons - no columns
                weight_value = entry.get('weight', 0.0)
                date = entry.get('date')
                if hasattr(date, 'strftime'):
                    date_str = date.strftime('%b %d, %Y')
                else:
                    date_str = str(date)[:10] if date else 'Unknown'
                
                # Single integrated card with buttons - using columns for buttons
                if st.session_state.get(f'confirm_delete_weight_local_{entry_id}', False):
                    # Confirmation mode
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{weight_value:.1f} kg</strong></div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{date_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for confirmation buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✓", key=f'confirm_yes_weight_local_{entry_id}', help="Confirm", use_container_width=True):
                            if dm.delete_weight_entry(entry_id):
                                st.success(get_text('weight_deleted', lang))
                                st.session_state[f'confirm_delete_weight_local_{entry_id}'] = False
                                st.rerun()
                            else:
                                st.error("Failed to delete weight entry")
                    with col3:
                        if st.button("✗", key=f'confirm_no_weight_local_{entry_id}', help="Cancel", use_container_width=True):
                            st.session_state[f'confirm_delete_weight_local_{entry_id}'] = False
                            st.rerun()
                else:
                    # Normal mode - integrated card with buttons
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{weight_value:.1f} kg</strong></div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{date_str}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✏️", key=f'edit_weight_local_{entry_id}', help="Edit", use_container_width=True):
                            st.session_state[f'editing_weight_local_{entry_id}'] = True
                            st.session_state['preserve_tab_state'] = True
                            st.rerun()
                    with col3:
                        if st.button("🗑️", key=f'delete_weight_local_{entry_id}', help="Delete", use_container_width=True):
                            st.session_state[f'confirm_delete_weight_local_{entry_id}'] = True
                            st.rerun()

def show_activity_history_db(db, lang):
    """Show activity history section for database version with Apple-style minimalistic design"""
    
    with st.expander(f"📋 {get_text('activity_history', lang)}", expanded=False):
        st.markdown(f"*{get_text('activity_history_subtitle', lang)}*")
        
        # Get recent activities (limit to 10 for display)
        activities = db.get_user_activities(st.session_state.user_id, "All time")[:10]
        
        if not activities:
            st.info(get_text('no_activities', lang))
            return
        
        # Apple-style minimalistic activity list
        for i, activity in enumerate(activities):
            # Check if this activity is being edited
            is_editing = st.session_state.get(f'editing_activity_db_{activity.id}', False)
            
            if is_editing:
                # Show edit form inline
                show_edit_activity_form_db(db, activity, lang)
            else:
                # Complete activity card with integrated buttons - no columns
                activity_type_en = getattr(activity, 'type', 'Unknown')
                activity_type_localized = get_text(activity_type_en.lower().replace(' ', '_').replace('-', '_'), lang)
                
                # Secondary info
                date_str = activity.date.strftime('%b %d, %Y')
                info_parts = [date_str]
                
                adaptation_en = getattr(activity, 'adaptation', '')
                if adaptation_en:
                    adaptation_localized = get_text(adaptation_en.lower().replace(' ', '_').replace('-', '_'), lang) if adaptation_en else ''
                    if adaptation_localized:
                        info_parts.append(adaptation_localized)
                
                if activity.description:
                    description_short = activity.description[:40] + '...' if len(activity.description) > 40 else activity.description
                    info_parts.append(f'"{description_short}"')
                
                secondary_info = ' · '.join(info_parts)
                
                # Single integrated card with buttons - using columns for buttons
                if st.session_state.get(f'confirm_delete_db_{activity.id}', False):
                    # Confirmation mode
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{activity_type_localized}</strong> · {activity.duration} min · {activity.intensity}</div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{secondary_info}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for confirmation buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✓", key=f'confirm_yes_db_{activity.id}', help="Confirm", use_container_width=True):
                            if db.delete_activity(st.session_state.user_id, activity.id):
                                st.success(get_text('activity_deleted', lang))
                                st.session_state[f'confirm_delete_db_{activity.id}'] = False
                                st.rerun()
                            else:
                                st.error("Failed to delete activity")
                    with col3:
                        if st.button("✗", key=f'confirm_no_db_{activity.id}', help="Cancel", use_container_width=True):
                            st.session_state[f'confirm_delete_db_{activity.id}'] = False
                            st.rerun()
                else:
                    # Normal mode - integrated card with buttons
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{activity_type_localized}</strong> · {activity.duration} min · {activity.intensity}</div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{secondary_info}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✏️", key=f'edit_db_{activity.id}', help="Edit", use_container_width=True):
                            st.session_state[f'editing_activity_db_{activity.id}'] = True
                            st.session_state['preserve_tab_state'] = True
                            st.rerun()
                    with col3:
                        if st.button("🗑️", key=f'delete_db_{activity.id}', help="Delete", use_container_width=True):
                            st.session_state[f'confirm_delete_db_{activity.id}'] = True
                            st.rerun()

def show_edit_weight_form_db(db, entry, lang):
    """Show inline edit form for weight entry - database version"""
    with st.form(f"edit_weight_form_db_{entry.id}"):
        st.markdown("**Edit Weight Entry**")
        
        col1, col2 = st.columns(2)
        with col1:
            new_weight = st.number_input(
                "Weight (kg)", 
                min_value=30.0, 
                max_value=200.0, 
                value=float(getattr(entry, 'weight', 70.0)),
                step=0.1,
                key=f"edit_weight_db_{entry.id}"
            )
        
        with col2:
            new_date = st.date_input(
                "Date", 
                value=entry.date.date() if hasattr(entry.date, 'date') else entry.date,
                key=f"edit_date_db_{entry.id}"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save Changes", use_container_width=True):
                if db.update_weight_entry(entry.id, new_weight, new_date):
                    st.success(get_text('weight_updated', lang))
                    st.session_state[f'editing_weight_db_{entry.id}'] = False
                    st.session_state['preserve_tab_state'] = True
                    st.rerun()
                else:
                    st.error("Failed to update weight entry")
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state[f'editing_weight_db_{entry.id}'] = False
                st.session_state['preserve_tab_state'] = True
                st.rerun()

def show_edit_weight_form_local(dm, entry, lang):
    """Show inline edit form for weight entry - local version"""
    entry_id = entry.get('id', 0)
    
    with st.form(f"edit_weight_form_local_{entry_id}"):
        st.markdown("**Edit Weight Entry**")
        
        col1, col2 = st.columns(2)
        with col1:
            new_weight = st.number_input(
                "Weight (kg)", 
                min_value=30.0, 
                max_value=200.0, 
                value=float(entry.get('weight', 70.0)),
                step=0.1,
                key=f"edit_weight_local_{entry_id}"
            )
        
        with col2:
            current_date = entry.get('date')
            if hasattr(current_date, 'date'):
                date_value = current_date.date()
            elif hasattr(current_date, 'strftime'):
                date_value = current_date
            else:
                date_value = datetime.now().date()
                
            new_date = st.date_input(
                "Date", 
                value=date_value,
                key=f"edit_date_local_{entry_id}"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save Changes", use_container_width=True):
                if dm.update_weight_entry(entry_id, new_weight, new_date):
                    st.success(get_text('weight_updated', lang))
                    st.session_state[f'editing_weight_local_{entry_id}'] = False
                    st.session_state['preserve_tab_state'] = True
                    st.rerun()
                else:
                    st.error("Failed to update weight entry")
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state[f'editing_weight_local_{entry_id}'] = False
                st.session_state['preserve_tab_state'] = True
                st.rerun()

def show_edit_activity_form_db(db, activity, lang):
    """Show edit form for activity in database version with Apple-style design"""
    # Clean edit form styling
    st.markdown(f"**✏️ {get_text('edit_activity', lang)}**")
    
    with st.form(f"edit_activity_db_{activity.id}"):        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get current activity type and convert to localized
            current_type_en = activity.type
            activity_types_localized = get_activity_types(lang)
            
            # Find the current activity type in localized list
            try:
                current_index = activity_types_localized.index(get_text(current_type_en.lower().replace(' ', '_').replace('-', '_'), lang))
            except (ValueError, KeyError):
                current_index = 0
            
            activity_type = st.selectbox(
                get_text('activity_type', lang),
                activity_types_localized,
                index=current_index,
                key=f"edit_type_db_{activity.id}"
            )
            
            duration = st.number_input(
                get_text('duration_minutes', lang), 
                min_value=1, 
                value=activity.duration,
                key=f"edit_duration_db_{activity.id}"
            )
            
            # Get current adaptation and convert to localized
            adaptations = get_adaptations(lang)
            current_adaptation_en = activity.adaptation or ''
            
            try:
                current_adaptation_localized = get_text(current_adaptation_en.lower().replace(' ', '_').replace('-', '_'), lang)
                adaptation_options = list(adaptations.keys())
                current_adaptation_index = adaptation_options.index(current_adaptation_localized) if current_adaptation_localized in adaptation_options else 0
            except (ValueError, KeyError):
                current_adaptation_index = 0
                
            selected_adaptation = st.selectbox(
                get_text('primary_adaptation', lang),
                list(adaptations.keys()),
                index=current_adaptation_index,
                key=f"edit_adaptation_db_{activity.id}"
            )
        
        with col2:
            # Get current intensity
            intensity_options = [get_text('low', lang), get_text('medium', lang), get_text('high', lang)]
            try:
                current_intensity_index = intensity_options.index(get_text(activity.intensity.lower(), lang))
            except (ValueError, KeyError):
                current_intensity_index = 0
                
            intensity = st.selectbox(
                get_text('intensity', lang), 
                intensity_options,
                index=current_intensity_index,
                key=f"edit_intensity_db_{activity.id}"
            )
            
            date = st.date_input(
                get_text('date', lang), 
                value=activity.date.date(),
                key=f"edit_date_db_{activity.id}"
            )
        
        description = st.text_area(
            get_text('description_optional', lang),
            value=activity.description or '',
            key=f"edit_description_db_{activity.id}",
            height=80
        )
        
        # Clean button layout
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            save = st.form_submit_button("✅ Save", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        with col3:
            st.empty()  # spacer
        
        if save:
            # Convert back to English for storage
            intensity_map = {
                get_text('low', lang): "Low",
                get_text('medium', lang): "Medium", 
                get_text('high', lang): "High"
            }
            intensity_en = intensity_map.get(intensity, "Low")
            
            activity_type_map = get_activity_type_mapping(lang)
            adaptation_map = get_adaptation_mapping(lang)
            
            activity_data = {
                'type': activity_type_map.get(activity_type, activity_type),
                'duration': duration,
                'intensity': intensity_en,
                'date': datetime.combine(date, datetime.now().time()),
                'description': description.strip(),
                'adaptation': adaptation_map.get(selected_adaptation, selected_adaptation)
            }
            
            if db.update_activity(st.session_state.user_id, activity.id, activity_data):
                st.success(get_text('activity_updated', lang))
                st.session_state[f'editing_activity_db_{activity.id}'] = False
                # Preserve tab state to avoid navigation issues
                st.session_state['preserve_tab_state'] = True
                st.rerun()
            else:
                st.error("Failed to update activity")
        
        if cancel:
            st.session_state[f'editing_activity_db_{activity.id}'] = False
            # Preserve tab state to avoid navigation issues
            st.session_state['preserve_tab_state'] = True
            st.rerun()

def show_activity_history_local(dm, lang):
    """Show activity history section for local version with Apple-style minimalistic design"""
    
    with st.expander(f"📋 {get_text('activity_history', lang)}", expanded=False):
        st.markdown(f"*{get_text('activity_history_subtitle', lang)}*")
        
        # Get recent activities (limit to 10 for display)
        activities_df = dm.get_recent_activities(10)
        
        if activities_df.empty:
            st.info(get_text('no_activities', lang))
            return
        
        # Apple-style minimalistic activity list
        for i, (idx, activity) in enumerate(activities_df.iterrows()):
            activity_id = activity.get('id', f'activity_{i}')
            # Check if this activity is being edited
            is_editing = st.session_state.get(f'editing_activity_local_{activity_id}', False)
            
            if is_editing:
                # Show edit form inline
                show_edit_activity_form_local(dm, activity, lang)
            else:
                # Complete activity card with integrated buttons - no columns
                activity_type = activity.get('type', 'Unknown')
                duration = activity.get('duration', 0)
                intensity = activity.get('intensity', 'Low')
                
                # Secondary info
                date = activity.get('date')
                if hasattr(date, 'strftime'):
                    date_str = date.strftime('%b %d, %Y')
                else:
                    date_str = str(date)[:10] if date else 'Unknown'
                
                info_parts = [date_str]
                
                adaptation = activity.get('adaptation', '')
                if adaptation:
                    info_parts.append(adaptation)
                
                description = activity.get('description', '')
                if description:
                    description_short = description[:40] + '...' if len(description) > 40 else description
                    info_parts.append(f'"{description_short}"')
                
                secondary_info = ' · '.join(info_parts)
                
                # Single integrated card with buttons - using columns for buttons
                if st.session_state.get(f'confirm_delete_local_{activity_id}', False):
                    # Confirmation mode
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{activity_type}</strong> · {duration} min · {intensity}</div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{secondary_info}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for confirmation buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✓", key=f'confirm_yes_local_{activity_id}', help="Confirm", use_container_width=True):
                            if dm.delete_activity(activity_id):
                                st.success(get_text('activity_deleted', lang))
                                st.session_state[f'confirm_delete_local_{activity_id}'] = False
                                st.rerun()
                            else:
                                st.error("Failed to delete activity")
                    with col3:
                        if st.button("✗", key=f'confirm_no_local_{activity_id}', help="Cancel", use_container_width=True):
                            st.session_state[f'confirm_delete_local_{activity_id}'] = False
                            st.rerun()
                else:
                    # Normal mode - integrated card with buttons
                    st.markdown(f"""
                    <div style="
                        background: rgba(248, 249, 250, 0.6);
                        border-radius: 12px;
                        padding: 12px;
                        margin: 4px 0;
                        border: 1px solid rgba(0, 0, 0, 0.06);
                    ">
                        <div><strong>{activity_type}</strong> · {duration} min · {intensity}</div>
                        <div style="color: #8E8E93; font-size: 14px; margin-top: 4px;">{secondary_info}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for buttons with proper spacing
                    col1, col2, col3 = st.columns([7, 1.5, 1.5])
                    with col1:
                        st.empty()  # This pushes buttons to the right
                    with col2:
                        if st.button("✏️", key=f'edit_local_{activity_id}', help="Edit", use_container_width=True):
                            st.session_state[f'editing_activity_local_{activity_id}'] = True
                            st.session_state['preserve_tab_state'] = True
                            st.rerun()
                    with col3:
                        if st.button("🗑️", key=f'delete_local_{activity_id}', help="Delete", use_container_width=True):
                            st.session_state[f'confirm_delete_local_{activity_id}'] = True
                            st.rerun()

def show_edit_activity_form_local(dm, activity, lang):
    """Show edit form for activity in local version with Apple-style design"""
    activity_id = activity.get('id', 'unknown')
    
    # Clean edit form styling
    st.markdown(f"**✏️ {get_text('edit_activity', lang)}**")
    
    with st.form(f"edit_activity_local_{activity_id}"):        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get current activity type
            current_type = activity.get('type', 'Running')
            activity_types_localized = get_activity_types(lang)
            
            try:
                current_index = activity_types_localized.index(current_type)
            except ValueError:
                current_index = 0
            
            activity_type = st.selectbox(
                get_text('activity_type', lang),
                activity_types_localized,
                index=current_index,
                key=f"edit_type_local_{activity_id}"
            )
            
            duration = st.number_input(
                get_text('duration_minutes', lang), 
                min_value=1, 
                value=int(activity.get('duration', 30)),
                key=f"edit_duration_local_{activity_id}"
            )
            
            # Get current adaptation
            adaptations = get_adaptations(lang)
            current_adaptation = activity.get('adaptation', '')
            
            try:
                adaptation_options = list(adaptations.keys())
                current_adaptation_index = adaptation_options.index(current_adaptation) if current_adaptation in adaptation_options else 0
            except (ValueError, KeyError):
                current_adaptation_index = 0
                
            selected_adaptation = st.selectbox(
                get_text('primary_adaptation', lang),
                list(adaptations.keys()),
                index=current_adaptation_index,
                key=f"edit_adaptation_local_{activity_id}"
            )
        
        with col2:
            # Get current intensity
            intensity_options = [get_text('low', lang), get_text('medium', lang), get_text('high', lang)]
            current_intensity = activity.get('intensity', 'Low')
            
            try:
                current_intensity_localized = get_text(current_intensity.lower(), lang)
                current_intensity_index = intensity_options.index(current_intensity_localized)
            except (ValueError, KeyError):
                current_intensity_index = 0
                
            intensity = st.selectbox(
                get_text('intensity', lang), 
                intensity_options,
                index=current_intensity_index,
                key=f"edit_intensity_local_{activity_id}"
            )
            
            current_date = activity.get('date')
            if hasattr(current_date, 'date'):
                date_value = current_date.date()
            else:
                try:
                    date_value = pd.to_datetime(current_date).date()
                except:
                    date_value = datetime.now().date()
            
            date = st.date_input(
                get_text('date', lang), 
                value=date_value,
                key=f"edit_date_local_{activity_id}"
            )
        
        description = st.text_area(
            get_text('description_optional', lang),
            value=activity.get('description', ''),
            key=f"edit_description_local_{activity_id}",
            height=80
        )
        
        # Clean button layout
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            save = st.form_submit_button("✅ Save", use_container_width=True, type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        with col3:
            st.empty()  # spacer
        
        if save:
            # Convert back to English for storage
            intensity_map = {
                get_text('low', lang): "Low",
                get_text('medium', lang): "Medium", 
                get_text('high', lang): "High"
            }
            intensity_en = intensity_map.get(intensity, "Low")
            
            activity_data = {
                'type': activity_type,
                'duration': duration,
                'intensity': intensity_en,
                'date': datetime.combine(date, datetime.now().time()),
                'description': description.strip() if description else '',
                'adaptation': selected_adaptation
            }
            
            if dm.update_activity(activity_id, activity_data):
                st.success(get_text('activity_updated', lang))
                st.session_state[f'editing_activity_local_{activity_id}'] = False
                # Preserve tab state to avoid navigation issues
                st.session_state['preserve_tab_state'] = True
                st.rerun()
            else:
                st.error("Failed to update activity")
        
        if cancel:
            st.session_state[f'editing_activity_local_{activity_id}'] = False
            # Preserve tab state to avoid navigation issues
            st.session_state['preserve_tab_state'] = True
            st.rerun()

if __name__ == "__main__":
    main()
