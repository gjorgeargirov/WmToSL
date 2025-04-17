import streamlit as st
import requests
import json
import os
import time
from dotenv import load_dotenv
from error_handlers import (
    handle_api_error,
    handle_file_validation,
    handle_network_error,
    handle_migration_error,
    MigrationError
)
from ui_components import (
    apply_custom_styling,
    show_progress_bar,
    show_success_message,
    show_error_message,
    show_migration_status,
    show_migration_history,
    show_file_preview,
    show_tooltip
)
from migration_estimator import MigrationEstimator
from datetime import datetime

# Load environment variables
load_dotenv()

# Set page config with improved layout
st.set_page_config(
    page_title="WM to SnapLogic Migrator",
    page_icon="icon.webp",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Hide sidebar and other default elements
st.markdown("""
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }

    /* Base styles */
    .main-header {
        background: linear-gradient(90deg, #1E88E5 0%, #1976D2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.5s ease;
        width: calc(66.67% - 1rem);
        box-sizing: border-box;
    }
    .main-header h1 {
        color: white !important;
        margin: 0 !important;
        font-size: 2rem !important;
        line-height: 1.2 !important;
        margin-bottom: 0.5rem !important;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem !important;
        line-height: 1.4 !important;
        margin-top: 1rem;
        margin-bottom: 0;
    }
    .steps-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        transition: all 0.3s ease;
        width: 100%;
        box-sizing: border-box;
    }
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        width: 100%;
        box-sizing: border-box;
    }
    .upload-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 2px dashed #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
        width: 100%;
        box-sizing: border-box;
    }

    /* Layout adjustments */
    [data-testid="stHorizontalBlock"] {
        align-items: flex-start !important;
        gap: 2rem !important;
    }

    /* Right column adjustments */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        margin-top: -13.2rem !important;
        padding-top: 0 !important;
    }

    /* Ensure proper spacing between right column elements */
    [data-testid="stExpander"] {
        z-index: 1;
        margin-bottom: 1rem !important;
    }

    .stats-card {
        margin-top: 1rem !important;
    }

    /* Adjust main header to prevent any overlap */
    .main-header {
        z-index: 0;
        position: relative;
        margin-bottom: 3rem !important;
    }

    /* Other styles */
    .step-item {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 4px;
        transition: background-color 0.3s;
    }
    .step-number {
        background: #1E88E5;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 0.9rem;
    }
    .stat-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .stat-item:last-child {
        border-bottom: none;
    }
    @keyframes slideIn {
        from {
            transform: translateY(-10px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize migration estimator
estimator = MigrationEstimator()

# Get secrets with error handling
try:
    SNAPLOGIC_URL = st.secrets["SNAPLOGIC_URL"]
    SNAPLOGIC_BEARER_TOKEN = st.secrets["SNAPLOGIC_BEARER_TOKEN"]
except Exception as e:
    show_error_message(
        "Configuration Error: Missing required secrets.",
        """Please ensure you have set up the following in your .streamlit/secrets.toml file:
        
        SNAPLOGIC_URL = "your-url-here"
        SNAPLOGIC_BEARER_TOKEN = "your-token-here"
        
        For deployment: Add these values in the app's "Advanced settings" section."""
    )
    st.stop()

# File to store migration history locally
HISTORY_FILE = "migration_history.json"

# Function to format timestamp
def format_timestamp(timestamp_str):
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        return timestamp.strftime("%Y-%m-%d %H:%M")
    except:
        return "N/A"

# Function to load migration history from file
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    return []

# Function to save migration history to file
def save_history(history):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(history, file)

# Initialize session state variables
if 'migration_history' not in st.session_state:
    st.session_state['migration_history'] = load_history()
if 'current_migration' not in st.session_state:
    st.session_state['current_migration'] = None
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False
if 'upload_key' not in st.session_state:
    st.session_state['upload_key'] = 0

def reset_upload():
    """Reset the file uploader by incrementing the key"""
    st.session_state['upload_key'] += 1

# Configure page and theme
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False

# Main page header with animation and improved styling
st.markdown("""
<div class="main-header">
    <h1>webMethods to SnapLogic Migration Tool</h1>
    <p>Welcome to the webMethods to SnapLogic Migration Tool! This application helps you migrate your integration projects 
    from webMethods to SnapLogic seamlessly.</p>
</div>
""", unsafe_allow_html=True)

# Create two columns with different ratios (2:1 for left:right)
col_left, col_right = st.columns([2, 1])

# Left column - How it works and Upload section
with col_left:
    # Steps section with improved styling
    st.markdown("""
    <div class="steps-container">
        <h3>🔄 How it works:</h3>
        <div class="step-item">
            <div class="step-number">1</div>
            <div><strong>Upload your webMethods project</strong> as a ZIP file</div>
        </div>
        <div class="step-item">
            <div class="step-number">2</div>
            <div><strong>Review</strong> the file details and project name</div>
        </div>
        <div class="step-item">
            <div class="step-number">3</div>
            <div>Click the <strong>Migrate</strong> button to start the migration process</div>
        </div>
        <div class="step-item">
            <div class="step-number">4</div>
            <div><strong>Monitor</strong> the migration progress</div>
        </div>
        <div class="step-item">
            <div class="step-number">5</div>
            <div><strong>View</strong> the migration results</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload section
    uploaded_file = st.file_uploader(
        "Upload your webMethods project ZIP file",
        type="zip",
        key=f"project_uploader_{st.session_state['upload_key']}",
        help="Upload a ZIP file containing your webMethods project artifacts.",
        on_change=None
    )
    
    # Show file preview and time estimate if a file is uploaded
    if uploaded_file is not None:
        st.markdown("""
        <div class="skeleton"></div>
        <div class="skeleton" style="width: 60%;"></div>
        """, unsafe_allow_html=True)
        show_file_preview(uploaded_file)
        
        # Calculate and show time estimate
        file_size_mb = uploaded_file.size / (1024 * 1024)
        estimated_time, estimate_details = estimator.estimate_migration_time(file_size_mb)
        
        # Show time estimate with confidence level
        st.markdown("### ⏱️ Migration Time Estimate")
        st.markdown(f"""
        <div class="info-message" style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #1E88E5;">
            <h4 style="color: #1E88E5; margin-bottom: 0.5rem;">Estimated Duration: {estimator.format_time_estimate(estimated_time)}</h4>
            <p style="margin-bottom: 0.5rem;"><strong>Confidence Level:</strong> {estimate_details['confidence'].title()}</p>
            <p style="margin-bottom: 0.5rem;"><strong>File Size:</strong> {file_size_mb:.2f} MB</p>
            <p style="margin-bottom: 0.5rem;"><strong>Complexity:</strong> {estimate_details['complexity'].title()}</p>
            <p style="color: #666; font-style: italic;">{estimate_details['explanation']}</p>
            {f'<p style="color: #666;"><strong>Note:</strong> {estimate_details["note"]}</p>' if 'note' in estimate_details else ''}
            {f'<p style="color: #666;"><strong>Similar Files Range:</strong> {estimate_details["similar_sizes_range"]}</p>' if 'similar_sizes_range' in estimate_details else ''}
            {f'<p style="color: #666;"><strong>Data Range:</strong> {estimate_details["data_range"]}</p>' if 'data_range' in estimate_details else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Add a clear button
        if st.button("Clear File", key="clear_file"):
            reset_upload()
            st.rerun()
        
        # Migrate button
        migrate_button = st.button(
            "🚀 Start Migration",
            type="primary",
            key="migrate_button",
            help="Click to start the migration process",
            use_container_width=True
        )
        
        if migrate_button:
            # Validate file before proceeding
            if not handle_file_validation(uploaded_file):
                st.stop()

            # Extract and validate project name
            project_name = uploaded_file.name.replace(".zip", "")
            if not project_name:
                show_error_message("Invalid project name. The ZIP file name cannot be empty.")
                st.stop()

            # Update current migration status
            start_time = time.time()
            st.session_state['current_migration'] = {
                'name': project_name,
                'status': 'in_progress',
                'start_time': start_time
            }

            # Show animated progress bar and status
            show_migration_status(project_name, "in_progress")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Send the request to the SnapLogic API with shorter timeout
                with st.spinner(""):
                    # Initial progress
                    status_text.text("Initiating migration...")
                    progress_bar.progress(0.1)
                    time.sleep(0.5)  # Small delay for visual feedback
                    
                    # Simulate progress during API request
                    for i in range(1, 9):
                        progress_bar.progress(0.1 + (i * 0.1))
                        time.sleep(0.2)  # Small delay between updates
                    
                    response = requests.post(
                        SNAPLOGIC_URL,
                        headers={
                            "Authorization": f"Bearer {SNAPLOGIC_BEARER_TOKEN}",
                            "Content-Type": "application/octet-stream",
                        },
                        params={"projectName": project_name},
                        data=uploaded_file.getvalue(),
                    )
                    
                    # Final progress updates
                    progress_bar.progress(0.9)
                    status_text.text("Finalizing migration...")
                    time.sleep(0.5)  # Small delay for visual feedback
                    progress_bar.progress(1.0)
                
                # Calculate actual duration
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    show_toast("Migration completed successfully! 🎉", "success")
                    show_success_message(
                        "Migration completed successfully! 🎉",
                        response.json()
                    )
                    
                    # Update migration history
                    st.session_state['migration_history'].append(project_name)
                    save_history(st.session_state['migration_history'])
                    
                    # Add migration record
                    estimator.add_migration_record(project_name, file_size_mb, duration)
                    
                    # Update status and reset upload
                    st.session_state['current_migration']['status'] = 'completed'
                    reset_upload()
                    st.rerun()
                else:
                    show_toast("Migration failed. Please check the error details.", "error")
                    status_text.text("Migration failed. Please check the error details.")
                    handle_api_error(response)
                    st.session_state['current_migration']['status'] = 'failed'
                    
            except requests.exceptions.RequestException as e:
                progress_bar.empty()
                status_text.text("Network error occurred. Please check your connection.")
                handle_network_error(e)
                st.session_state['current_migration']['status'] = 'failed'
            except Exception as e:
                progress_bar.empty()
                status_text.text("An unexpected error occurred.")
                handle_migration_error(MigrationError(
                    "An unexpected error occurred during migration",
                    {"error": str(e)}
                ))
                st.session_state['current_migration']['status'] = 'failed'

# Right column - Settings, Statistics, and History
with col_right:
    # Settings expander
    with st.expander("⚙️ Settings", expanded=False):
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state['dark_mode'])
        if dark_mode != st.session_state['dark_mode']:
            st.session_state['dark_mode'] = dark_mode
            st.rerun()

    # Statistics section
    stats = estimator.get_migration_statistics()
    if stats["total_migrations"] > 0:
        st.markdown("""
        <div class="stats-card">
            <h3>📊 Migration Statistics</h3>
            <div class="stat-item">
                <span>📈 Total Migrations</span>
                <strong>{}</strong>
            </div>
            <div class="stat-item">
                <span>⏱️ Average Time</span>
                <strong>{}</strong>
            </div>
            <div class="stat-item">
                <span>📦 Average Size</span>
                <strong>{:.2f} MB</strong>
            </div>
            <div class="stat-item">
                <span>⌛ Median Time</span>
                <strong>{}</strong>
            </div>
            <div class="stat-item">
                <span>💾 Median Size</span>
                <strong>{:.2f} MB</strong>
            </div>
        </div>
        """.format(
            stats['total_migrations'],
            estimator.format_time_estimate(stats['average_time']),
            stats['average_size'],
            estimator.format_time_estimate(stats['median_time']),
            stats['median_size']
        ), unsafe_allow_html=True)
    
    # Migration history
    st.markdown("""
    <div class="stats-card">
        <h3>📋 Migration History</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['migration_history']:
        # Get detailed history from estimator
        detailed_history = estimator.size_time_data
        
        for project in reversed(detailed_history):
            timestamp = format_timestamp(project.get('timestamp', ''))
            file_size = project.get('file_size_mb', 0)
            duration = project.get('duration_seconds', 0)
            
            st.markdown(f"""
            <div class="history-item">
                <div class="history-item-content">
                    <div class="history-item-header">
                        <strong>{project['project_name']}</strong>
                        <span class="history-timestamp">{timestamp}</span>
                    </div>
                    <div class="history-item-details">
                        <span>📦 {file_size:.2f} MB</span>
                        <span>⏱️ {estimator.format_time_estimate(duration)}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-history">
            <div class="empty-icon">📋</div>
            <p>No migrations yet</p>
            <span>Your migration history will appear here</span>
        </div>
        """, unsafe_allow_html=True)

# Current migration status
if st.session_state['current_migration']:
    migration = st.session_state['current_migration']
    show_migration_status(migration['name'], migration['status'])
    
    if migration['status'] == 'completed':
        duration = time.time() - migration['start_time']
        st.metric("⏱️ Migration Duration", f"{duration:.1f} seconds")

# Add toast notification function
def show_toast(message: str, type: str = "info"):
    """Show a toast notification"""
    st.markdown(f"""
    <div class="toast {type}">
        {message}
    </div>
    """, unsafe_allow_html=True)