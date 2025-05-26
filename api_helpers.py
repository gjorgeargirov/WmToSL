import requests
import json
import streamlit as st
import config
import time
import traceback
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_session():
    """
    Create a requests session with retry logic
    
    Returns:
        requests.Session: Configured session with retry capabilities
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def validate_file(uploaded_file):
    """
    Validate the uploaded file
    
    Args:
        uploaded_file: The file uploaded by the user
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in config.SUPPORTED_FILE_TYPES:
        return False, f"Unsupported file type. Please upload a {', '.join(config.SUPPORTED_FILE_TYPES)} file."
    
    # Check file size (convert MB to bytes)
    max_size_bytes = config.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        return False, f"File too large. Maximum size is {config.MAX_UPLOAD_SIZE_MB}MB."
    
    return True, ""

def send_to_api(uploaded_file, migration_options):
    """
    Send the uploaded file to the backend API for processing
    
    Args:
        uploaded_file: The file uploaded by the user
        migration_options: Dictionary with migration settings (not used in API call)
        
    Returns:
        dict: API response or error message
    """
    try:
        # Using a regular session without retries
        session = requests.Session()
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        headers = {
            "Authorization": f"{config.API_BEARER_TOKEN}"
        }
        
        # Debug info
        print(f"Using endpoint: {config.API_ENDPOINT}")
        print(f"Auth header: {headers['Authorization'][:10]}...")
        print(f"File size: {len(uploaded_file.getvalue())} bytes")
        
        try:
            # Single request with long timeout
            response = session.post(
                config.API_ENDPOINT,
                files=files,
                headers=headers
            )
            
            # Debug: print status and content
            print(f"Status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            # Try to get response content for debugging
            try:
                content_preview = response.text[:500]
                print(f"Response preview: {content_preview}")
            except:
                print("Could not get response preview")
            
            if response.status_code == 200:
                try:
                    return {"success": True, "data": response.json()}
                except Exception as e:
                    return {"success": False, "error": f"JSON decode error: {e}\nRaw response: {response.text[:1000]}"}
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code} - {response.text[:1000]}"
                }
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except requests.exceptions.ReadTimeout:
            return {"success": False, "error": "API request timed out. The server might be busy or the file may be too large."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Unexpected error: {error_details}")
        return {"success": False, "error": f"Unexpected error: {str(e)}\n\nPlease check network settings and API configuration."}

def simulate_processing(migration_options):
    """
    Simulate API processing for demo purposes
    
    Args:
        migration_options: Dictionary with migration settings
        
    Returns:
        dict: Simulated API response
    """
    # Count enabled options to affect the simulated conversion rate
    enabled_options = sum(1 for value in migration_options.values() if value)
    
    # Better conversion rate if more options are enabled
    conversion_rate = min(95, 70 + (enabled_options * 5))
    
    # Random data based on enabled options
    converted_services = 10 + (enabled_options * 2)
    converted_flows = 5 + (enabled_options * 3)
    warning_count = max(1, 10 - (enabled_options * 2))
    
    sample_response = {
        "migrationId": f"m{hash(str(migration_options)) % 100000}",
        "convertedServices": converted_services,
        "convertedFlows": converted_flows,
        "conversionRate": conversion_rate,
        "warningCount": warning_count,
        "nextSteps": "Review the generated SnapLogic pipelines and address any warnings."
    }
    
    return {"success": True, "data": sample_response} 