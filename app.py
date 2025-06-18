import streamlit as st
import pandas as pd
from database import DatabaseManager
from data_analyzer import DataAnalyzer
import plotly.express as px
import os
from datetime import datetime
import base64

# Function to load and encode favicon
def get_favicon_base64():
    try:
        with open("assets/favicon.ico", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

# Function to get favicon data URL
def get_favicon_data_url():
    favicon_b64 = get_favicon_base64()
    if favicon_b64:
        return f"data:image/x-icon;base64,{favicon_b64}"
    else:
        # Fallback to external icon if favicon not found
        return "https://cdn-icons-png.flaticon.com/512/2103/2103665.png"

st.set_page_config(
    page_title="DataLoom - Analytics Dashboard",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

# Security: Redirect non-authenticated users
if not st.session_state.authenticated:
    # Only allow access to login page
    pass
else:
    # Authenticated users can access the app
    pass

st.markdown("""
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
<style>
    /* Dark mode as default */
    .stApp {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: #ffffff;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.3));
    }
    
    .logo-svg {
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        backdrop-filter: blur(10px);
    }
    
    .metric-card h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .metric-card h2 {
        color: #ffffff;
        margin: 0;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .sidebar .stSelectbox > div > div {
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

def show_login_page():
    st.markdown(f"""
    <div class="main-header">
        <div class="logo-container">
            <img src="{get_favicon_data_url()}" class="logo-icon" alt="DataLoom Logo">
            <h1 style="margin: 0;">DataLoom</h1>
        </div>
        <p>Professional Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Welcome back!")
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
        st.subheader("Create your account")
        
        # Password requirements info
        with st.expander("📋 Account Requirements", expanded=False):
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
            new_username = st.text_input("Username", help="Choose a unique username (3-20 characters)")
            new_email = st.text_input("Email Address", placeholder="example@domain.com")
            new_password = st.text_input("Password", type="password", help="Minimum 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_btn = st.form_submit_button("Create Account", use_container_width=True)
            
            if signup_btn:
                # Validation
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                username_pattern = r'^[a-zA-Z0-9_-]{3,20}$'
                
                # Check all fields filled
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("⚠️ Please fill in all fields")
                # Username validation
                elif not re.match(username_pattern, new_username):
                    st.error("❌ Username must be 3-20 characters long and contain only letters, numbers, hyphens, and underscores")
                # Email validation
                elif not re.match(email_pattern, new_email):
                    st.error("❌ Please enter a valid email address (example: user@domain.com)")
                # Password length validation
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters long")
                # Password strength validation
                elif not re.search(r'[A-Za-z]', new_password) or not re.search(r'[0-9]', new_password):
                    st.error("❌ Password must contain at least one letter and one number")
                # Password confirmation validation
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match. Please check both password fields")
                else:
                    # Try to create user
                    if db.create_user(new_username, new_email, new_password):
                        st.success("✅ Account created successfully! You can now login with your credentials.")
                        st.info("💡 Please switch to the Login tab to access your account")
                    else:
                        st.error("❌ Username or email already exists. Please try different credentials.")

def show_dashboard():
    user = st.session_state.user
    
    # Header without theme toggle
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class="main-header">
            <div class="logo-container">
                <img src="{get_favicon_data_url()}" class="logo-icon" alt="DataLoom Logo">
                <h1 style="margin: 0;">Logged in as {user['username']} 👋</h1>
            </div>
            <p>Your personal DataLoom analytics dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Sidebar navigation
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
        st.markdown(f"**Member since:** {user['created_at'][:10] if user['created_at'] else 'Unknown'}")
        
        # File storage info
        user_files = db.get_user_files(user['id'])
        total_size = sum([f['file_size'] or 0 for f in user_files]) / (1024*1024)  # Convert to MB
        st.markdown(f"**Files stored:** {len(user_files)}")
        st.markdown(f"**Storage used:** {total_size:.1f} MB")
    
    # Main content based on selected page
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
    
    # Get user files
    user_files = db.get_user_files(user['id'])
    
    # Dashboard metrics
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
        total_size = sum([f['file_size'] or 0 for f in user_files])
        st.markdown("""
        <div class="metric-card">
            <h3>Storage Used</h3>
            <h2>{:.1f} MB</h2>
        </div>
        """.format(total_size / (1024*1024)), unsafe_allow_html=True)
    
    with col4:
        last_upload = user_files[0]['upload_date'][:10] if user_files else "Never"
        st.markdown("""
        <div class="metric-card">
            <h3>Last Upload</h3>
            <h2>{}</h2>
        </div>
        """.format(last_upload), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent files
    st.subheader("Your Recent Files")
    
    if user_files:
        files_df = pd.DataFrame(user_files)
        files_df['upload_date'] = pd.to_datetime(files_df['upload_date']).dt.strftime('%Y-%m-%d %H:%M')
        files_df['file_size_mb'] = (files_df['file_size'] / (1024*1024)).round(2)
        
        display_df = files_df[['filename', 'upload_date', 'rows_count', 'columns_count', 'file_size_mb']].copy()
        display_df.columns = ['File Name', 'Upload Date', 'Rows', 'Columns', 'Size (MB)']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No files uploaded yet. Go to 'Upload Data' to get started!")

def show_upload_page():
    st.subheader("📁 Upload Your Data")
    
    # Sample Data Information
    with st.expander("🎯 Need Sample Data to Test?", expanded=False):
        st.markdown("""
        **Don't have data to test with?** We've prepared 11 sample datasets for you!
        
        📊 **Available Sample Datasets:**
        - Sales Data, Customer Data, Employee Data
        - Marketing Data, Financial Data, Inventory Data
        - Survey Data, Website Analytics, Project Data
        - E-commerce Data, IoT Sensor Data
        
        **How to get them:**
        1. Visit our [GitHub Repository](https://github.com/yourusername/DataLoom)
        2. Download any `sample_*.csv` file
        3. Upload it here to start exploring!
        
        *All sample data is synthetic and safe to use for testing.*
        """)
    
    st.markdown("""
    <div class="upload-section">
        <h3>Supported Formats</h3>
        <p>CSV, Excel (XLS, XLSX) - Max size: 50MB</p>
        <p>Files are automatically compressed and stored securely</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose your file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload CSV or Excel files for analysis (Max 50MB)"
    )
    
    if uploaded_file is not None:
        # Check file size limit (50MB)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if len(uploaded_file.getvalue()) > max_size:
            st.error("File size exceeds 50MB limit. Please upload a smaller file.")
            return
            
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # File info
            file_size = len(uploaded_file.getvalue())
            rows_count = len(df)
            columns_count = len(df.columns)
            
            # Display preview
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
            
            # Save file button
            if st.button("Save File to DataLoom", use_container_width=True):
                user = st.session_state.user
                
                with st.spinner("Compressing and saving file..."):
                    # Compress and store file data
                    import pickle
                    import gzip
                    import base64
                    
                    # Compress the dataframe
                    compressed_data = gzip.compress(pickle.dumps(df))
                    encoded_data = base64.b64encode(compressed_data).decode('utf-8')
                    
                    # Store compressed data in database
                    if db.save_user_file_with_data(user['id'], uploaded_file.name, 
                                                 encoded_data, file_size, rows_count, columns_count):
                        # Also store in session state for immediate access
                        file_key = f"{user['id']}_{uploaded_file.name}"
                        st.session_state.uploaded_files[file_key] = {
                            'data': df,
                            'filename': uploaded_file.name
                        }
                        
                        st.success("✅ File saved successfully and compressed for storage!")
                        st.balloons()
                        
                        # Show compression stats
                        compression_ratio = len(compressed_data) / file_size * 100
                        st.info(f"🗜️ Compression: {compression_ratio:.1f}% of original size")
                    else:
                        st.error("Error saving file. Please try again.")
                    
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

def show_analytics_page():
    st.subheader("📈 Data Analytics")
    
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
                    df = db.get_file_data(st.session_state.user['id'], selected_filename)
                    
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
                    st.metric("Memory Usage", f"{summary['basic_info']['memory_usage']/1024/1024:.1f} MB")
                
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
    st.subheader("⚙️ Settings")
    
    user = st.session_state.user
    
    # User profile
    st.write("**User Profile**")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**Member Since:** {user['created_at'][:10] if user['created_at'] else 'Unknown'}")
    st.write(f"**Last Login:** {user['last_login'][:16] if user['last_login'] else 'Unknown'}")
    
    st.markdown("---")
    
    # File management
    st.write("**File Management**")
    user_files = db.get_user_files(user['id'])
    
    if user_files:
        st.write(f"You have {len(user_files)} files stored in DataLoom.")
        
        # Option to delete files
        st.write("**Delete Files**")
        file_to_delete = st.selectbox("Select file to delete:", [f['filename'] for f in user_files])
        
        if st.button("Delete Selected File", type="secondary"):
            if db.delete_user_file(user['id'], file_to_delete):
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

# Main application logic
def main():
    # Security: Prevent access without authentication
    # This ensures users can't access the app even if they have a shared link
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Authentication gate - redirect all unauthenticated users to login
    if not st.session_state.authenticated:
        # Clear any potentially cached data for security
        if 'user' in st.session_state:
            del st.session_state.user
        if 'uploaded_files' in st.session_state:
            st.session_state.uploaded_files = {}
        
        show_login_page()
    else:
        # Verify user session is still valid
        if 'user' not in st.session_state:
            st.session_state.authenticated = False
            st.error("Session expired. Please login again.")
            st.rerun()
        else:
            show_dashboard()

if __name__ == "__main__":
    main()
