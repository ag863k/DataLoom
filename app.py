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
        background: #111111;
        color: #f2f2f2;
    }
    .main-header {
        background: #1b1b1b;
        padding: 1.4rem 1.6rem; border-radius: 8px; color: #f5f5f5;
        text-align: left; margin-bottom: 1.25rem;
        border: 1px solid #333333; border-left: 4px solid #bdbdbd;
    }
    .metric-card {
        background: #1c1c1c;
        padding: 1rem; border-radius: 8px;
        border: 1px solid #353535;
        color: #f2f2f2; margin-bottom: 1rem;
    }
    .metric-card h3 { color: #a6a6a6; margin-bottom: 0.5rem; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-card h2 { color: #ffffff; margin: 0; font-size: 1.5rem; font-weight: bold; }
    .insight-card {
        background: #1c1c1c;
        padding: 0.8rem; border-radius: 6px; border-left: 3px solid #8f8f8f;
        margin: 0.5rem 0; color: #e6e6e6;
    }
    .stForm {
        background: #181818; padding: 1.5rem; border-radius: 8px;
        border: 1px solid #333333; margin: 1rem 0;
    }
    .stButton > button, .stForm button { background: #e6e6e6 !important; color: #111111 !important; border: 1px solid #e6e6e6 !important; border-radius: 6px !important; font-weight: 600; }
    .stButton > button:hover, .stForm button:hover { background: #bdbdbd !important; border-color: #bdbdbd !important; }
    .stTextInput > div > div > input { background: #242424 !important; border: 1px solid #4a4a4a !important; color: #f5f5f5 !important; border-radius: 6px !important; }
    .stTextInput > div > div > input:focus { border-color: #bdbdbd !important; box-shadow: 0 0 0 1px #bdbdbd !important; }
    [data-testid="stSidebar"] { background: #181818; border-right: 1px solid #303030; }
    [data-testid="stMetric"] { background: #1c1c1c; border: 1px solid #353535; border-radius: 8px; padding: 1rem; }
    [data-testid="stFileUploader"] { background: #1c1c1c; border: 1px dashed #555555; border-radius: 8px; padding: 0.5rem; }
    .password-checklist { background: #202020; border: 1px solid #363636; border-radius: 6px; padding: 0.75rem 1rem; margin: 0.5rem 0 1rem; color: #bdbdbd; font-size: 0.9rem; }
    .password-checklist p { margin: 0.25rem 0; }
    .password-checklist .valid { color: #d7d7d7; }
    .password-checklist .invalid { color: #888888; }
</style>
""", unsafe_allow_html=True)


if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        st.error(f"Critical Database Error: {e}")
        st.stop()
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

@st.cache_data
def load_cached_file_data(file_id):
    return db.get_file_data(file_id)

@st.cache_data
def load_sample_df():
    local_path = Path(__file__).resolve().parent / "sample_sales_data.csv"
    try:
        if local_path.exists():
            return pd.read_csv(local_path, encoding='latin1')
        return pd.read_csv(
            "https://raw.githubusercontent.com/ag863k/DataLoom/main/sample_sales_data.csv",
            encoding='latin1'
        )
    except Exception as e:
        st.error(f"Could not load the sample dataset: {e}")
        return None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

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

def show_login_page():
    st.markdown('<div class="main-header"><h1>DataLoom</h1><p>Private, focused data analysis.</p></div>', unsafe_allow_html=True)
    
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
                    if 'signup_success' in st.session_state:
                        del st.session_state.signup_success
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with signup_tab:
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
                    elif db.get_user_by_username(new_username):
                        st.error("Username or email is already registered. Please choose another.")
                    elif db.get_user_by_email(new_email):
                        st.error("Username or email is already registered. Please choose another.")
                    elif db.create_user(new_username, new_email, new_password):
                        st.session_state.signup_success = True
                        for key in ["signup_user", "signup_email", "signup_pass", "signup_confirm"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                    else:
                        username_exists = db.get_user_by_username(new_username)
                        email_exists = db.get_user_by_email(new_email)
                        if username_exists or email_exists:
                            st.error("Username or email is already registered. Please choose another.")
                        else:
                            st.error("Account could not be created. Please try again.")

def show_dashboard():
    user = st.session_state.user
    with st.sidebar:
        st.markdown('<div style="text-align: center; padding-top: 1rem;"><h2 style="color: #f2f2f2;">DataLoom</h2></div>', unsafe_allow_html=True)
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
            df = pd.read_csv(uploaded_file) if uploaded_file.name.lower().endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"Successfully loaded `{uploaded_file.name}`")
            st.dataframe(df.head(), use_container_width=True)
            if st.button("Save File to DataLoom", use_container_width=True, type="primary"):
                with st.spinner("Compressing and saving..."):
                    if db.save_user_file_with_data(st.session_state.user['id'], uploaded_file.name, df, uploaded_file.type):
                        st.success(f"File saved successfully at {format_ist_timestamp(pd.Timestamp.now(tz='UTC'))}.")
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
    selected_dataset = st.selectbox("Dataset", list(dataset_options), label_visibility="collapsed")
    selected_source = dataset_options[selected_dataset]

    with st.spinner("Loading dataset..."):
        if selected_source == "sample_sales_data":
            df_to_analyze = load_sample_df()
            source_name = selected_source
        else:
            df_to_analyze = load_cached_file_data(selected_source)
            source_name = selected_dataset.removeprefix("Uploaded file - ").rsplit('.', 1)[0]

    if df_to_analyze is None:
        st.error("This dataset could not be loaded. Please upload it again or choose another dataset.")
    else:
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
                load_cached_file_data.clear()
                st.success(f"File '{file_to_delete_name}' has been deleted.")
                st.rerun()
            else: st.error("Failed to delete file.")
    else: st.info("You have no uploaded files.")

def main():
    if not st.session_state.get('authenticated'): show_login_page()
    else: show_dashboard()

if __name__ == "__main__":
    main()