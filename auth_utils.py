"""Authentication utilities for remember me functionality"""

import streamlit as st
import json
import base64
import hashlib
import os
from typing import Optional, Dict, Any

def _get_browser_storage_key():
    """Generate a unique key for browser storage based on session"""
    # Use a combination of factors to create a persistent key
    session_info = str(st.runtime.scriptrunner.get_script_run_ctx().session_id)
    return f"fitness_remember_{hashlib.md5(session_info.encode()).hexdigest()[:8]}"

def save_remember_credentials(username: str, token: str) -> None:
    """Save remember me credentials to persistent storage"""
    # Create credentials object
    credentials = {
        'username': username,
        'token': token
    }
    
    # Encode credentials
    encoded_creds = base64.b64encode(json.dumps(credentials).encode()).decode()
    
    # Store in session state for current session
    st.session_state.remember_credentials = encoded_creds
    
    # Use JavaScript to store in localStorage via Streamlit components
    storage_key = _get_browser_storage_key()
    
    # Store the credentials using a hidden component that persists in localStorage simulation
    # Since we can't use real localStorage in Streamlit, we use a file-based approach
    try:
        import os
        storage_dir = "/tmp/streamlit_storage"
        os.makedirs(storage_dir, exist_ok=True)
        
        with open(f"{storage_dir}/{storage_key}.json", "w") as f:
            json.dump(credentials, f)
    except Exception:
        pass  # Fallback gracefully if file storage fails

def get_remember_credentials() -> Optional[Dict[str, str]]:
    """Retrieve remember me credentials from persistent storage"""
    try:
        # First check session state (for current session)
        if hasattr(st.session_state, 'remember_credentials'):
            encoded_creds = st.session_state.remember_credentials
            credentials_json = base64.b64decode(encoded_creds.encode()).decode()
            return json.loads(credentials_json)
        
        # Then try file-based storage for persistence across sessions
        storage_key = _get_browser_storage_key()
        storage_dir = "/tmp/streamlit_storage"
        storage_file = f"{storage_dir}/{storage_key}.json"
        
        if os.path.exists(storage_file):
            with open(storage_file, "r") as f:
                credentials = json.load(f)
                return credentials
                
    except Exception:
        # If there's any error, clear the credentials
        clear_remember_credentials()
    
    return None

def clear_remember_credentials() -> None:
    """Clear remember me credentials from all storage locations"""
    # Clear from session state
    if hasattr(st.session_state, 'remember_credentials'):
        del st.session_state.remember_credentials
    
    # Clear from file storage
    try:
        storage_key = _get_browser_storage_key()
        storage_dir = "/tmp/streamlit_storage"
        storage_file = f"{storage_dir}/{storage_key}.json"
        
        if os.path.exists(storage_file):
            os.remove(storage_file)
    except Exception:
        pass  # Fail gracefully

def auto_login_user(db_manager) -> Optional[Any]:
    """Attempt to auto-login user using remember me credentials"""
    credentials = get_remember_credentials()
    if credentials:
        username = credentials.get('username')
        token = credentials.get('token')
        
        if username and token:
            # Try to authenticate using the token
            user = db_manager.authenticate_by_token(username, token)
            if user:
                return user
            else:
                # If token authentication fails, clear the credentials
                clear_remember_credentials()
    
    return None

def setup_auto_login(db_manager) -> bool:
    """Setup auto-login if remember me credentials exist"""
    # Only attempt auto-login if user is not already logged in
    if not st.session_state.get('user'):
        user = auto_login_user(db_manager)
        if user:
            # Set session state for logged in user
            st.session_state.user = user
            st.session_state.user_id = user.id
            st.session_state.dark_mode = user.dark_mode
            st.session_state.language = user.preferred_language
            return True
    
    return False