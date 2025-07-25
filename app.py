import streamlit as st
import pandas as pd
from database import DatabaseManager
from data_analyzer import DataAnalyzer
import plotly.express as px
import re
from typing import List

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DataLoom - Analytics Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        color: #ffffff;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
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
    .stForm {
        background: rgba(45, 45, 68, 0.3); padding: 1.5rem; border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1); margin: 1rem 0;
    }
    .stForm button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; border: none !important; }
    .stTextInput > div > div > input { background: rgba(61, 61, 92, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; color: white !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# --- DATABASE & CACHE INITIALIZATION ---
if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        st.error(f"Critical Database Error: {e}")
        st.stop()
db = st.session_state.db_manager

# --- Caching Functions for Performance ---
@st.cache_data
def load_cached_file_data(file_id):
    return db.get_file_data(file_id)

@st.cache_data
def load_sample_df():
    url = "https://raw.githubusercontent.com/ag863k/DataLoom/main/sample_data/sample_sales_data.csv"
    try:
        return pd.read_csv(url, encoding='latin1')
    except Exception as e:
        st.error(f"Could not load sample data from GitHub. Error: {e}")
        return None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- HELPER FUNCTIONS ---
def validate_password(password: str) -> List[str]:
    """Validates password strength and returns a list of errors."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number.")
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append("Password must contain at least one special character.")
    return errors

# --- AUTHENTICATION PAGES ---
def show_login_page():
    st.markdown('<div class="main-header"><h1>DataLoom</h1><p>Your Professional Analytics Dashboard</p></div>', unsafe_allow_html=True)
    
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.form_submit_button("Login", use_container_width=True):
                user = db.verify_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with signup_tab:
        with st.expander("View Password Requirements"):
            st.markdown("""
            - At least 8 characters long
            - Contains at least one uppercase letter (A-Z)
            - Contains at least one lowercase letter (a-z)
            - Contains at least one number (0-9)
            - Contains at least one special character (e.g., !@#$%)
            """)
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_user")
            new_email = st.text_input("Email Address", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.form_submit_button("Create Account", use_container_width=True):
                password_errors = validate_password(new_password)
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Please fill all fields.")
                elif new_password != confirm_password: 
                    st.error("Passwords do not match.")
                elif password_errors:
                    for error in password_errors:
                        st.error(error)
                elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                    st.error("Invalid email address format.")
                elif db.get_user_by_email(new_email):
                    st.error("This email is already registered.")
                elif db.create_user(new_username, new_email, new_password):
                    st.success("Account created successfully. Please switch to the Login tab to sign in.")
                    for key in ["signup_user", "signup_email", "signup_pass", "signup_confirm"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                else: 
                    st.error("Username already exists. Please choose another.")

# --- MAIN APPLICATION PAGES ---
def show_dashboard():
    user = st.session_state.user
    with st.sidebar:
        st.markdown('<div style="text-align: center; padding-top: 1rem;"><h2 style="color: #667eea;">DataLoom</h2></div>', unsafe_allow_html=True)
        st.markdown("---")
        page = st.radio("Navigation", ["Dashboard", "Upload Data", "Analytics", "Settings"], label_visibility="collapsed")
        st.markdown("---")
        st.markdown(f"**Welcome, {user['username']}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    st.markdown(f'<div class="main-header"><h1>{page}</h1></div>', unsafe_allow_html=True)
    pages = {"Dashboard": show_dashboard_page, "Upload Data": show_upload_page, "Analytics": show_analytics_page, "Settings": show_settings_page}
    pages[page]()

def show_dashboard_page():
    user_files = db.get_user_files(st.session_state.user['id'])
    col1, col2, col3 = st.columns(3)
    total_rows = sum(f.get('rows_count', 0) for f in user_files)
    col1.markdown(f'<div class="metric-card"><h3>Total Files</h3><h2>{len(user_files)}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><h3>Total Rows</h3><h2>{total_rows:,}</h2></div>', unsafe_allow_html=True)
    last_upload = "Never"
    if user_files: last_upload = pd.to_datetime(max(user_files, key=lambda f: f['upload_date'])['upload_date']).strftime('%Y-%m-%d')
    col3.markdown(f'<div class="metric-card"><h3>Last Upload</h3><h2>{last_upload}</h2></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Recent Files")
    if user_files:
        files_df = pd.DataFrame(user_files)
        st.dataframe(files_df[['filename', 'upload_date', 'rows_count', 'columns_count']], use_container_width=True, hide_index=True, 
                     column_config={"filename": "File Name", "upload_date": "Upload Date", "rows_count": "Rows", "columns_count": "Columns"})
    else: st.info("No files uploaded. Go to 'Upload Data' to get started.")

def show_upload_page():
    st.subheader("Upload Your Data")
    st.info("For additional sample files, please visit the project repository on GitHub: https://github.com/ag863k/DataLoom")
    
    MAX_FILE_SIZE_MB = 50
    uploaded_file = st.file_uploader("Drag and drop CSV or Excel files", type=['csv', 'xlsx'])
    
    if uploaded_file:
        file_size = len(uploaded_file.getvalue())
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error(f"File size exceeds the {MAX_FILE_SIZE_MB}MB limit. Please upload a smaller file.")
            return

        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"Successfully loaded `{uploaded_file.name}`")
            st.dataframe(df.head(), use_container_width=True)
            if st.button("Save File to DataLoom", use_container_width=True, type="primary"):
                with st.spinner("Compressing and saving..."):
                    if db.save_user_file_with_data(st.session_state.user['id'], uploaded_file.name, df, uploaded_file.type):
                        st.success("File saved successfully.")
                        load_cached_file_data.clear()
                    else: st.error("Failed to save the file.")
        except Exception as e: st.error(f"Error processing file: {e}")

def display_analysis_ui(analyzer: DataAnalyzer, source_name: str):
    df, summary = analyzer.df, analyzer.get_summary_stats()
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Rows", f"{summary['basic_info']['rows']:,}")
    m_col2.metric("Columns", summary['basic_info']['columns'])
    m_col3.metric("Missing Values", f"{summary['basic_info']['missing_values']:,}")
    st.subheader("Key Insights")
    for insight in analyzer.get_insights():
        st.markdown(f"<div class='insight-card'><strong>{insight['type']}:</strong> {insight['message']}</div>", unsafe_allow_html=True)
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Visualizations", "Data Summary", "Export"])
    with tab1:
        if not analyzer.numeric_columns: st.info("No numeric columns available for visualization.")
        else:
            plot_type = st.selectbox("Choose plot type", ["Histogram", "Scatter Plot", "Box Plot"])
            if plot_type == "Histogram":
                col = st.selectbox("Select column", analyzer.numeric_columns)
                st.plotly_chart(px.histogram(df, x=col, title=f"Distribution of {col}", color_discrete_sequence=px.colors.sequential.Purples_r), use_container_width=True)
            elif plot_type == "Scatter Plot" and len(analyzer.numeric_columns) > 1:
                x_ax, y_ax = st.columns(2)
                x_col = x_ax.selectbox("X-axis", analyzer.numeric_columns, index=0)
                y_col = y_ax.selectbox("Y-axis", analyzer.numeric_columns, index=1)
                color_col = st.selectbox("Color dimension (optional)", [None] + analyzer.categorical_columns)
                st.plotly_chart(px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{x_col} vs. {y_col}"), use_container_width=True)
            elif plot_type == "Box Plot":
                col = st.selectbox("Select column for Box Plot", analyzer.numeric_columns)
                st.plotly_chart(px.box(df, y=col, title=f"Box Plot for {col}"), use_container_width=True)
    with tab2:
        st.subheader("Numeric Column Statistics"); st.dataframe(summary['numeric_summary'], use_container_width=True)
        st.subheader("Full Data Preview"); st.dataframe(df, use_container_width=True)
    with tab3:
        st.subheader("Download Data or Report")
        st.download_button("Download Data as CSV", df.to_csv(index=False).encode('utf-8'), f"{source_name}.csv", "text/csv", use_container_width=True)
        st.download_button("Download Summary Report", analyzer.generate_report(), f"report_{source_name}.txt", "text/plain", use_container_width=True)

def show_analytics_page():
    st.subheader("Select Data Source")
    data_source = st.radio("Choose data to analyze", ("My Uploaded Files", "Load Sample Dataset"), horizontal=True, label_visibility="collapsed")
    df_to_analyze, source_name = None, None
    if data_source == "Load Sample Dataset":
        st.info("Analyzing a sample sales dataset from the project's GitHub repository.")
        with st.spinner("Loading sample data..."):
            df_to_analyze = load_sample_df()
            source_name = "sample_sales_data"
    else:
        user_files = db.get_user_files(st.session_state.user['id'])
        if not user_files:
            st.info("No files found. Please use the 'Upload Data' page to upload a file."); return
        file_options = {f['filename']: f['id'] for f in user_files}
        selected_filename = st.selectbox("Select one of your files to analyze", file_options.keys())
        if selected_filename:
            with st.spinner("Loading data..."):
                df_to_analyze = load_cached_file_data(file_options[selected_filename])
                source_name = selected_filename.split('.')[0]
    if df_to_analyze is not None: display_analysis_ui(DataAnalyzer(df_to_analyze), source_name)

def show_settings_page():
    st.subheader("File Management")
    user_files = db.get_user_files(st.session_state.user['id'])
    if user_files:
        files_df = pd.DataFrame(user_files)[['filename', 'upload_date', 'rows_count']]
        st.dataframe(files_df, use_container_width=True, hide_index=True)
        file_to_delete_name = st.selectbox("Select a file to delete", [f['filename'] for f in user_files])
        if st.button("Delete Selected File", type="secondary", use_container_width=True):
            file_id = next((f['id'] for f in user_files if f['filename'] == file_to_delete_name), None)
            if file_id and db.delete_user_file(file_id, st.session_state.user['id']):
                load_cached_file_data.clear()
                st.success(f"File '{file_to_delete_name}' has been deleted.")
                st.rerun()
            else: st.error("Failed to delete file.")
    else: st.info("You have no uploaded files.")

# --- MAIN CONTROLLER ---
def main():
    if not st.session_state.get('authenticated'): show_login_page()
    else: show_dashboard()

if __name__ == "__main__":
    main()