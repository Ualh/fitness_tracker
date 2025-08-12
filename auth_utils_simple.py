"""Simple authentication utilities for remember me functionality"""

import streamlit as st
import hashlib
import time
from typing import Optional, Any

def get_device_fingerprint() -> str:
    """Generate a simple device fingerprint for this browser session"""
    # Create a fingerprint based on available browser info
    # In Streamlit, we'll use a combination of factors
    user_agent = st.get_option("browser.serverAddress") or "unknown"
    return hashlib.md5(f"{user_agent}_{time.time()}".encode()).hexdigest()

def save_remember_credentials(db_manager, user_id: int, username: str) -> None:
    """Save remember me credentials by setting remember token in database"""
    # Generate a remember token and save it to the database
    token = db_manager.set_remember_token(user_id, generate_token=True)
    if token:
        # Store username and token in query parameters for persistence
        st.query_params["remember_user"] = username
        st.query_params["remember_token"] = token[:16]  # Store only part of token for security

def get_remember_credentials() -> Optional[dict]:
    """Get remember me credentials from query parameters"""
    try:
        remember_user = st.query_params.get("remember_user")
        remember_token_part = st.query_params.get("remember_token")
        
        if remember_user and remember_token_part:
            return {
                'username': remember_user,
                'token_part': remember_token_part
            }
    except Exception:
        pass
    
    return None

def clear_remember_credentials() -> None:
    """Clear remember me credentials"""
    try:
        if "remember_user" in st.query_params:
            del st.query_params["remember_user"]
        if "remember_token" in st.query_params:
            del st.query_params["remember_token"]
    except Exception:
        pass

def authenticate_remember_token(db_manager, username: str, token_part: str) -> Optional[Any]:
    """Authenticate using partial token match"""
    try:
        # Get user from database
        session = db_manager.get_session()
        from database import User
        user = session.query(User).filter(User.username == username).first()
        session.close()
        
        if user and user.remember_token and user.remember_token.startswith(token_part):
            return user
    except Exception:
        pass
    
    return None

def setup_auto_login(db_manager) -> bool:
    """Setup auto-login if remember me credentials exist"""
    # Only attempt auto-login if user is not already logged in
    if not st.session_state.get('user'):
        credentials = get_remember_credentials()
        if credentials:
            username = credentials['username']
            token_part = credentials['token_part']
            
            user = authenticate_remember_token(db_manager, username, token_part)
            if user:
                # Set session state for logged in user
                st.session_state.user = user
                st.session_state.user_id = user.id
                st.session_state.dark_mode = user.dark_mode
                st.session_state.language = user.preferred_language
                return True
            else:
                # If authentication fails, clear the credentials
                clear_remember_credentials()
    
    return False