import streamlit as st
import pandas as pd
from database import DatabaseManager
from data_analyzer import DataAnalyzer
import plotly.express as px
import re
from html import escape
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="DataLoom - Analytics Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, rgba(251, 218, 3, 0.24) 0%, rgba(74, 48, 12, 0.18) 28%, rgba(13, 13, 13, 0) 68%), #0D0D0D;
        color: #e6edf3;
    }
    .stApp::before { content: ""; position: fixed; inset: -35%; z-index: 0; background: radial-gradient(ellipse at 50% 28%, rgba(251, 218, 3, 0.48) 0%, rgba(152, 97, 20, 0.26) 26%, rgba(13, 13, 13, 0) 66%); filter: blur(120px); pointer-events: none; }
    .block-container { max-width: 1200px; padding-top: 2.5rem; padding-bottom: 1rem; }
    .main-header {
        background: transparent;
        padding: 0; border: 0; color: #f0f6fc;
        text-align: left; margin: 0 0 1.25rem;
        box-shadow: none;
    }
    .main-header h1 { color: #fbda03; margin: 0; }
    .brand-mark { color: #fbda03; font-size: clamp(2.8rem, 7vw, 5.75rem); font-weight: 800; line-height: 0.82; letter-spacing: 0.08em; text-align: center; margin: 0 0 3.5rem; text-shadow: 0 0 34px rgba(251, 218, 3, 0.32); }
    .brand-mark span { display: block; }
    .auth-title { color: #f0f6fc; font-size: 2rem; font-weight: 700; text-align: center; margin: 0.5rem 0 0.2rem; }
    .auth-tagline { color: #f0f6fc; text-align: center; margin: 0 0 1.25rem; }
    .metric-card {
        background: #161b22;
        padding: 1rem; border-radius: 8px;
        border: 1px solid #242424;
        color: #e6edf3; margin-bottom: 1rem;
    }
    .metric-card h3 { color: #f0f6fc; margin-bottom: 0.5rem; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-card h2 { color: #f0f6fc; margin: 0; font-size: 1.5rem; font-weight: bold; }
    .insight-card {
        background: #161b22;
        padding: 0.8rem; border-radius: 6px; border-left: 3px solid #fbda03;
        margin: 0.5rem 0; color: #f0f6fc; border-top: 1px solid #242424; border-right: 1px solid #242424; border-bottom: 1px solid #242424;
    }
    .stForm {
        background: rgba(31, 23, 15, 0.92); padding: 1.35rem; border-radius: 10px;
        border: 1px solid #4a351d; margin: 1rem 0;
        box-shadow: 0 16px 50px rgba(0, 0, 0, 0.22);
    }
    .stButton > button, .stForm button { background: #fbda03 !important; color: #000000 !important; border: 1px solid #fbda03 !important; border-radius: 6px !important; font-weight: 600; }
    .stButton > button:hover, .stForm button:hover { background: #d9bb00 !important; color: #000000 !important; border-color: #d9bb00 !important; }
    [data-testid="stSidebar"] .stButton > button { background: #fbda03 !important; color: #000000 !important; border-color: #fbda03 !important; }
    [data-testid="stSidebar"] .stButton > button p { color: #000000 !important; }
    .stTextInput > div > div > input { background: #130f0b !important; border: 1px solid #604624 !important; color: #f5eadc !important; border-radius: 6px !important; }
    .stTextInput > div > div > input:focus { border-color: #fbda03 !important; box-shadow: 0 0 0 1px #fbda03 !important; }
    [data-testid="stSidebar"] { background: #010409; border-right: 1px solid #242424; color: #f0f6fc; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #f0f6fc; }
    [data-testid="stMetric"] { background: #161b22; border: 1px solid #242424; border-radius: 8px; padding: 1rem; }
    [data-testid="stFileUploader"] { background: #161b22; border: 1px dashed #242424; border-radius: 8px; padding: 0.5rem; }
    .upload-helper { color: #ffffff; font-size: 0.9rem; margin: -0.5rem 0 1rem; }
    .upload-helper a { color: #ffffff !important; text-decoration: underline; }
    .password-checklist { background: #21170e; border: 1px solid #4a351d; border-radius: 6px; padding: 0.75rem 1rem; margin: 0.5rem 0 1rem; color: #e0c09a; font-size: 0.9rem; }
    .password-checklist p { margin: 0.25rem 0; }
    .password-checklist .valid { color: #f0f6fc; }
    .password-checklist .invalid { color: #c79d6e; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 1.25rem; }
    .stTabs [data-baseweb="tab"] { color: #f0f6fc; }
    .stTabs [aria-selected="true"] { color: #fbda03 !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #fbda03; }
    .footer-bar { position: fixed; left: 0; right: 0; bottom: 0; z-index: 10; background: rgba(13, 13, 13, 0.94); border-top: 1px solid #4a351d; color: #ffffff; font-size: 0.78rem; text-align: center; padding: 0.7rem 0 0.55rem; }
    .stForm { max-width: 420px; }
    .block-container { padding-bottom: 5rem; }
</style>
""", unsafe_allow_html=True)


if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

db = st.session_state.db_manager
IST = ZoneInfo("Asia/Kolkata")

def format_ist_timestamp(value, date_only: bool = False) -> str:
    if not value:
        return "Never"
    try:
        timestamp = pd.to_datetime(value, utc=True).tz_convert(IST)
        return timestamp.strftime("%Y-%m-%d" if date_only else "%d %b %Y, %I:%M %p IST")
    except (TypeError, ValueError, OverflowError):
        return str(value)

def load_cached_file_data(file_id, user_id):
    return db.get_file_data(file_id, user_id)

@st.cache_data
def load_sample_df():
    local_paths = [
        Path(__file__).parent / "assets" / "sample_sales_data.csv",
        Path(__file__).parent / "sample_sales_data.csv",
    ]
    for sample_path in local_paths:
        if sample_path.is_file():
            try:
                return pd.read_csv(sample_path, encoding='latin1')
            except Exception:
                continue
    
    remote_urls = [
        "https://raw.githubusercontent.com/ag863k/DataLoom/main/sample_sales_data.csv",
    ]
    for url in remote_urls:
        try:
            return pd.read_csv(url, encoding='latin1')
        except Exception:
            continue
    return None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = pd.Timestamp.now(tz='UTC')
if 'login_timestamp' not in st.session_state:
    st.session_state.login_timestamp = None

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

def render_password_requirements(password: str):
    requirements = [
        (len(password) >= 8, "At least 8 characters"),
        (bool(re.search(r'[A-Z]', password)), "One uppercase letter"),
        (bool(re.search(r'[a-z]', password)), "One lowercase letter"),
        (bool(re.search(r'[0-9]', password)), "One number"),
        (bool(re.search(r'[^A-Za-z0-9]', password)), "One special character"),
    ]
    checks = "".join(
        f"<p class={'valid' if passed else 'invalid'}>{'&#10003;' if passed else '&#8226;'} {label}</p>"
        for passed, label in requirements
    )
    st.markdown(f'<div class="password-checklist"><strong>Password requirements</strong>{checks}</div>', unsafe_allow_html=True)

def check_session_timeout():
    if st.session_state.get('authenticated'):
        TIMEOUT_MINUTES = 30
        last_activity = st.session_state.get('last_activity')
        if last_activity:
            elapsed = (pd.Timestamp.now(tz='UTC') - last_activity).total_seconds() / 60
            if elapsed > TIMEOUT_MINUTES:
                st.session_state.authenticated = False
                st.session_state.user = None
                st.warning(f"Session expired after {TIMEOUT_MINUTES} minutes of inactivity.")
                st.rerun()
        st.session_state.last_activity = pd.Timestamp.now(tz='UTC')

def show_login_page():
    st.markdown('<div class="brand-mark"><span>DATA</span><span>LOOM</span></div>', unsafe_allow_html=True)
    _, auth_column, _ = st.columns([1, 1.25, 1])
    with auth_column:
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
                        st.session_state.login_timestamp = pd.Timestamp.now(tz='UTC')
                        st.session_state.last_activity = pd.Timestamp.now(tz='UTC')
                        if 'signup_success' in st.session_state:
                            del st.session_state.signup_success
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with signup_tab:
            st.markdown('<div class="auth-title">Create your account</div>', unsafe_allow_html=True)
            if st.session_state.get('signup_success'):
                st.success("Account created successfully!")
                st.info("Please switch to the Login tab to sign in with your new credentials.")
            else:
                with st.form("signup_form"):
                    new_username = st.text_input("Username", key="signup_user")
                    new_email = st.text_input("Email Address", key="signup_email")
                    new_password = st.text_input("Password", type="password", key="signup_pass")
                    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
                    render_password_requirements(new_password)

                    if st.form_submit_button("Create Account", use_container_width=True):
                        new_username = new_username.strip()
                        new_email = new_email.strip().lower()
                        password_errors = validate_password(new_password)
                        if not new_username or not new_email or not new_password or not confirm_password:
                            st.error("Please complete every field.")
                        elif not re.match(r'^[a-zA-Z0-9_]{3,30}$', new_username):
                            st.error("Username must be 3-30 characters and use only letters, numbers, or underscores.")
                        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                            st.error("Enter a valid email address.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match.")
                        elif password_errors:
                            for error in password_errors:
                                st.error(error)
                        elif db.get_user_by_username(new_username) or db.get_user_by_email(new_email):
                            st.error("Username or email is already registered. Please choose another.")
                        elif db.create_user(new_username, new_email, new_password):
                            st.session_state.signup_success = True
                            for key in ["signup_user", "signup_email", "signup_pass", "signup_confirm"]:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error("Account could not be created. Please try again.")

def render_footer():
    st.markdown('<div class="footer-bar">&copy; 2024 DataLoom. All rights reserved.</div>', unsafe_allow_html=True)

def show_dashboard():
    check_session_timeout()
    user = st.session_state.user
    with st.sidebar:
        st.markdown('<div style="text-align: center; padding-top: 1rem;"><h2 style="color: #fbda03;">DataLoom</h2></div>', unsafe_allow_html=True)
        st.markdown("---")
        page = st.radio("Navigation", ["Dashboard", "Upload Data", "Analytics", "Settings"], label_visibility="collapsed")
        st.markdown("---")
        st.markdown(f"**Welcome, {user['username']}**")
        if st.session_state.login_timestamp:
            session_duration = (pd.Timestamp.now(tz='UTC') - st.session_state.login_timestamp).total_seconds() / 60
            st.caption(f"Session: {int(session_duration)} min")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
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
    if user_files:
        last_upload = format_ist_timestamp(
            max(user_files, key=lambda f: f['upload_date'])['upload_date'],
            date_only=True
        )
    col3.markdown(f'<div class="metric-card"><h3>Last Upload</h3><h2>{last_upload}</h2></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Recent Files")
    if user_files:
        files_df = pd.DataFrame(user_files)
        files_df['upload_date'] = files_df['upload_date'].map(format_ist_timestamp)
        st.dataframe(files_df[['filename', 'upload_date', 'rows_count', 'columns_count']], use_container_width=True, hide_index=True, 
                     column_config={"filename": "File Name", "upload_date": "Upload Date", "rows_count": "Rows", "columns_count": "Columns"})
    else: st.info("No files uploaded. Go to 'Upload Data' to get started.")

def show_upload_page():
    st.subheader("Add a dataset")
    st.markdown(
        '<p class="upload-helper">For additional files, refer to: '
        '<a href="https://mega.nz/folder/JF031ZrJ#2C1eypfC7u0aBZvF_mdYxA" target="_blank">Link</a></p>',
        unsafe_allow_html=True
    )
    
    MAX_FILE_SIZE_MB = 50
    uploaded_file = st.file_uploader("Drag and drop CSV or Excel files", type=['csv', 'xlsx'], key="file_uploader")
    
    if uploaded_file:
        file_size = len(uploaded_file.getvalue())
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error(f"File size exceeds the {MAX_FILE_SIZE_MB}MB limit. Please upload a smaller file.")
            return

        try:
            if uploaded_file.name.lower().endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            elif uploaded_file.name.lower().endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                st.error("Unsupported file format. Please upload CSV or Excel files.")
                return
            
            if df.empty:
                st.error("The uploaded file is empty. Please upload a file with data.")
                return
            
            st.success(f"Successfully loaded `{uploaded_file.name}` ({len(df)} rows, {len(df.columns)} columns)")
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            st.dataframe(df.head(10), use_container_width=True)
            
            st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Save to My Files", type="primary", use_container_width=True, key="save_file_btn"):
                    with st.spinner("Saving..."):
                        file_id = db.save_user_file_with_data(st.session_state.user['id'], uploaded_file.name, df, uploaded_file.type)
                        if file_id:
                            st.success(f"File uploaded successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to upload the file. Please try again.")
            
            st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
        except pd.errors.EmptyDataError:
            st.error("The file is empty or corrupted. Please upload a valid file.")
        except pd.errors.ParserError:
            st.error("Failed to parse the file. Please ensure it's a valid CSV or Excel file.")
        except Exception as e: 
            st.error(f"Error processing file: {str(e)}")
            st.info("If the issue persists, try converting your file to CSV format and re-upload.")

def display_analysis_ui(analyzer: DataAnalyzer, source_name: str):
    df, summary = analyzer.df, analyzer.get_summary_stats()
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Rows", f"{summary['basic_info']['rows']:,}")
    m_col2.metric("Columns", summary['basic_info']['columns'])
    m_col3.metric("Missing Values", f"{summary['basic_info']['missing_values']:,}")
    st.subheader("Key Insights")
    for insight in analyzer.get_insights():
        insight_type = escape(str(insight['type']))
        insight_message = escape(str(insight['message']))
        st.markdown(
            f"<div class='insight-card'><strong>{insight_type}:</strong> {insight_message}</div>",
            unsafe_allow_html=True
        )
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Visualizations", "Data Summary", "Export"])
    with tab1:
        if not analyzer.numeric_columns: st.info("No numeric columns available for visualization.")
        else:
            plot_type = st.selectbox("Choose plot type", ["Histogram", "Scatter Plot", "Box Plot"])
            if plot_type == "Histogram":
                col = st.selectbox("Select column", analyzer.numeric_columns)
                st.plotly_chart(px.histogram(df, x=col, title=f"Distribution of {col}", color_discrete_sequence=["#bdbdbd"]), use_container_width=True)
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
    st.subheader("Choose a dataset to analyze")
    user_files = db.get_user_files(st.session_state.user['id'])
    dataset_options = {"Sample dataset - Sales": "sample_sales_data"}
    dataset_options.update({f"Uploaded file - {file['filename']}": file['id'] for file in user_files})
    
    if len(dataset_options) == 1:
        st.info("You haven't uploaded any files yet. Upload a file from the 'Upload Data' page or use the sample dataset.")
    
    selected_dataset = st.selectbox("Dataset", list(dataset_options), label_visibility="collapsed")
    selected_source = dataset_options[selected_dataset]

    df_to_analyze = None
    
    with st.spinner("Loading dataset..."):
        if selected_source == "sample_sales_data":
            df_to_analyze = load_sample_df()
            source_name = selected_source
        else:
            try:
                user_id = st.session_state.user['id']
                df_to_analyze = load_cached_file_data(selected_source, user_id)
                
                if df_to_analyze is None:
                    st.error("File could not be loaded. Please re-upload the file.")
                    return
                elif df_to_analyze.empty:
                    st.error("The file is empty.")
                    return
                
                source_name = selected_dataset.removeprefix("Uploaded file - ").rsplit('.', 1)[0]
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please re-upload the file from 'Upload Data' page.")
                return

    if df_to_analyze is None or df_to_analyze.empty:
        st.error("Dataset could not be loaded.")
        return
    
    st.caption(f"Currently analyzing: {selected_dataset}")
    display_analysis_ui(DataAnalyzer(df_to_analyze), source_name)

def show_settings_page():
    st.subheader("File Management")
    user_files = db.get_user_files(st.session_state.user['id'])
    if user_files:
        files_df = pd.DataFrame(user_files)[['filename', 'upload_date', 'rows_count']]
        files_df['upload_date'] = files_df['upload_date'].map(format_ist_timestamp)
        st.dataframe(files_df, use_container_width=True, hide_index=True)
        file_to_delete_name = st.selectbox("Select a file to delete", [f['filename'] for f in user_files])
        if st.button("Delete Selected File", type="secondary", use_container_width=True):
            file_id = next((f['id'] for f in user_files if f['filename'] == file_to_delete_name), None)
            if file_id and db.delete_user_file(file_id, st.session_state.user['id']):
                st.success(f"File '{file_to_delete_name}' has been deleted.")
                st.rerun()
            else: st.error("Failed to delete file.")
    else: st.info("You have no uploaded files.")

def main():
    if not st.session_state.get('authenticated'):
        show_login_page()
    else:
        show_dashboard()
    render_footer()

if __name__ == "__main__":
    main()