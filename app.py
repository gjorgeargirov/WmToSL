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

# Set page config with dark theme
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

# Apply dark theme
st.markdown("""
    <style>
        /* Force dark theme */
        [data-testid="stAppViewContainer"] {
            background-color: #0e1117;
        }
        
        [data-testid="stSidebar"] {
            background-color: #0e1117;
        }
        
        [data-testid="stHeader"] {
            background-color: #0e1117;
        }
        
        .stMarkdown {
            color: #fafafa !important;
        }
        
        /* Hide default elements */
        [data-testid="collapsedControl"] {
            display: none;
        }
        #MainMenu {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }

        /* Base styles with dark theme */
        .main-header {
            background: linear-gradient(90deg, #1E88E5 0%, #1976D2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
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
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 1rem !important;
            line-height: 1.4 !important;
            margin-top: 1rem;
            margin-bottom: 0;
        }

        /* Dark theme styles */
        .steps-container {
            background: #1e1e2f;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            transition: all 0.3s ease;
            width: 100%;
            box-sizing: border-box;
            border: 1px solid #2d2d44;
            color: #fafafa !important;
        }
        .stats-card {
            background: #1e1e2f;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            margin-bottom: 1rem;
            border: 1px solid #2d2d44;
            transition: all 0.3s ease;
            width: 100%;
            box-sizing: border-box;
            color: #fafafa !important;
        }
        .upload-section {
            background: #1e1e2f;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            border: 2px dashed #1E88E5;
            text-align: center;
            margin-bottom: 2rem;
            transition: all 0.3s ease;
            width: 100%;
            box-sizing: border-box;
            color: #fafafa !important;
        }

        /* Step items styling */
        .step-item {
            display: flex;
            align-items: center;
            margin: 0.5rem 0;
            padding: 0.8rem;
            border-radius: 6px;
            background: #1e1e2f;
            border: 1px solid #2d2d44;
            transition: all 0.2s ease;
            color: #fafafa !important;
        }
        .step-item:hover {
            background: #2a2a3d;
            transform: translateX(5px);
        }
        .step-number {
            background: #1E88E5;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-size: 0.9rem;
            font-weight: bold;
        }

        /* History items styling */
        .history-item {
            background: #1e1e2f;
            border: 1px solid #2d2d44;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            transition: all 0.2s ease;
            color: #fafafa !important;
        }
        .history-item:hover {
            background: #2a2a3d;
            transform: translateX(5px);
        }
        .history-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
            color: #fafafa !important;
        }
        .history-timestamp {
            color: #fafafa !important;
            opacity: 0.7;
            font-size: 0.9rem;
        }
        .history-item-details {
            display: flex;
            gap: 1rem;
            font-size: 0.9rem;
            color: #fafafa !important;
            opacity: 0.9;
        }

        /* Empty state styling */
        .empty-history {
            text-align: center;
            padding: 2rem;
            color: #fafafa !important;
            opacity: 0.7;
        }
        .empty-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
        }

        /* Toast notifications */
        .toast {
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            padding: 1rem 2rem;
            border-radius: 6px;
            background: #1e1e2f;
            border: 1px solid #2d2d44;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            color: #fafafa !important;
        }

        /* Info message styling */
        .info-message {
            background: #1e1e2f !important;
            border: 1px solid #2d2d44 !important;
            color: #fafafa !important;
        }
        .info-message h4 {
            color: #1E88E5 !important;
        }

        /* Streamlit element overrides */
        .stButton button {
            width: 100%;
            background: #1E88E5 !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        
        /* File uploader styling */
        div[data-testid="stFileUploader"] {
            width: 100%;
        }

        /* Upload box background */
        div[data-testid="stFileUploader"] > section {
            background-color: #1e1e2f !important;
            border: 2px dashed #1E88E5 !important;
            border-radius: 10px !important;
            padding: 2rem !important;
        }

        /* Main upload text */
        div[data-testid="stFileUploader"] p {
            color: #fafafa !important;
            font-size: 1.1rem !important;
            font-weight: 500 !important;
        }

        /* File size limit text */
        div[data-testid="stFileUploader"] small {
            color: rgba(250, 250, 250, 0.7) !important;
        }

        /* Browse files button */
        div[data-testid="stFileUploader"] button {
            background-color: #1E88E5 !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            margin-top: 1rem !important;
        }

        /* Ensure text is visible in all states */
        div[data-testid="stFileUploader"] * {
            color: #fafafa !important;
        }

        /* Override Streamlit's default styles */
        .css-1aehpvj, .css-16idsys, .css-1vbkxwb {
            color: #fafafa !important;
        }

        /* Fix any dynamic class text colors */
        [class*="css"] {
            color: #fafafa !important;
        }

        /* Specific fix for the drag and drop text */
        div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] p {
            color: #fafafa !important;
        }

        /* Fix for the file size text */
        div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] div {
            color: rgba(250, 250, 250, 0.7) !important;
        }

        /* Ensure the upload icon is visible */
        div[data-testid="stFileUploader"] svg {
            color: #1E88E5 !important;
        }

        /* Style for drag over state */
        div[data-testid="stFileUploader"]:focus-within section {
            border-color: #64B5F6 !important;
            background-color: #2a2a3d !important;
        }

        /* Fix for any nested text elements */
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] label,
        div[data-testid="stFileUploader"] div {
            color: #fafafa !important;
        }

        /* Specific override for the upload text */
        .upload-text {
            color: #fafafa !important;
            font-weight: 500 !important;
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
        
        /* Ensure proper spacing */
        [data-testid="stExpander"] {
            margin-bottom: 1rem !important;
        }
        
        .stats-card {
            margin-top: 1rem !important;
        }
        
        /* Animations */
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

        [data-testid="stFileUploader"] label {
            font-size: 1.1rem !important;
            color: #fafafa !important;
            font-weight: 500 !important;
        }
        [data-testid="stFileUploader"] small {
            color: rgba(250, 250, 250, 0.7) !important;
        }
        [data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] {
            color: #fafafa !important;
        }

        /* File Details Section Styling */
        .file-details {
            background: #1e1e2f !important;
            border-radius: 10px !important;
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
            border: 1px solid #2d2d44 !important;
        }

        /* File Details Header */
        .file-details h3 {
            color: #fafafa !important;
            font-size: 1.2rem !important;
            margin-bottom: 1rem !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }

        /* File Name Styling */
        .file-name {
            color: #fafafa !important;
            font-size: 1.1rem !important;
            margin-bottom: 1rem !important;
            font-weight: 500 !important;
        }

        /* File Properties */
        .file-property {
            color: #fafafa !important;
            margin: 0.5rem 0 !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }

        .file-property-label {
            color: rgba(250, 250, 250, 0.7) !important;
            font-weight: 500 !important;
        }

        .file-property-value {
            color: #fafafa !important;
        }

        /* Migration Time Estimate Section */
        .estimate-section {
            background: #1e1e2f !important;
            border-radius: 10px !important;
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
            border: 1px solid #2d2d44 !important;
        }

        .estimate-header {
            color: #1E88E5 !important;
            font-size: 1.2rem !important;
            margin-bottom: 1rem !important;
            font-weight: 500 !important;
        }

        .estimate-detail {
            color: #fafafa !important;
            margin: 0.5rem 0 !important;
        }

        .estimate-label {
            color: rgba(250, 250, 250, 0.7) !important;
            font-weight: 500 !important;
        }

        .estimate-value {
            color: #fafafa !important;
        }

        .estimate-note {
            color: rgba(250, 250, 250, 0.6) !important;
            font-style: italic !important;
            margin-top: 1rem !important;
            font-size: 0.9rem !important;
        }

        /* Override Streamlit's default text colors in file details */
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div {
            color: #fafafa !important;
        }

        /* Style for file size and other metadata */
        .file-metadata {
            color: rgba(250, 250, 250, 0.7) !important;
            font-size: 0.9rem !important;
        }

        /* Ensure all text in the details section is visible */
        div[data-testid="stFileUploader"] ~ div * {
            color: #fafafa !important;
        }

        /* Settings Box Styling */
        [data-testid="stExpander"] {
            background-color: #1e1e2f !important;
            border: 1px solid #2d2d44 !important;
            border-radius: 10px !important;
            margin-bottom: 1rem !important;
        }

        /* Settings Header */
        [data-testid="stExpander"] details summary {
            padding: 1rem !important;
            background-color: #1e1e2f !important;
            border-radius: 10px !important;
            color: #fafafa !important;
            font-weight: 500 !important;
            font-size: 1.1rem !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }

        /* Settings Content */
        [data-testid="stExpander"] details div[data-testid="stExpanderContent"] {
            background-color: #1e1e2f !important;
            border-top: 1px solid #2d2d44 !important;
            padding: 1rem !important;
            color: #fafafa !important;
        }

        /* Settings Icon */
        [data-testid="stExpander"] svg {
            color: #1E88E5 !important;
        }

        /* Settings Text */
        [data-testid="stExpander"] p,
        [data-testid="stExpander"] span,
        [data-testid="stExpander"] div {
            color: #fafafa !important;
        }

        /* Settings Hover Effect */
        [data-testid="stExpander"] details summary:hover {
            background-color: #2a2a3d !important;
            cursor: pointer;
        }

        /* Settings Arrow Icon */
        [data-testid="stExpander"] details summary::-webkit-details-marker,
        [data-testid="stExpander"] details summary::marker {
            color: #1E88E5 !important;
        }

        /* No Settings Message */
        [data-testid="stExpander"] .no-settings {
            color: rgba(250, 250, 250, 0.7) !important;
            font-style: italic !important;
            text-align: center !important;
            padding: 1rem !important;
        }

        /* Settings Divider */
        [data-testid="stExpander"] hr {
            border-color: #2d2d44 !important;
            margin: 1rem 0 !important;
        }

        /* Make sure the expander text is visible */
        .streamlit-expanderHeader {
            color: #fafafa !important;
            background-color: #1e1e2f !important;
            font-weight: 500 !important;
        }

        /* Override any Streamlit default colors */
        div[class*="stMarkdown"] > div[data-testid="stExpanderContent"] p {
            color: #fafafa !important;
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
if 'upload_key' not in st.session_state:
    st.session_state['upload_key'] = 0

def reset_upload():
    """Reset the file uploader by incrementing the key"""
    st.session_state['upload_key'] += 1

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
        label="Upload your webMethods project ZIP file",
        type="zip",
        key=f"project_uploader_{st.session_state['upload_key']}",
        help="Upload a ZIP file containing your webMethods project artifacts.",
        on_change=None
    )
    
    # Show file preview and time estimate if a file is uploaded
    if uploaded_file is not None:
        # File Details Section
        st.markdown("""
            <div class="file-details">
                <h3>📁 File Details</h3>
                <div class="file-name">{}</div>
                <div class="file-property">
                    <span class="file-property-label">Size:</span>
                    <span class="file-property-value">{:.2f} MB</span>
                </div>
            </div>
        """.format(
            uploaded_file.name,
            uploaded_file.size / (1024 * 1024)
        ), unsafe_allow_html=True)
        
        # Calculate and show time estimate
        file_size_mb = uploaded_file.size / (1024 * 1024)
        estimated_time, estimate_details = estimator.estimate_migration_time(file_size_mb)
        
        # Show time estimate with confidence level
        st.markdown("""
            <div class="estimate-section">
                <div class="estimate-header">⏱️ Migration Time Estimate</div>
                <div class="estimate-detail">
                    <span class="estimate-label">Estimated Duration:</span>
                    <span class="estimate-value">{}</span>
                </div>
                <div class="estimate-detail">
                    <span class="estimate-label">Confidence Level:</span>
                    <span class="estimate-value">{}</span>
                </div>
                <div class="estimate-detail">
                    <span class="estimate-label">File Size:</span>
                    <span class="estimate-value">{:.2f} MB</span>
                </div>
                <div class="estimate-detail">
                    <span class="estimate-label">Complexity:</span>
                    <span class="estimate-value">{}</span>
                </div>
                <div class="estimate-note">{}</div>
                {}
                {}
            </div>
        """.format(
            estimator.format_time_estimate(estimated_time),
            estimate_details['confidence'].title(),
            file_size_mb,
            estimate_details['complexity'].title(),
            estimate_details['explanation'],
            f'<div class="estimate-note">Note: {estimate_details["note"]}</div>' if 'note' in estimate_details else '',
            f'<div class="estimate-detail"><span class="estimate-label">Similar Files Range:</span> <span class="estimate-value">{estimate_details["similar_sizes_range"]}</span></div>' if 'similar_sizes_range' in estimate_details else ''
        ), unsafe_allow_html=True)
        
        # Add clear button with proper styling
        if st.button("Clear File", key="clear_file", help="Click to remove the current file"):
            reset_upload()
            st.rerun()
        
        # Migrate button with proper styling
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
    # Settings expander (removed dark mode toggle)
    with st.expander("⚙️ Settings", expanded=False):
        st.markdown("No settings available")

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