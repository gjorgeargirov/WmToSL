import streamlit as st
from typing import Optional, List, Dict, Any
import time

def apply_custom_styling():
    """Apply custom styling to the application"""
    st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header styling */
        .main h1 {
            color: #1E88E5;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        /* Description text styling */
        .main p {
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        /* Migrate button styling */
        .migrate-button>button {
            background-color: #4CAF50;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            transition: all 0.3s ease;
            width: auto;
            min-width: unset;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .migrate-button>button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* File uploader styling */
        .uploadedFile {
            border: 2px dashed #1E88E5;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            background-color: #1E88E5;
        }
        
        /* Success message styling */
        .success-message {
            background-color: #E8F5E9;
            border-left: 4px solid #4CAF50;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }
        
        /* Error message styling */
        .error-message {
            background-color: #FFEBEE;
            border-left: 4px solid #F44336;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
        }
        
        /* Tooltip styling */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            background-color: #f8f9fa;
            color: #333;
            text-align: center;
            padding: 5px 10px;
            border-radius: 6px;
            border: 1px solid #ddd;
            
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
    </style>
    """, unsafe_allow_html=True)

def show_progress_bar(message: str, progress: float):
    """Show a progress bar with a message"""
    st.progress(progress)
    st.text(message)

def show_success_message(message: str, details: Optional[Dict[str, Any]] = None):
    """Show a success message with optional details"""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)
    
    if details:
        st.json(details)

def show_error_message(message: str, details: Optional[str] = None):
    """Show an error message with optional details"""
    st.markdown(f"""
    <div class="error-message">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)
    
    if details:
        st.text(details)

def show_migration_status(project_name: str, status: str):
    """Show the current migration status"""
    status_emoji = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "failed": "❌"
    }.get(status, "❓")
    
    st.markdown(f"""
    ### Migration Status: {status_emoji} {project_name}
    **Current Status:** {status.replace('_', ' ').title()}
    """)

def show_migration_history(history: List[str]):
    """Show the migration history in a formatted way"""
    if not history:
        st.sidebar.info("No migrations yet.")
        return
        
    st.sidebar.markdown("### 📋 Recent Migrations")
    for project in history[-5:]:  # Show last 5 migrations
        st.sidebar.markdown(f"- {project}")
    
    if len(history) > 5:
        st.sidebar.markdown(f"... and {len(history) - 5} more")

def show_file_preview(file):
    """Show a preview of the uploaded file"""
    if file is not None:
        st.markdown("### 📁 File Details")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Name", file.name)
        with col2:
            st.metric("File Size", f"{file.size / 1024 / 1024:.2f} MB")

def show_tooltip(text: str, tooltip_text: str) -> None:
    """Show text with a tooltip"""
    st.markdown(f"""
    <div class="tooltip">
        {text}
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    """, unsafe_allow_html=True) 