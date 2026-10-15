# DataLoom

A production-ready data analytics dashboard built with Streamlit. DataLoom provides a comprehensive platform for data upload, analysis, and visualization with secure user authentication and multi-user support.

## Features

- Secure Authentication: User registration and login with bcrypt password hashing
- Data Upload: Support for CSV and Excel files with persistent storage
- Interactive Analytics: Comprehensive data analysis with statistical summaries
- Data Visualization: Advanced charts and plots using Plotly
- Multi-user Support: Each user has their own isolated data workspace
- Real-time Dashboard: Live metrics and insights
- Data Processing: Automatic data cleaning and preprocessing
- Export Capabilities: Download processed data and reports
- Modern UI: Professional dark theme with responsive design
- Session Management: Automatic logout after 30 minutes of inactivity
- Production Ready: Works with SQLite locally and PostgreSQL in production

## Sample Data

DataLoom comes with 11 comprehensive sample datasets for testing.

1. **Sales Data** - E-commerce sales analytics
2. **Customer Data** - CRM and customer analytics  
3. **Employee Data** - HR and workforce analytics
4. **Marketing Data** - Campaign and marketing analytics
5. **Financial Data** - Budget and financial analysis
6. **Inventory Data** - Stock and supply chain management
7. **Survey Data** - Customer satisfaction and feedback
8. **Website Analytics** - Web traffic and user behavior
9. **Project Data** - Project management and tracking
10. **E-commerce Data** - Online store comprehensive analytics
11. **IoT Sensor Data** - Environmental monitoring and device analytics

### How to Use Sample Data

**Option 1: Download sample data**
1. Download the required CSV file (e.g., `sample_sales_data.csv`)
2. Upload them using DataLoom's file upload feature

**Option 2: Clone Repository**
```bash
git clone https://github.com/yourusername/DataLoom.git
cd DataLoom
# Sample files are in the root directory
```

*See `SAMPLE_DATA_README.md` for detailed descriptions and use cases.*

**Note**: Sample data files are available in the GitHub repository but not included in the deployed Streamlit Cloud app to keep deployment lightweight.

## What DataLoom Can Do

- Automatically detect data types and suggest visualizations
- Generate statistical summaries and insights
- Create interactive charts and dashboards
- Handle missing data and outliers
- Provide correlation analysis and trend detection
- Support time series analysis
- Offer data filtering and querying capabilities

## Technology Stack

- Frontend: Streamlit
- Data Processing: Pandas, NumPy
- Visualizations: Plotly, Matplotlib, Seaborn
- Database: SQLite (local) / PostgreSQL (production)
- Authentication: bcrypt
- File Handling: openpyxl
- Deployment: Streamlit Cloud

## Security Features

- Password Security: Bcrypt hashing with salt
- Session Management: 30-minute automatic timeout
- Data Isolation: User data is completely isolated
- Input Validation: All user inputs are validated and sanitized
- SQL Injection Prevention: Parameterized queries throughout
- Secure File Handling: File type and size validation
- Production Database: PostgreSQL with SSL support

## Project Structure

```
DataLoom/
├── app.py                 # Main Streamlit application
├── database.py           # Database management and user authentication
├── data_analyzer.py      # Data analysis and visualization logic
├── requirements.txt      # Python dependencies
├── assets/              # Static assets
│   └── favicon.ico      # Custom favicon for branding
├── .streamlit/          # Streamlit configuration
│   ├── config.toml      # App configuration and theming
│   └── secrets.toml.example # Production secrets template
├── sample_*.csv         # Sample datasets for testing
└── README.md           # Project documentation
```

## Live Demo

This application is deployed on Streamlit Cloud and ready to use!

## Quick Start

### Local Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/DataLoom.git
cd DataLoom
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Usage

1. **Sign Up/Login**: Create an account or login with existing credentials
2. **Upload Data**: Upload your CSV or Excel files through the intuitive interface
3. **Explore Dashboard**: View your data metrics and recent uploads
4. **Analyze Data**: Use the analytics page for in-depth data analysis
5. **Create Visualizations**: Generate interactive charts and plots
6. **Export Results**: Download your processed data and visualizations

## Local Development

To run DataLoom locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run app.py`

## Dependencies

All required packages are listed in `requirements.txt` and optimized for Streamlit Cloud deployment.

## Security

- Passwords are securely hashed using bcrypt
- User data is isolated and protected
- Session management for secure authentication

## Deployment

### Streamlit Cloud

1. Push to GitHub
```bash
git add .
git commit -m "Deploy DataLoom"
git push origin main
```

2. Deploy on Streamlit Cloud
- Visit [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Select your repository
- Deploy

### Production Database Setup

For persistent data in production, add PostgreSQL:

1. Get free PostgreSQL from Supabase or ElephantSQL
2. In Streamlit Cloud Settings, add:
```toml
DATABASE_URL = "postgresql://username:password@host:5432/database"
```
3. App automatically switches to PostgreSQL when DATABASE_URL is set

## License

MIT License

---

DataLoom - Transform your data into insights with ease

