# Configuration settings for the Web Methods to SnapLogic Migration Accelerator
import streamlit as st

# Backend API endpoint
API_ENDPOINT = st.secrets["SNAPLOGIC_API_ENDPOINT"]
API_BEARER_TOKEN = st.secrets["SNAPLOGIC_API_TOKEN"]

# Application settings
MAX_UPLOAD_SIZE_MB = 100
SUPPORTED_FILE_TYPES = ["zip"]

# Feature flags
ENABLE_DOCUMENTATION = True
ENABLE_FIELD_MAPPINGS = True
ENABLE_TRANSFORMATIONS = True
ENABLE_DEPENDENCY_ANALYSIS = True 