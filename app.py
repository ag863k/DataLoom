import streamlit as st
import pandas as pd
from database import DatabaseManager
from data_analyzer import DataAnalyzer
import plotly.express as px
import re

# --- PAGE CONFIGURATION ---
# FIX: Using a reliable emoji for the page icon to avoid FileNotFoundError.
st.set_page_config(
    page_title="DataLoom - Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
# NOTE: The CSS is largely kept as is, but fragile, version-specific selectors are removed.
st.markdown("""
<style>
    /* General Styles */
    .stApp {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: #ffffff;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    .logo-container {
        display: flex; align-items: center; justify-content: center;
        gap: 0.5rem; margin-bottom: 0.5rem;
    }
    .logo-icon { width: 32px; height: 32px; }
    .metric-card {
        background: linear-gradient(135deg, #2d2d44 0%, #3d3d5c 100%);
        padding: 1rem; border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; margin-bottom: 1rem;
    }
    .metric-card h3 { color: #667eea; margin-bottom: 0.5rem; font-size: 0.9rem; }
    .metric-card h2 { color: #ffffff; margin: 0; font-size: 1.5rem; font-weight: bold; }
    .insight-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 0.8rem; border-radius: 10px; border-left: 4px solid #4CAF50;
        margin: 0.5rem 0; color: white;
    }
    /* Form & Input Styles */
    .stForm {
        background: rgba(45, 45, 68, 0.3); padding: 1.5rem; border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1); margin: 1rem 0;
    }
    .stForm button[kind="formSubmit"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border: none !important;
    }
    .stTextInput > div > div > input {
        background: rgba(61, 61, 92, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important; border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# --- HELPERS & INITIALIZATION ---

def get_logo_url():
    """FIX: Returns a reliable public URL for the logo."""
    return "https://cdn-icons-png.flaticon.com/512/2103/2103665.png"

# Use session state for caching database manager
if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        st.error(f"🚨 Critical Database Error: {e}")
        st.info("Please check your database configuration or contact support.")
        st.stop()

db = st.session_state.db_manager

# Initialize core session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

# --- AUTHENTICATION PAGES ---

def show_login_page():
    """Displays the login and sign-up interface."""
    st.markdown(f"""
    <div class="main-header">
        <div class="logo-container">
            <img src="{get_logo_url()}" class="logo-icon">
            <h1 style="margin:0;">DataLoom</h1>
        </div>
        <p>Your Professional Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    login_tab, signup_tab = st.tabs(["🔒 Login", "✍️ Sign Up"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

    with signup_tab:
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_user")
            new_email = st.text_input("Email Address", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                # Validation logic
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long.")
                elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                    st.error("Invalid email address format.")
                elif not all([new_username, new_email, new_password]):
                    st.error("Please fill all fields.")
                else:
                    # Check if email exists
                    if db.get_user_by_email(new_email):
                        st.error("This email is already registered.")
                    # Attempt to create user
                    elif db.create_user(new_username, new_email, new_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists. Please choose another one.")


# --- MAIN APPLICATION PAGES ---

def show_dashboard():
    """Main authenticated view with navigation."""
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding-top: 1rem;">
            <img src="{get_logo_url()}" style="width: 48px; height: 48px;">
            <h2 style="color: #667eea;">DataLoom</h2>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "Upload Data", "Analytics", "Settings"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown(f"**Welcome, {user['username']}**")
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown(f"""
    <div class="main-header">
        <h1>{page}</h1>
    </div>
    """, unsafe_allow_html=True)

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
    
    col1, col2, col3 = st.columns(3)
    total_rows = sum(f.get('rows_count', 0) for f in user_files)
    
    with col1:
        st.markdown(f"""<div class="metric-card"><h3>Total Files</h3><h2>{len(user_files)}</h2></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><h3>Total Rows</h3><h2>{total_rows:,}</h2></div>""", unsafe_allow_html=True)
    with col3:
        last_upload = "Never"
        if user_files:
            latest_file = max(user_files, key=lambda f: f['upload_date'])
            last_upload = pd.to_datetime(latest_file['upload_date']).strftime('%Y-%m-%d')
        st.markdown(f"""<div class="metric-card"><h3>Last Upload</h3><h2>{last_upload}</h2></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Recent Files")
    if user_files:
        files_df = pd.DataFrame(user_files)
        files_df['upload_date'] = pd.to_datetime(files_df['upload_date']).dt.strftime('%Y-%m-%d %H:%M')
        files_df['file_size_mb'] = (files_df['file_size'] / (1024*1024)).round(2)
        display_df = files_df[['filename', 'upload_date', 'rows_count', 'columns_count', 'file_size_mb']]
        display_df.columns = ['File Name', 'Upload Date', 'Rows', 'Columns', 'Size (MB)']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No files uploaded yet. Go to 'Upload Data' to get started!")

def show_upload_page():
    st.subheader("Upload Your Data")
    uploaded_file = st.file_uploader(
        "Drag and drop CSV or Excel files",
        type=['csv', 'xlsx'],
        accept_multiple_files=False,
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"Successfully loaded `{uploaded_file.name}`")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("Save File to DataLoom", use_container_width=True, type="primary"):
                with st.spinner("Compressing and saving..."):
                    file_id = db.save_user_file_with_data(st.session_state.user['id'], uploaded_file.name, df, uploaded_file.type)
                    if file_id:
                        st.success("File saved successfully!")
                        st.balloons()
                    else:
                        st.error("Failed to save the file.")
        except Exception as e:
            st.error(f"Error processing file: {e}")

def show_analytics_page():
    user = st.session_state.user
    user_files = db.get_user_files(user['id'])
    
    if not user_files:
        st.info("No files found. Please upload data first.")
        return

    file_options = {f['filename']: f['id'] for f in user_files}
    selected_filename = st.selectbox("Select a file to analyze", file_options.keys())
    
    if selected_filename:
        file_id = file_options[selected_filename]
        
        # Caching mechanism: load from db only if not in session state
        if file_id not in st.session_state.uploaded_files:
            with st.spinner("Loading data from database..."):
                st.session_state.uploaded_files[file_id] = db.get_file_data(file_id)
        
        df = st.session_state.uploaded_files[file_id]

        if df is None:
            st.error("Could not load data for this file. It might be corrupted.")
            return

        analyzer = DataAnalyzer(df)
        summary = analyzer.get_summary_stats()
        
        # Summary Metrics
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Rows", f"{summary['basic_info']['rows']:,}")
        m_col2.metric("Columns", summary['basic_info']['columns'])
        m_col3.metric("Missing Values", f"{summary['basic_info']['missing_values']:,}")

        # Insights
        st.subheader("Key Insights")
        insights = analyzer.get_insights()
        for insight in insights:
            st.markdown(f"<div class='insight-card'><strong>{insight['type']}:</strong> {insight['message']}</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Tabs for detailed analysis
        tab1, tab2, tab3 = st.tabs(["📊 Visualizations", "🔢 Data Summary", "📤 Export"])

        with tab1:
            st.subheader("Interactive Visualizations")
            if not analyzer.numeric_columns:
                st.info("No numeric columns available for visualization.")
            else:
                plot_type = st.selectbox("Choose plot type", ["Histogram", "Scatter Plot", "Box Plot"])
                if plot_type == "Histogram":
                    col = st.selectbox("Select column", analyzer.numeric_columns)
                    fig = px.histogram(df, x=col, title=f"Distribution of {col}", color_discrete_sequence=px.colors.sequential.Purples_r)
                    st.plotly_chart(fig, use_container_width=True)
                elif plot_type == "Scatter Plot" and len(analyzer.numeric_columns) > 1:
                    x_ax = st.selectbox("Select X-axis", analyzer.numeric_columns, index=0)
                    y_ax = st.selectbox("Select Y-axis", analyzer.numeric_columns, index=1)
                    c_ax = st.selectbox("Select color dimension (optional)", [None] + analyzer.categorical_columns)
                    fig = px.scatter(df, x=x_ax, y=y_ax, color=c_ax, title=f"{x_ax} vs. {y_ax}")
                    st.plotly_chart(fig, use_container_width=True)
                elif plot_type == "Box Plot":
                    col = st.selectbox("Select column", analyzer.numeric_columns)
                    fig = px.box(df, y=col, title=f"Box Plot for {col}")
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("Numeric Column Statistics")
            st.dataframe(summary['numeric_summary'], use_container_width=True)
            st.subheader("Full Data Preview")
            st.dataframe(df, use_container_width=True)

        with tab3:
            st.subheader("Download Data or Report")
            st.download_button(
                "Download Data as CSV",
                df.to_csv(index=False),
                f"processed_{selected_filename}.csv",
                "text/csv",
                use_container_width=True
            )
            st.download_button(
                "Download Summary Report",
                analyzer.generate_report(),
                f"report_{selected_filename}.txt",
                "text/plain",
                use_container_width=True
            )

def show_settings_page():
    st.subheader("File Management")
    user_files = db.get_user_files(st.session_state.user['id'])
    
    if user_files:
        files_df = pd.DataFrame(user_files)[['filename', 'upload_date', 'rows_count']]
        st.dataframe(files_df, use_container_width=True, hide_index=True)
        
        file_to_delete = st.selectbox("Select a file to delete", [f['filename'] for f in user_files])
        
        if st.button("Delete Selected File", type="secondary", use_container_width=True):
            file_id = next((f['id'] for f in user_files if f['filename'] == file_to_delete), None)
            if file_id:
                if db.delete_user_file(file_id, st.session_state.user['id']):
                    # Clear from cache
                    if file_id in st.session_state.uploaded_files:
                        del st.session_state.uploaded_files[file_id]
                    st.success(f"`{file_to_delete}` has been deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete file.")
    else:
        st.info("You have not uploaded any files.")


# --- MAIN CONTROLLER ---

def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()