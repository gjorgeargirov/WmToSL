import streamlit as st
from typing import Optional, Any
import requests
import json

class MigrationError(Exception):
    """Custom exception for migration-related errors"""
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

def handle_api_error(response: requests.Response) -> None:
    """Handle API response errors with detailed messages"""
    try:
        error_data = response.json()
        error_message = error_data.get('message', 'Unknown error occurred')
        error_details = error_data.get('details', {})
        
        st.error(f"""
        🚫 API Error: {error_message}
        
        Details:
        {json.dumps(error_details, indent=2)}
        """)
    except json.JSONDecodeError:
        st.error(f"""
        🚫 API Error (Status {response.status_code}):
        {response.text}
        """)

def handle_file_validation(file) -> bool:
    """Validate uploaded file"""
    if file is None:
        st.warning("⚠️ Please upload a ZIP file.")
        return False
        
    if not file.name.endswith('.zip'):
        st.error("❌ Invalid file type. Please upload a ZIP file.")
        return False
        
    # Check file size (e.g., 100MB limit)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
    if file.size > MAX_FILE_SIZE:
        st.error(f"❌ File too large. Maximum size is 100MB.")
        return False
        
    return True

def handle_network_error(error: requests.exceptions.RequestException) -> None:
    """Handle network-related errors"""
    error_message = str(error)
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("""
        🔌 Connection Error:
        Unable to connect to the SnapLogic API. Please check:
        1. Your internet connection
        2. The API endpoint is accessible
        3. Your network allows the connection
        """)
    elif isinstance(error, requests.exceptions.Timeout):
        st.error("""
        ⏰ Request Timeout:
        The request took too long to complete. Please try again.
        """)
    else:
        st.error(f"""
        🌐 Network Error:
        {error_message}
        """)

def handle_migration_error(error: MigrationError) -> None:
    """Handle migration-specific errors"""
    st.error(f"""
    ❌ Migration Error:
    {error.message}
    
    Details:
    {json.dumps(error.details, indent=2) if error.details else 'No additional details available'}
    """) 