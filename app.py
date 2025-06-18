"""
DataLoom - Professional Analytics Dashboard
Production-ready Streamlit application with secure authentication and database integration.
"""
import streamlit as st
import pandas as pd
from database import DatabaseManager
from data_analyzer import DataAnalyzer
import plotly.express as px
import os
from datetime import datetime
import base64

def get_favicon_base64():
    try:
        with open("assets/favicon.ico", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

def get_favicon_data_url():
    favicon_b64 = get_favicon_base64()
    if favicon_b64:
        return f"data:image/x-icon;base64,{favicon_b64}"
    else:
        return "https://cdn-icons-png.flaticon.com/512/2103/2103665.png"

st.set_page_config(
    page_title="DataLoom - Analytics Dashboard",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

if not st.session_state.authenticated:
    pass
else:
    pass

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: #ffffff;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;
    }
    
    .logo-icon {
        width: 32px;
        height: 32px;
        filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.3));
    }
    
    .logo-container h1 {
        font-size: 1.5rem !important;
        margin: 0 !important;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .metric-card h2 {
        color: #ffffff;
        margin: 0;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 0.8rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    @media screen and (max-width: 768px) {
        .main-header {
            padding: 1rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .logo-container {
            gap: 0.3rem;
        }
        
        .logo-icon {
            width: 28px;
            height: 28px;
        }
        
        .logo-container h1 {
            font-size: 1.2rem !important;
        }
        
        .metric-card {
            padding: 0.8rem;
            margin-bottom: 0.8rem;
        }
        
        .metric-card h2 {
            font-size: 1.3rem;
        }
        
        .upload-section {
            padding: 0.8rem;
        }
        
        .insight-card {
            padding: 0.6rem;
        }
        
        .stSelectbox > div > div {
            min-height: 2.5rem;
        }
        
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        .stColumns > div {
            padding: 0 0.25rem;
        }
        
        .stForm {
            display: flex;
            flex-direction: column;
        }
        
        .stForm > div {
            margin-bottom: 0.8rem;
        }
        
        .stForm button[kind="formSubmit"] {
            width: 100% !important;
            margin-top: 1rem !important;
            order: 999;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding: 1rem 0 !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        .main-header {
            padding: 0.8rem 0.3rem;
        }
        
        .logo-container h1 {
            font-size: 1rem !important;
        }
        
        .logo-icon {
            width: 24px;
            height: 24px;
        }
        
        .metric-card h2 {
            font-size: 1.1rem;
        }
        
        .metric-card h3 {
            font-size: 0.8rem;
        }
        
        .upload-section {
            padding: 0.6rem;
        }
        
        .stButton > button {
            font-size: 0.9rem;
            padding: 0.5rem;
        }
        
        .stForm button[kind="formSubmit"] {
            font-size: 1rem !important;
            padding: 0.75rem !important;
            margin-top: 1.5rem !important;
            border-radius: 8px !important;
        }
        
        .stTextInput > div > div > input {
            font-size: 1rem;
            padding: 0.75rem;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
        }
    }
    
    .stMarkdown, .stText {
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .stForm {
        background: rgba(45, 45, 68, 0.3);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
    }
    
    .stForm button[kind="formSubmit"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stForm button[kind="formSubmit"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(61, 61, 92, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
    }
    
    @media screen and (max-width: 768px) {
        .css-1d391kg {
            padding: 1rem 0.5rem;
        }
        
        .stForm {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
    
    .sidebar .stSelectbox > div > div {
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        color: white;
    }
    
    /* Enhanced drag and drop styling */
    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #3d3d5c 0%, #4d4d6c 100%);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    .stFileUploader > div {
        color: white !important;
        text-align: center;
    }
    
    .stFileUploader section {
        border: none !important;
        background: transparent !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed #667eea !important;
        border-radius: 15px !important;
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%) !important;
        color: white !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #4CAF50 !important;
        background: linear-gradient(135deg, #3d3d5c 0%, #4d4d6c 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
        color: white !important;
        font-size: 1.1rem !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

def show_login_page():
    st.markdown(f"""
    <div class="main-header">
        <div class="logo-container">
            <img src="{get_favicon_data_url()}" class="logo-icon" alt="DataLoom Logo">
            <div style="margin: 0; font-size: 2.5rem; font-weight: 600; color: inherit;">DataLoom</div>
        </div>
        <p>Professional Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login Below", anchor=False)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)
            
            if login_btn:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please check your credentials or create an account first.")
    
    with tab2:
        st.subheader("Create your account", anchor=False)
        
        if st.session_state.get('signup_success', False):
            st.success("✅ Account created successfully! You can now login with your credentials.")
            st.info("Please switch to the Login tab to access your account")
            del st.session_state.signup_success
            for key in ['signup_username', 'signup_email', 'signup_password', 'signup_confirm']:
                if key in st.session_state:
                    del st.session_state[key]
        
        with st.expander("Account Requirements", expanded=False):
            st.markdown("""
            **Username:**
            - 3-20 characters long
            - Letters, numbers, hyphens (-), and underscores (_) only
            
            **Email:**
            - Valid email format (e.g., user@domain.com)
            - Will be used for account recovery
            
            **Password:**
            - Minimum 8 characters
            - Must contain at least one letter and one number
            - Both password fields must match
            """)
        
        with st.form("signup_form"):
            new_username = st.text_input("Username", 
                                       help="Choose a unique username (3-20 characters)",
                                       key="signup_username")
            new_email = st.text_input("Email Address", 
                                    placeholder="example@domain.com",
                                    key="signup_email")
            new_password = st.text_input("Password", 
                                       type="password", 
                                       help="Minimum 8 characters",
                                       key="signup_password")
            confirm_password = st.text_input("Confirm Password", 
                                           type="password",
                                           key="signup_confirm")
            signup_btn = st.form_submit_button("Create Account", use_container_width=True)
            
            if signup_btn:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                username_pattern = r'^[a-zA-Z0-9_-]{3,20}$'
                
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("⚠️ Please fill in all fields")
                elif not re.match(username_pattern, new_username):
                    st.error("❌ Username must be 3-20 characters long and contain only letters, numbers, hyphens, and underscores")
                elif not re.match(email_pattern, new_email):
                    st.error("❌ Please enter a valid email address (example: user@domain.com)")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters long")
                elif not re.search(r'[A-Za-z]', new_password) or not re.search(r'[0-9]', new_password):
                    st.error("❌ Password must contain at least one letter and one number")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match. Please check both password fields")
                else:
                    if db.create_user(new_username, new_email, new_password):
                        st.session_state.signup_success = True
                        st.rerun()
                    else:
                        st.error("❌ Username or email already exists. Please try different credentials.")

def show_dashboard():
    user = st.session_state.user
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class="main-header">
            <div class="logo-container">
                <img src="{get_favicon_data_url()}" class="logo-icon" alt="DataLoom Logo">
                <h1 style="margin: 0;">DataLoom Analytics</h1>
            </div>
            <p>Welcome back, {user['username']}!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <img src="{get_favicon_data_url()}" style="width: 32px; height: 32px; filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.3));">
            <h2 style="margin: 0.5rem 0; color: #667eea;">DataLoom</h2>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "Upload Data", "Analytics", "Settings"],
            index=0
        )
        
        st.markdown("---")
        st.markdown(f"**User:** {user['username']}")
        
        member_since = "Unknown"
        if user.get('created_at'):
            try:
                if isinstance(user['created_at'], str):
                    member_since = user['created_at'][:10]
                else:
                    member_since = str(user['created_at'])[:10]
            except:
                member_since = "Unknown"
        
        st.markdown(f"**Member since:** {member_since}")
        
        user_files = db.get_user_files(user['id'])
        total_rows = sum([f['rows_count'] or 0 for f in user_files])
        total_columns = sum([f['columns_count'] or 0 for f in user_files])
        st.markdown(f"**Total Files:** {len(user_files)}")
        st.markdown(f"**Total Records:** {total_rows:,}")
        if user_files:
            avg_columns = total_columns / len(user_files)
            st.markdown(f"**Avg Columns:** {avg_columns:.0f}")
    
    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Upload Data":
        show_upload_page()
    elif page == "Analytics":
        show_analytics_page()
    elif page == "Settings":
        show_settings_page()

def show_dashboard_page():
    user = st.session_state.user
    
    user_files = db.get_user_files(user['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Files</h3>
            <h2>{}</h2>
        </div>
        """.format(len(user_files)), unsafe_allow_html=True)
    
    with col2:
        total_rows = sum([f['rows_count'] or 0 for f in user_files])
        st.markdown("""
        <div class="metric-card">
            <h3>Total Rows</h3>
            <h2>{:,}</h2>
        </div>
        """.format(total_rows), unsafe_allow_html=True)
    
    with col3:
        total_columns = sum([f['columns_count'] or 0 for f in user_files])
        st.markdown("""
        <div class="metric-card">
            <h3>Total Columns</h3>
            <h2>{:,}</h2>
        </div>
        """.format(total_columns), unsafe_allow_html=True)
    
    with col4:
        if user_files:
            try:
                last_upload = str(user_files[0]['upload_date'])[:10] if user_files[0]['upload_date'] else "Never"
            except (TypeError, AttributeError):
                last_upload = "Never"
        else:
            last_upload = "Never"
        st.markdown("""
        <div class="metric-card">
            <h3>Last Upload</h3>
            <h2>{}</h2>
        </div>
        """.format(last_upload), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Your Recent Files", anchor=False)
    
    if user_files:
        files_df = pd.DataFrame(user_files)
        try:
            files_df['upload_date'] = pd.to_datetime(files_df['upload_date']).dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            files_df['upload_date'] = files_df['upload_date'].astype(str)
        files_df['file_size_mb'] = (files_df['file_size'] / (1024*1024)).round(2)
        
        display_df = files_df[['filename', 'upload_date', 'rows_count', 'columns_count', 'file_size_mb']].copy()
        display_df.columns = ['File Name', 'Upload Date', 'Rows', 'Columns', 'Size (MB)']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No files uploaded yet. Go to 'Upload Data' to get started!")

def show_upload_page():
    st.subheader("📁 Upload Your Data", anchor=False)
    
    with st.expander("🎯 Need Sample Data to Test?", expanded=False):
        st.markdown("""
        **Don't have data to test with?** We've prepared 11 sample datasets for you!
        
        📊 **Available Sample Datasets:**
        - Sales Data, Customer Data, Employee Data
        - Marketing Data, Financial Data, Inventory Data
        - Survey Data, Website Analytics, Project Data
        - E-commerce Data, IoT Sensor Data
        
        **How to get them:**
        1. Download sample files from the DataLoom sample data collection
        2. Upload any `sample_*.csv` file here
        3. Start exploring your data analytics!
        
        *All sample data is synthetic and safe to use for testing.*
        """)
    
    uploaded_file = st.file_uploader(
        "📁 Drag and drop your file here, or click to browse",
        type=['csv', 'xlsx', 'xls'],
        help="Drag and drop CSV or Excel files for analysis (Max 50MB)",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if len(uploaded_file.getvalue()) > max_size:
            st.error("File size exceeds 50MB limit. Please upload a smaller file.")
            return
            
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            file_size = len(uploaded_file.getvalue())
            rows_count = len(df)
            columns_count = len(df.columns)
            
            st.success(f"File uploaded successfully! ({rows_count:,} rows, {columns_count} columns, {file_size/1024/1024:.1f} MB)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
            
            with col2:
                st.subheader("Column Information")
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null Count': df.count(),
                    'Null Count': df.isnull().sum()
                })
                st.dataframe(col_info, use_container_width=True, hide_index=True)
            
            if st.button("Save File to DataLoom", use_container_width=True):
                user = st.session_state.user
                
                with st.spinner("Auto-compressing and saving to database..."):
                    file_type = 'csv' if uploaded_file.name.endswith('.csv') else 'excel'
                    
                    file_id = db.save_user_file_with_data(user['id'], uploaded_file.name, df, file_type)
                    
                    if file_id:
                        file_key = f"{user['id']}_{uploaded_file.name}"
                        st.session_state.uploaded_files[file_key] = {
                            'data': df,
                            'filename': uploaded_file.name
                        }
                        
                        st.success("✅ File saved successfully to DataLoom!")
                        st.balloons()
                        
                        # Show file info
                        st.info(f"� Saved: {rows_count:,} rows, {columns_count} columns")
                    else:
                        st.error("❌ Error saving file. Please try again.")
                    
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

def show_analytics_page():
    st.subheader("📈 Data Analytics", anchor=False)
    
    user = st.session_state.user
    user_files = db.get_user_files(user['id'])
    
    if not user_files:
        st.info("No files uploaded yet. Upload a file first to start analyzing!")
        return
    
    # File selection
    file_options = {f['filename']: f for f in user_files}
    selected_filename = st.selectbox("Select a file to analyze:", list(file_options.keys()))
    
    if selected_filename:
        selected_file = file_options[selected_filename]
        
        try:
            # Try to load from session state first
            file_key = f"{st.session_state.user['id']}_{selected_filename}"
            if 'uploaded_files' in st.session_state and file_key in st.session_state.uploaded_files:
                df = st.session_state.uploaded_files[file_key]['data']
            else:
                # Try to load from database (compressed data)
                with st.spinner("Loading file data..."):
                    # First find the file_id from user_files
                    user_files = db.get_user_files(st.session_state.user['id'])
                    file_id = None
                    for file_info in user_files:
                        if file_info['filename'] == selected_filename:
                            file_id = file_info['id']
                            break
                    
                    if file_id:
                        df = db.get_file_data(file_id)
                    else:
                        df = None
                    
                if df is not None:
                    # Store in session state for faster access
                    if 'uploaded_files' not in st.session_state:
                        st.session_state.uploaded_files = {}
                    st.session_state.uploaded_files[file_key] = {
                        'data': df,
                        'filename': selected_filename
                    }
                    st.success("📁 File loaded from storage!")
                else:
                    st.error("❌ Could not load file data. The file may need to be re-uploaded.")
                    st.info("💡 Tip: Files are automatically saved and compressed, but very old files may need re-uploading.")
                    return
            
            # Initialize analyzer
            analyzer = DataAnalyzer(df)
            
            # Analysis tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Visualizations", "Correlations", "Export"])
            
            with tab1:
                st.subheader("Data Summary")
                summary = analyzer.get_summary_stats()
                
                # Basic info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Rows", f"{summary['basic_info']['rows']:,}")
                with col2:
                    st.metric("Columns", summary['basic_info']['columns'])
                with col3:
                    st.metric("Missing Values", f"{summary['basic_info']['missing_values']:,}")
                with col4:
                    try:
                        memory_mb = summary['basic_info']['memory_usage'] / (1024 * 1024)
                        st.metric("Memory Usage", f"{memory_mb:.1f} MB")
                    except (KeyError, TypeError, ZeroDivisionError):
                        st.metric("Memory Usage", "N/A")
                
                # Data types
                st.subheader("Column Types")
                type_cols = st.columns(3)
                with type_cols[0]:
                    st.metric("Numeric", summary['column_types']['numeric'])
                with type_cols[1]:
                    st.metric("Categorical", summary['column_types']['categorical'])
                with type_cols[2]:
                    st.metric("DateTime", summary['column_types']['datetime'])
                
                # Numeric summary
                if analyzer.numeric_columns:
                    st.subheader("Numeric Columns Summary")
                    numeric_df = pd.DataFrame(summary['numeric_summary'])
                    st.dataframe(numeric_df, use_container_width=True)
            
            with tab2:
                st.subheader("Data Visualizations")
                
                if analyzer.numeric_columns:
                    # Distribution plots
                    st.write("**Distribution Plots**")
                    selected_numeric = st.selectbox("Select numeric column:", analyzer.numeric_columns)
                    
                    if selected_numeric:
                        col1, col2 = st.columns(2)
                        with col1:
                            fig_hist = px.histogram(df, x=selected_numeric, title=f"Distribution of {selected_numeric}")
                            st.plotly_chart(fig_hist, use_container_width=True)
                        
                        with col2:
                            fig_box = px.box(df, y=selected_numeric, title=f"Box Plot of {selected_numeric}")
                            st.plotly_chart(fig_box, use_container_width=True)
                
                if len(analyzer.numeric_columns) > 1:
                    # Scatter plots
                    st.write("**Scatter Plots**")
                    col1, col2 = st.columns(2)
                    with col1:
                        x_axis = st.selectbox("X-axis:", analyzer.numeric_columns, key="scatter_x")
                    with col2:
                        y_axis = st.selectbox("Y-axis:", analyzer.numeric_columns, key="scatter_y")
                    
                    if x_axis and y_axis and x_axis != y_axis:
                        fig_scatter = px.scatter(df, x=x_axis, y=y_axis, title=f"{x_axis} vs {y_axis}")
                        st.plotly_chart(fig_scatter, use_container_width=True)
            
            with tab3:
                st.subheader("Correlation Analysis")
                
                if len(analyzer.numeric_columns) > 1:
                    corr_matrix = df[analyzer.numeric_columns].corr()
                    fig_corr = px.imshow(corr_matrix, 
                                       text_auto=True, 
                                       aspect="auto",
                                       title="Correlation Matrix")
                    st.plotly_chart(fig_corr, use_container_width=True)
                    
                    # Insights
                    st.subheader("Key Insights")
                    insights = analyzer.get_insights()
                    for insight in insights:
                        st.markdown(f"""
                        <div class="insight-card">
                            <strong>{insight['type']}:</strong> {insight['message']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Need at least 2 numeric columns for correlation analysis.")
            
            with tab4:
                st.subheader("Export Data")
                
                # Processed data download
                st.write("**Download Processed Data**")
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"processed_{selected_filename}",
                    mime="text/csv"
                )
                
                # Summary report
                st.write("**Generate Summary Report**")
                if st.button("Generate Report"):
                    report = analyzer.generate_report()
                    st.download_button(
                        label="Download Report",
                        data=report,
                        file_name=f"report_{selected_filename.split('.')[0]}.txt",
                        mime="text/plain"
                    )
                    
        except Exception as e:
            st.error(f"Error analyzing file: {str(e)}")

def show_settings_page():
    st.subheader("⚙️ Settings", anchor=False)
    
    user = st.session_state.user
    
    st.write("**User Profile**")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Email:** {user['email']}")
    try:
        member_since_display = str(user['created_at'])[:10] if user['created_at'] else 'Unknown'
    except (TypeError, AttributeError):
        member_since_display = 'Unknown'
    st.write(f"**Member Since:** {member_since_display}")
    try:
        last_login_display = str(user['last_login'])[:16] if user['last_login'] else 'Unknown'
    except (TypeError, AttributeError):
        last_login_display = 'Unknown'
    st.write(f"**Last Login:** {last_login_display}")
    
    st.markdown("---")
    
    st.write("**File Management**")
    user_files = db.get_user_files(user['id'])
    
    if user_files:
        st.write(f"You have {len(user_files)} files stored in DataLoom.")
        
        # Option to delete files
        st.write("**Delete Files**")
        file_to_delete = st.selectbox("Select file to delete:", [f['filename'] for f in user_files])
        
        if st.button("Delete Selected File", type="secondary"):
            # Find the file_id for the selected filename
            file_id = None
            for file_info in user_files:
                if file_info['filename'] == file_to_delete:
                    file_id = file_info['id']
                    break
            
            if file_id and db.delete_user_file(file_id, user['id']):
                # Also remove from session state if exists
                files_to_remove = [key for key in st.session_state.get('uploaded_files', {}).keys() 
                                 if file_to_delete in key]
                for key in files_to_remove:
                    del st.session_state.uploaded_files[key]
                
                st.success("File deleted successfully!")
                st.rerun()
            else:
                st.error("Error deleting file.")
    else:
        st.info("No files uploaded yet.")

def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        if 'user' in st.session_state:
            del st.session_state.user
        if 'uploaded_files' in st.session_state:
            st.session_state.uploaded_files = {}
        
        show_login_page()
    else:
        if 'user' not in st.session_state:
            st.session_state.authenticated = False
            st.error("Session expired. Please login again.")
            st.rerun()
        else:
            show_dashboard()

if __name__ == "__main__":
    main()
