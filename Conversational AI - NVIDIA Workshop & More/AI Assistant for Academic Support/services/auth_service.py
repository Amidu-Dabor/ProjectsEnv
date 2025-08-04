# services/auth_service.py

import time
import threading
import uuid
from typing import Dict, Optional, Any

# Sample credentials
users = {
    "adabor@usiu.ac.ke": "student123",
    "adavid@usiu.ac.ke": "faculty123",
    "jmilton@usiu.ac.ke": "staff123"
}

# Active user sessions storage
active_sessions: Dict[str, Dict[str, Any]] = {}

# Inactivity timeout in seconds (60 seconds for testing)
INACTIVITY_TIMEOUT = 60
WARNING_TIMEOUT = 40  # Show warning after 40 seconds of inactivity

def authenticate(user_id: str, password: str) -> bool:
    """Return True if the provided credentials match the lookup table."""
    return users.get(user_id) == password

def create_session(user_id: str) -> str:
    """Create a new user session with a unique session ID."""
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "user_id": user_id,
        "logged_in": True,
        "last_activity": time.time(),
        "created_at": time.time()
    }
    return session_id

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data for a given session ID."""
    if session_id in active_sessions:
        # Check if session has expired
        if not is_session_active(session_id):
            # Auto-end expired sessions when accessed
            end_session(session_id)
            return None
        return active_sessions[session_id]
    return None

def update_session_activity(session_id: str) -> bool:
    """Update the last activity timestamp for a session."""
    if session_id in active_sessions and active_sessions[session_id]["logged_in"]:
        active_sessions[session_id]["last_activity"] = time.time()
        return True
    return False

def end_session(session_id: str) -> bool:
    """End a user session."""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return True
    return False

def is_session_active(session_id: str) -> bool:
    """Check if a session is still active and not expired."""
    if session_id not in active_sessions or not active_sessions[session_id]["logged_in"]:
        return False
    
    current_time = time.time()
    last_activity = active_sessions[session_id]["last_activity"]
    
    return (current_time - last_activity) < INACTIVITY_TIMEOUT

def get_session_remaining_time(session_id: str) -> int:
    """Get remaining time in seconds before session expires."""
    if session_id not in active_sessions:
        return 0
    
    current_time = time.time()
    last_activity = active_sessions[session_id]["last_activity"]
    elapsed_time = current_time - last_activity
    
    if elapsed_time >= INACTIVITY_TIMEOUT:
        return 0
    
    return int(INACTIVITY_TIMEOUT - elapsed_time)

# Function to check if warning should be shown
def should_show_warning(session_id: str) -> bool:
    """Check if inactivity warning should be shown."""
    if session_id not in active_sessions:
        return False
    
    current_time = time.time()
    last_activity = active_sessions[session_id]["last_activity"]
    elapsed_time = current_time - last_activity
    
    return elapsed_time >= WARNING_TIMEOUT and elapsed_time < INACTIVITY_TIMEOUT

# Periodic cleanup function
def clear_expired_sessions():
    """Clear all expired sessions."""
    current_time = time.time()
    sessions_to_remove = []
    
    for session_id, session_data in active_sessions.items():
        last_activity = session_data["last_activity"]
        if current_time - last_activity >= INACTIVITY_TIMEOUT:
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        end_session(session_id)
    
    return len(sessions_to_remove)

# Start a background thread to periodically clean up expired sessions
def setup_session_cleanup(interval=60):  # Run every minute
    def cleanup_task():
        while True:
            clear_expired_sessions()
            time.sleep(interval)
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

# Initialize the session cleanup thread
setup_session_cleanup()