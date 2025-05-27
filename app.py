import streamlit as st
import json
import time
import config
import api_helpers
import os
from PIL import Image
import random
import base64

# Set page configuration
st.set_page_config(
    page_title="WebMethods to SnapLogic Migration",
    page_icon="icon.webp",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit elements and ensure text visibility
st.markdown("""
    <style>
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Fix title and text visibility */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
        
        h1, h2, h3, .stMarkdown, .stText {
            color: #111827 !important;
            visibility: visible !important;
            display: block !important;
        }
        
        /* Style the main title */
        .title-container h1 {
            color: #1e293b !important;
            font-size: 30px !important;
            font-weight: 600 !important;
            margin-bottom: 8px !important;
            line-height: 1.2 !important;
            visibility: visible !important;
        }
        
        .title-container h2 {
            color: #64748b !important;
            font-size: 20px !important;
            font-weight: 400 !important;
            margin-top: 0 !important;
            visibility: visible !important;
        }
        
        /* Ensure upload section titles are visible */
        [data-testid="stFileUploader"] label {
            color: #374151 !important;
            visibility: visible !important;
        }
        
        /* Quick Guide text */
        .quick-guide {
            color: #6b7280 !important;
            font-size: 0.875rem !important;
            visibility: visible !important;
        }
        
        /* Ensure white background */
        .stApp {
            background: white;
        }
        
        /* Make all text elements explicitly visible */
        div[data-testid="stMarkdown"] > * {
            visibility: visible !important;
            color: inherit !important;
        }
        
        /* File uploader styling */
        [data-testid="stFileUploader"] section {
            padding: 1rem !important;
            border: 1px dashed #6366f1 !important;
            border-radius: 8px !important;
        }
        
        /* Make all file uploader text visible */
        [data-testid="stFileUploader"] span {
            color: #6b7280 !important;
            visibility: visible !important;
        }
        
        /* Make file size limit text visible */
        [data-testid="stFileUploader"] section div small {
            color: #6b7280 !important;
            visibility: visible !important;
            display: block !important;
            margin-top: 4px !important;
        }
        
        /* Make sure the limit text is visible */
        [data-testid="stFileUploader"] section div:first-child {
            color: #6b7280 !important;
            visibility: visible !important;
        }
        
        /* Ensure the "ZIP files only" text is visible */
        [data-testid="stFileUploader"] section div:first-child small {
            color: #6b7280 !important;
            visibility: visible !important;
            display: inline-block !important;
        }
        
        /* Style for uploaded files list */
        [data-testid="stFileUploader"] ul {
            list-style: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Style for each uploaded file */
        [data-testid="stFileUploader"] li {
            color: #1e40af !important;
            visibility: visible !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            padding: 0.5rem 0 !important;
        }
        
        /* File name and size text */
        [data-testid="stFileUploader"] li p {
            color: #1e40af !important;
            visibility: visible !important;
            margin: 0 !important;
        }
        
        /* File size text */
        [data-testid="stFileUploader"] li small {
            color: #6b7280 !important;
            visibility: visible !important;
        }
        
        /* Make sure the file info is always visible */
        .uploadedFile, .uploadedFileName {
            color: #1e40af !important;
            visibility: visible !important;
        }
        
        /* Ensure file size is visible */
        .uploadedFileInfo, .file-size {
            color: #6b7280 !important;
            visibility: visible !important;
        }
        
        /* Style the drag and drop text */
        .drag-text, .upload-text {
            color: #6b7280 !important;
            visibility: visible !important;
        }
        
        /* Make sure all text in the uploader is visible */
        [data-testid="stFileUploader"] * {
            visibility: visible !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if 'is_migrating' not in st.session_state:
    st.session_state.is_migrating = False
if 'migration_status' not in st.session_state:
    st.session_state.migration_status = 'not_started'

# Custom CSS for the app
st.markdown("""
<style>
    /* Layout and spacing */
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Header styling */
    .header-layout {
        display: flex;
        align-items: flex-start;
        gap: 0px;
        margin-bottom: 20px;
    }
    
    .logo-container {
        flex: 0 0 auto;
        padding-top: 5px;
        padding-right: 0;
    }
    
    .title-container {
        flex: 1;
        padding-left: 0;
        margin-left: 0;
    }
    
    .title-container h1 {
        color: #333;
        font-size: 34px;
        font-weight: 600;
        margin-bottom: 8px;
        line-height: 1.2;
        margin-left: 0;
        padding-left: 0;
    }
    
    .title-container h2 {
        color: #666;
        font-size: 22px;
        font-weight: 400;
        margin-top: 0;
        margin-left: 0;
        padding-left: 0;
    }
    
    /* Banner styling */
    .info-banner {
        background-color: #f0f6ff;
        border-left: 4px solid #6366f1;
        padding: 16px 20px;
        border-radius: 4px;
        margin: 20px 0 30px 0;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid #f0f0f0;
        transition: all 0.2s ease;
    }
    
    /* Clean card without border/shadow - for the empty state as in screenshot */
    .clean-card {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid #f0f0f0;
    }
    
    /* Card hover effect */
    .card:hover {
        box-shadow: 0 10px 15px rgba(0,0,0,0.05), 0 4px 6px rgba(0,0,0,0.05);
        border-color: #e6e6e6;
    }
    
    /* Custom file upload area */
    .file-upload-container {
        margin: 20px 0;
        border: 2px dashed #d1d5db;
        border-radius: 10px;
        padding: 30px 20px;
        text-align: center;
        background-color: #f9fafb;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .file-upload-container:hover {
        border-color: #6366f1;
        background-color: #f8fafc;
    }
    
    .upload-icon {
        font-size: 40px;
        color: #9ca3af;
        margin-bottom: 15px;
    }
    
    .drag-text {
        font-size: 18px;
        color: #4b5563;
        margin-bottom: 10px;
    }
    
    .file-info {
        font-size: 14px;
        color: #6b7280;
    }
    
    /* Animated file upload button */
    .file-upload-btn {
        background-color: #6366f1;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        margin-top: 15px;
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    .file-upload-btn:hover {
        background-color: #4f46e5;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* File drop highlight */
    .file-drop-active {
        border-color: #6366f1;
        background-color: #eef2ff;
    }
    
    /* Upload section */
    .upload-section {
        background-color: #f9fafb;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 2px dashed #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #6366f1;
        background-color: #f8fafc;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #6366f1;
        color: white;
        font-weight: 600;
        height: 3.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(99, 102, 241, 0.2);
        transition: all 0.3s ease;
        padding: 0 2rem;
        margin-top: 1rem;
        border: none;
    }
    
    .stButton button:hover {
        background-color: #4f46e5;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
        transform: translateY(-2px);
    }
    
    /* File detail card */
    .file-details-card {
        background-color: #f0f9ff;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        border-left: 3px solid #0ea5e9;
        transition: all 0.2s ease;
    }
    
    .file-details-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .file-name {
        font-weight: 600;
        color: #1e40af;
        margin-bottom: 5px;
    }
    
    .file-size {
        color: #6b7280;
        font-size: 14px;
    }
    
    .file-icon {
        margin-right: 10px;
        color: #3b82f6;
    }
    
    /* Progress styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        height: 8px !important;
        border-radius: 999px !important;
    }
    
    .stProgress {
        height: 10px;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        width: 100%;
        padding: 2rem;
        border: 2px dashed #d1d5db;
        border-radius: 10px;
        background-color: #f9fafb;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #6366f1;
        background-color: #f8fafc;
    }
    
    [data-testid="stFileUploader"] > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    
    /* Layout for the app */
    .app-container {
        display: flex;
        flex-direction: column;
        margin-top: 20px;
        padding: 0 20px;
    }
    
    /* Steps Container - Styled to Match Image */
    .steps-container {
        width: auto;
        display: flex;
        justify-content: space-around;
        padding: 20px 0;
        background-color: #f9fafb;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0 auto;
    }
    
    .content-area {
        width: 100%;
    }
    
    /* Step indicators - Circular with Gradient */
    .step-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 40px;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        padding: 10px 15px;
        transition: all 0.3s ease;
    }
    
    .step-number {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 8px;
        z-index: 1;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .step-text {
        font-size: 14px;
        color: #6b7280;
        font-weight: 400;
        text-align: center;
    }
    
    .step-active .step-number {
        transform: scale(1.1);
    }
    
    .step:not(:last-child):after {
        content: "";
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translateX(-50%);
        width: 2px;
        height: 20px;
        background-color: #e5e7eb;
    }
    
    .step-active:not(:last-child):after {
        background-color: #6366f1;
    }
    
    /* Tooltip and help text */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #6366f1;
        margin-left: 5px;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 14px;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Status and action buttons */
    .action-button {
        background-color: #6366f1;
        color: white;
        font-weight: 600;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        text-decoration: none;
        text-align: center;
    }
    
    .action-button:hover {
        background-color: #4f46e5;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .action-button-secondary {
        background-color: #f3f4f6;
        color: #4b5563;
        border: 1px solid #d1d5db;
    }
    
    .action-button-secondary:hover {
        background-color: #e5e7eb;
        color: #111827;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 14px;
        font-weight: 500;
    }
    
    .status-ready {
        background-color: #ecfdf5;
        color: #065f46;
    }
    
    .status-waiting {
        background-color: #fff7ed;
        color: #9a3412;
    }
    
    .status-error {
        background-color: #fef2f2;
        color: #b91c1c;
    }
    
    /* Add animation for processing states */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .processing-pulse {
        animation: pulse 1.5s infinite;
        padding: 15px;
        border-radius: 8px;
        background-color: #f0f6ff;
        margin-top: 20px;
        margin-bottom: 20px;
        border: 1px solid #e0e7ff;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid rgba(99, 102, 241, 0.3);
        border-radius: 50%;
        border-top-color: #6366f1;
        animation: spin 1s ease-in-out infinite;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .app-container {
            flex-direction: column;
        }
        
        .steps-container {
            padding: 10px;
        }
        
        .step-container {
            flex-direction: column;
            gap: 20px;
        }
        
        .step {
            padding: 10px;
        }
        
        .file-upload-container {
            padding: 20px 10px;
        }
    }
    
    /* Hide the default Streamlit file uploader */
    [data-testid="stFileUploader"] {
        display: none !important;
    }
    
    /* Enhanced File Uploader Styling */
    [data-testid="stFileUploader"] {
        width: 100%;
    }
    
    [data-testid="stFileUploader"] > section {
        padding: 2rem;
        border: 2px dashed #d1d5db;
        border-radius: 10px;
        background-color: #f9fafb;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        cursor: pointer;
    }
    
    [data-testid="stFileUploader"] > section:hover {
        border-color: #6366f1;
        background-color: #f8fafc;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.1);
    }
    
    [data-testid="stFileUploader"] > section::before {
        content: "📁";
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stFileUploader"] > section > button {
        background-color: #6366f1 !important;
        border-color: #6366f1 !important;
        color: white !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"] > section > button:hover {
        background-color: #4f46e5 !important;
        border-color: #4f46e5 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(79, 70, 229, 0.2);
    }
    
    /* Enhanced Card Styling */
    .card, .clean-card {
        background-color: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Enhanced Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.75rem 1.25rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        gap: 0.5rem;
    }
    
    .status-ready {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #34d399;
    }
    
    .status-waiting {
        background-color: #fff7ed;
        color: #9a3412;
        border: 1px solid #fb923c;
    }
    
    /* Enhanced Button Styling */
    .stButton > button {
        width: 100%;
        height: 3rem;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.025em;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.3);
        background: linear-gradient(135deg, #4f46e5, #4338ca);
    }
    
    /* Enhanced File Details Card */
    .file-details-card {
        background: linear-gradient(to right, #f0f9ff, #e0f2fe);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1.25rem 0;
        border-left: 4px solid #0ea5e9;
        transition: all 0.3s ease;
    }
    
    .file-details-card:hover {
        box-shadow: 0 4px 6px rgba(14, 165, 233, 0.1);
        transform: translateX(2px);
    }
    
    .file-name {
        font-weight: 600;
        color: #0c4a6e;
        font-size: 1.125rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .file-size {
        color: #64748b;
        font-size: 0.875rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Enhanced Header */
    .title-container h1 {
        background: linear-gradient(135deg, #1e293b, #334155);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    .title-container h2 {
        color: #64748b;
        font-size: 1.25rem;
        font-weight: 500;
    }
    
    /* Processing Card Animation */
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .processing-card {
        background: linear-gradient(-45deg, #f0f9ff, #e0f2fe, #dbeafe, #eff6ff);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    /* Processing Step Animation */
    .processing-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        border-radius: 8px;
        background-color: white;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .processing-step.active {
        border-left: 4px solid #6366f1;
        background-color: #fafafa;
        transform: translateX(5px);
    }
    
    /* Spinner Animation */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .spinner {
        width: 24px;
        height: 24px;
        border: 3px solid rgba(99, 102, 241, 0.1);
        border-radius: 50%;
        border-top-color: #6366f1;
        animation: spin 1s linear infinite;
    }
    
    /* Enhanced Results Card */
    .results-card {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(99, 102, 241, 0.1);
    }
    
    /* Success Animation */
    @keyframes success-circle {
        from { transform: scale(0); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    .success-icon {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #34d399, #10b981);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 32px;
        margin: 0 auto 1.5rem;
        animation: success-circle 0.5s ease-out;
    }
    
    /* Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border-top: 4px solid;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card.services { border-color: #6366f1; }
    .metric-card.flows { border-color: #8b5cf6; }
    .metric-card.success-rate { border-color: #06b6d4; }
    .metric-card.warnings { border-color: #fb923c; }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #1e293b, #334155);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Download Section */
    .download-section {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    .download-button {
        background: white !important;
        color: #1f2937 !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .download-button:hover {
        background: #f9fafb !important;
        border-color: #6366f1 !important;
        transform: translateY(-1px) !important;
    }

    /* Make file uploader more compact */
    [data-testid="stFileUploader"] {
        width: 100%;
        visibility: visible !important;
        display: block !important;
    }

    [data-testid="stFileUploader"] > section {
        min-height: 80px !important;     /* Further reduced from 120px */
        padding: 1rem 0.75rem !important;  /* Further reduced padding */
        border: 1px dashed #6366f1;      /* Thinner border */
        border-radius: 6px;              /* Smaller radius */
        background-color: #f8fafc;
        display: flex;
        flex-direction: row;             /* Changed to row for more compact layout */
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"] > section:hover {
        border-color: #4f46e5;
        background-color: #f0f7ff;
        box-shadow: 0 1px 3px rgba(99, 102, 241, 0.1);  /* Even smaller shadow */
    }

    [data-testid="stFileUploader"] > section::before {
        content: "📁";
        font-size: 1.5rem;              /* Further reduced from 2rem */
        margin-bottom: 0;
        margin-right: 0.5rem;
    }

    [data-testid="stFileUploader"] > section > div {
        font-size: 0.85rem;             /* Further reduced font size */
        color: #4b5563;
        text-align: center;
    }

    [data-testid="stFileUploader"] > section > button {
        margin: 0 0.5rem !important;    /* Adjusted margins */
        background-color: #6366f1 !important;
        color: white !important;
        padding: 0.35rem 0.75rem !important;  /* Smaller padding */
        border-radius: 4px !important;        /* Smaller radius */
        font-weight: 500 !important;          /* Slightly reduced weight */
        font-size: 0.8rem !important;         /* Smaller font */
        transition: all 0.3s ease !important;
        line-height: 1 !important;            /* Tighter line height */
    }

    [data-testid="stFileUploader"] > section > button:hover {
        background-color: #4f46e5 !important;
        transform: translateY(-1px);
        box-shadow: 0 1px 2px rgba(79, 70, 229, 0.2);
    }

    /* Even smaller help text */
    [data-testid="stFileUploader"] small {
        font-size: 0.75rem !important;
    }

    /* Hide some elements for compactness */
    [data-testid="stFileUploader"] > section > div > small {
        display: none !important;
    }

    /* Enhanced Upload Area Interactions */
    [data-testid="stFileUploader"] > section {
        position: relative;
        overflow: hidden;
    }

    [data-testid="stFileUploader"] > section::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 200%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(99, 102, 241, 0.1),
            transparent
        );
        transition: 0.5s;
        pointer-events: none;
    }

    [data-testid="stFileUploader"] > section:hover::after {
        left: 100%;
    }

    /* Progress Animation */
    @keyframes progress-pulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .processing-step {
        background: linear-gradient(
            90deg,
            #f0f7ff,
            #e0f2fe,
            #f0f7ff
        );
        background-size: 200% 100%;
        animation: progress-pulse 2s ease-in-out infinite;
    }

    /* Success Animation */
    @keyframes success-scale {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    .success-message {
        animation: success-scale 0.5s ease-out forwards;
    }

    /* Enhanced Button States */
    .stButton > button {
        position: relative;
        overflow: hidden;
    }

    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 60%);
        transform: translate(-50%, -50%) scale(0);
        opacity: 0;
        transition: 0.5s;
    }

    .stButton > button:hover::after {
        transform: translate(-50%, -50%) scale(1);
        opacity: 1;
    }

    /* Loading Indicator */
    .loading-spinner {
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #6366f1;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }

    /* Toast Notifications */
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 8px;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: toast-slide 0.3s ease-out forwards;
    }

    @keyframes toast-slide {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
</style>

<script>
    // Add drag and drop highlight functionality
    document.addEventListener('DOMContentLoaded', function() {
        const dropArea = document.querySelector('.file-upload-container');
        
        if (dropArea) {
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, unhighlight, false);
            });
            
            function highlight(e) {
                e.preventDefault();
                dropArea.classList.add('file-drop-active');
            }
            
            function unhighlight(e) {
                e.preventDefault();
                dropArea.classList.remove('file-drop-active');
            }
        }
    });
</script>
""", unsafe_allow_html=True)

def main():
    # Initialize session states
    if 'is_migrating' not in st.session_state:
        st.session_state.is_migrating = False
    if 'migration_status' not in st.session_state:
        st.session_state.migration_status = 'not_started'

    # Logo and title in the header
    col1, col2 = st.columns([1, 5])
    
    with col1:
        # Logo on the left
        try:
            logo = Image.open("logo.png")
            st.image(logo, width=150)
        except Exception as e:
            # Fallback to inline SVG if logo file is not found
            svg_code = """
            <svg width="150" height="70" viewBox="0 0 200 70">
                <rect x="20" y="15" width="40" height="40" fill="#E11D48"/>
                <text x="70" y="40" font-family="Arial" font-size="26" font-weight="bold" fill="#333">IW Connect</text>
            </svg>
            """
            st.markdown(svg_code, unsafe_allow_html=True)
    
    with col2:
        # Title and subtitle
        st.markdown("""
        <div class="title-container">
            <h1 style="font-size: 30px; margin-top: 10px;">Web Methods to SnapLogic</h1>
            <h2 style="font-size: 20px; margin-top: 0px;">Migration Accelerator</h2>
        </div>
        """, unsafe_allow_html=True)

    # Initialize step tracking
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    # Create app container
    st.markdown('<div class="app-container">', unsafe_allow_html=True)
    
    # Main content area
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    
    # File upload section first - BEFORE we use the variable
    st.subheader("📤 Upload your Web Methods package")
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <h3 style="font-size: 1rem; color: #374151; margin: 0;">📤 Upload Package</h3>
            <div style="background: #e0f2fe; color: #0369a1; font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 9999px;">
                ZIP files only
            </div>
        </div>
    </div>
    
    <style>
        /* Modern file uploader styling */
        [data-testid="stFileUploader"] {
            width: 100%;
            visibility: visible !important;
            display: block !important;
        }

        [data-testid="stFileUploader"] > section {
            min-height: 80px !important;
            padding: 1rem !important;
            border: 1px dashed #6366f1;
            border-radius: 8px;
            background-color: #f8fafc;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        [data-testid="stFileUploader"] > section:hover {
            border-color: #4f46e5;
            background-color: #f0f7ff;
            box-shadow: 0 1px 3px rgba(99, 102, 241, 0.1);
        }

        /* File details card styling */
        .file-info-card {
            background: linear-gradient(to right, #f0f9ff, #e0f2fe);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid #e0f2fe;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .file-info-card .file-details {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .file-info-card .file-icon {
            color: #3b82f6;
            font-size: 1.25rem;
        }

        .file-info-card .file-name {
            color: #1e40af;
            font-weight: 500;
        }

        .file-info-card .file-size {
            color: #64748b;
            font-size: 0.875rem;
        }

        .file-info-card .status-badge {
            background: #ecfdf5;
            color: #065f46;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        /* Start Migration button styling */
        .migration-button {
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.1);
        }

        .migration-button:hover {
            background: linear-gradient(135deg, #4f46e5, #4338ca);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
        }

        .ready-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #6b7280;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }

        .ready-indicator .dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize file uploader with explicit size limit text
    uploaded_file = st.file_uploader(
        "Drop ZIP file here",
        type="zip",
        help="Maximum size: 200MB • ZIP files only",
        key="file_uploader",
        label_visibility="visible"
    )

    # Initialize start_button variable
    start_button = False

    # Show file details if uploaded
    if uploaded_file:
        size_kb = uploaded_file.size / 1024
        size_text = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        
        st.markdown(f"""
        <div style="
            background: #f8fafc;
            border-radius: 6px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <span style="color: #6b7280;">📄</span>
                <div>
                    <div style="
                        color: #1e40af;
                        font-weight: 500;
                        font-size: 0.875rem;
                    ">{uploaded_file.name}</div>
                    <div style="
                        color: #6b7280;
                        font-size: 0.75rem;
                    ">Size: {size_text}</div>
                </div>
            </div>
            <div style="
                background: #ecfdf5;
                color: #065f46;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 500;
            ">Ready ✓</div>
        </div>
        """, unsafe_allow_html=True)
    
        # Start Migration button container
        button_container = st.empty()
        status_text_container = st.empty()
        
        # Show appropriate button based on migration state
        if not st.session_state.is_migrating:
            with button_container:
                start_button = st.button(
                    "⚡ START MIGRATION",
                    key="start_migration",
                    help="Begin the migration process",
                    use_container_width=True
                )
            with status_text_container:
                st.markdown("""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    color: #9ca3af;
                    font-size: 0.875rem;
                    margin-top: 0.5rem;
                ">
                    <div style="
                        width: 6px;
                        height: 6px;
                        background-color: #10b981;
                        border-radius: 50%;
                    "></div>
                    Ready to start the migration process
                </div>
                """, unsafe_allow_html=True)
        elif st.session_state.migration_status == 'not_started':
            with button_container:
                stop_button = st.button(
                    "⬛ STOP MIGRATION",
                    key="stop_migration",
                    help="Stop the migration process",
                    type="secondary",
                    use_container_width=True
                )
                if stop_button:
                    st.session_state.is_migrating = False
                    st.rerun()
            with status_text_container:
                st.markdown("""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    color: #9ca3af;
                    font-size: 0.875rem;
                    margin-top: 0.5rem;
                ">
                    <div style="
                        width: 6px;
                        height: 6px;
                        border: 2px solid #3b82f6;
                        border-top-color: transparent;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    "></div>
                    Migration in progress...
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: #f8fafc; border-radius: 6px; padding: 0.75rem; margin: 0.5rem 0;">
            <div style="color: #6b7280; font-size: 0.75rem; margin-bottom: 0.5rem;">Quick Guide:</div>
            <div style="display: flex; align-items: center; gap: 1rem; font-size: 0.75rem; color: #4b5563;">
                <div>1. 📋 Prepare ZIP file</div>
                <div>2. 📥 Drop or browse</div>
                <div>3. ✨ Start migration</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close card
    
    # Results section - only shown when processing is complete
    if start_button:
        # Set migration as started
        st.session_state.is_migrating = True
        st.rerun()

    if st.session_state.is_migrating:
        # Validate the uploaded file
        is_valid, error_message = api_helpers.validate_file(uploaded_file)
        
        if not is_valid:
            st.session_state.is_migrating = False
            st.markdown(f"""
            <div class="card">
                <div class="status-badge status-error">
                    ❌ Validation Error
                </div>
                <p style="margin-top: 15px; color: #b91c1c;">{error_message}</p>
                <button class="action-button action-button-secondary" onclick="window.location.reload()">
                    Try Again
                </button>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Create a card for the processing section
            processing_header = st.empty()
            processing_header.subheader("Processing Migration")
            
            # Create single progress bar and time container
            progress_bar = st.progress(0)
            time_container = st.empty()
            status_container = st.empty()
            
            # Prepare the data for API
            migration_options = {
                "include_documentation": True,
                "generate_mappings": True,
                "convert_transformations": True,
                "analyze_dependencies": True
            }
            
            # Define the processing steps with their progress percentages
            detailed_steps = [
                (5, "Validating package structure..."),
                (10, "Establishing secure connection to SnapLogic..."),
                (15, "Extracting Web Methods components..."),
                (25, "Processing service definitions..."),
                (35, "Mapping data structures..."),
                (45, "Processing flow logic..."),
                (55, "Creating pipeline structure..."),
                (65, "Processing business rules..."),
                (75, "Validating transformed components..."),
                (85, "Creating component mappings..."),
                (95, "Finalizing conversion...")
            ]
            
            try:
                # Start time
                start_time = time.time()
                
                # Process each step
                for progress, message in detailed_steps:
                    # Update progress
                    progress_bar.progress(progress)
                    
                    # Calculate elapsed time
                    elapsed_time = int(time.time() - start_time)
                    
                    # Update status with animation
                    status_container.markdown(f"""
                    <div style="padding: 1rem; border-radius: 8px; background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(8px); border: 1px solid rgba(59, 130, 246, 0.1);">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="position: relative; width: 24px; height: 24px;">
                                <style>
                                    @keyframes spin {{
                                        0%% {{ transform: rotate(0deg); }}
                                        100%% {{ transform: rotate(360deg); }}
                                    }}
                                    @keyframes pulse {{
                                        0%%, 100%% {{ opacity: 1; }}
                                        50%% {{ opacity: 0.5; }}
                                    }}
                                </style>
                                <div style="
                                    position: absolute;
                                    width: 24px;
                                    height: 24px;
                                    border: 3px solid #e0e7ff;
                                    border-top: 3px solid #6366f1;
                                    border-radius: 50%%;
                                    animation: spin 1s linear infinite;
                                "></div>
                            </div>
                            <div style="flex-grow: 1;">
                                <div style="
                                    color: #1e40af;
                                    font-weight: 500;
                                    margin-bottom: 0.25rem;
                                    animation: pulse 2s ease-in-out infinite;
                                ">{message}</div>
                                <div class="progress-details" style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="color: #3b82f6; font-size: 0.875rem;">Progress: {progress}%</div>
                                    <div style="
                                        background: rgba(255, 255, 255, 0.8);
                                        color: #3b82f6;
                                        padding: 0.25rem 0.75rem;
                                        border-radius: 9999px;
                                        font-size: 0.75rem;
                                        font-weight: 500;
                                        backdrop-filter: blur(4px);
                                    ">Migration in Progress</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Update time display
                    time_container.markdown(f"""
                    <div style="
                        text-align: right;
                        color: #3b82f6;
                        font-size: 0.875rem;
                        animation: pulse 2s ease-in-out infinite;
                    ">
                        Time elapsed: {elapsed_time // 60}m {elapsed_time % 60}s
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Simulate processing time (adjust as needed)
                    time.sleep(0.5)
                
                # Show completion with success animation
                progress_bar.progress(100)
                status_container.markdown("""
                <div style="padding: 1.5rem; border-radius: 8px; background: #f0f7ff; border-left: 3px solid #3b82f6;">
                    <style>
                        @keyframes slideIn {
                            from { transform: translateX(-10px); opacity: 0; }
                            to { transform: translateX(0); opacity: 1; }
                        }
                        @keyframes pulse {
                            0% { transform: scale(1); }
                            50% { transform: scale(1.05); }
                            100% { transform: scale(1); }
                        }
                        @keyframes dots {
                            0%, 20% { content: ""; }
                            40% { content: "."; }
                            60% { content: ".."; }
                            80%, 100% { content: "..."; }
                        }
                        .loading-dots::after {
                            content: "";
                            animation: dots 1.5s infinite;
                        }
                    </style>
                    <div style="display: flex; align-items: center; gap: 1rem; animation: slideIn 0.5s ease-out;">
                        <div style="
                            background: #60a5fa;
                            border-radius: 50%;
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            animation: pulse 2s ease-in-out infinite;
                        ">
                            <div style="
                                width: 16px;
                                height: 16px;
                                border: 3px solid #ffffff;
                                border-top-color: transparent;
                                border-radius: 50%;
                                animation: spin 1s linear infinite;
                            "></div>
                        </div>
                        <div>
                            <div style="
                                color: #1e40af;
                                font-weight: 500;
                                font-size: 1.125rem;
                                margin-bottom: 0.25rem;
                                display: flex;
                                align-items: center;
                            ">
                                Migration in Progress<span class="loading-dots"></span>
                            </div>
                            <div style="
                                color: #3b82f6;
                                font-size: 0.875rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            ">
                                <span>Transferring components to SnapLogic</span>
                                <div style="
                                    width: 12px;
                                    height: 12px;
                                    border: 2px solid #3b82f6;
                                    border-top-color: transparent;
                                    border-radius: 50%;
                                    animation: spin 1s linear infinite;
                                "></div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Start the API call and handle response
                result = api_helpers.send_to_api(uploaded_file, migration_options)
                
                # Handle the API response
                if result.get("success"):
                    # Reset migration status and set completion flag
                    st.session_state.is_migrating = False
                    st.session_state.migration_status = 'completed'
                    
                    # Clear all progress and status elements
                    progress_bar.empty()
                    processing_header.empty()
                    time_container.empty()
                    status_container.empty()
                    button_container.empty()
                    status_text_container.empty()
                    
                    # Show success message in a new container
                    st.markdown("""
                    <div style="margin-top: 2rem;">
                        <div style="background: #ecfdf5; border: 1px solid #10b981; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem;">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div style="background: #34d399; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                                    <span style="color: white; font-size: 24px;">✓</span>
                                </div>
                                <div>
                                    <h3 style="color: #065f46; margin: 0; font-size: 1.25rem;">Migration Successful!</h3>
                                    <p style="color: #047857; margin: 0.5rem 0 0 0; font-size: 0.875rem;">
                                        Your Web Methods package has been successfully migrated to SnapLogic.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Update the button to allow new migration
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button(
                            "🔄 MIGRATE ANOTHER",
                            key="migrate_another",
                            use_container_width=True
                        ):
                            # Reset all states to start fresh
                            st.session_state.is_migrating = False
                            st.session_state.migration_status = 'not_started'
                            st.rerun()
                    with col2:
                        st.markdown("""
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            color: #047857;
                            font-size: 0.875rem;
                            margin-top: 0.5rem;
                        ">
                            <div style="
                                width: 6px;
                                height: 6px;
                                background-color: #34d399;
                                border-radius: 50%;
                            "></div>
                            Ready to start another migration
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Reset migration status and set completion flag
                    st.session_state.is_migrating = False
                    st.session_state.migration_status = 'failed'
                    
                    # Clear all progress and status elements
                    progress_bar.empty()
                    processing_header.empty()
                    time_container.empty()
                    status_container.empty()
                    button_container.empty()
                    status_text_container.empty()
                    
                    # Show error message if the API call was not successful
                    error_message = result.get("error", "An unknown error occurred")
                    st.markdown(f"""
                    <div style="margin-top: 2rem;">
                        <div style="background: #fef2f2; border: 1px solid #ef4444; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem;">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div style="background: #ef4444; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                                    <span style="color: white; font-size: 24px;">×</span>
                                </div>
                                <div>
                                    <h3 style="color: #991b1b; margin: 0; font-size: 1.25rem;">Migration Failed</h3>
                                    <p style="color: #b91c1c; margin: 0.5rem 0 0 0; font-size: 0.875rem;">
                                        {error_message}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Update the button status to show error without animation
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.button(
                            "× FAILED",
                            key="failed_button",
                            disabled=True,
                            use_container_width=True
                        )
                    with col2:
                        st.markdown("""
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                            color: #991b1b;
                            font-size: 0.875rem;
                            margin-top: 0.5rem;
                        ">
                            <div style="
                                width: 6px;
                                height: 6px;
                                background-color: #ef4444;
                                border-radius: 50%;
                            "></div>
                            Migration failed. Please try again.
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                # Reset migration status on error
                st.session_state.is_migrating = False
                st.error(f"An error occurred: {str(e)}")
                st.button("Try Again", on_click=lambda: st.session_state.clear())
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close processing card
    
    st.markdown('</div>', unsafe_allow_html=True)  # close content area
    
    st.markdown('</div>', unsafe_allow_html=True)  # close app container
    
    # A sleeker footer
    st.markdown("""
    <div style="text-align: center; padding-top: 20px; margin-top: 30px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.9rem;">
        © 2023 IW Connect • Web Methods to SnapLogic Migration Accelerator • v1.0
    </div>
    """, unsafe_allow_html=True)

def estimate_remaining_time(progress, elapsed_time):
    if progress > 0:
        total_estimated = (elapsed_time / progress) * 100
        remaining = total_estimated - elapsed_time
        return f"Estimated time remaining: {int(remaining)}s"
    return "Calculating..."

def send_to_api_with_retry(uploaded_file, migration_options, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = api_helpers.send_to_api(uploaded_file, migration_options)
            if result.get("success"):
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    return {"success": False, "error": "Maximum retries reached"}

# Cache API responses
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_api_response(file_hash):
    return cached_responses.get(file_hash)

if __name__ == "__main__":
    main() 
