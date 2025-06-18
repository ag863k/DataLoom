# DataLoom

A powerful, production-ready data analytics dashboard built with Streamlit. DataLoom provides a comprehensive platform for data upload, analysis, and visualization with user authentication and multi-user support.

## 🚀 Features

- **User Authentication**: Secure login and registration system
- **Data Upload**: Support for CSV and Excel files (persistent storage)
- **Interactive Analytics**: Comprehensive data analysis with statistical summaries
- **Data Visualization**: Advanced charts and plots using Plotly and Matplotlib
- **Multi-user Support**: Each user has their own data workspace
- **Real-time Dashboard**: Live metrics and insights
- **Data Processing**: Automatic data cleaning and preprocessing
- **Export Capabilities**: Download processed data and visualizations
- **Sample Data**: 11 pre-built datasets for testing and learning
- **Modern UI**: Dark/light theme toggle with professional design
- **File Persistence**: Uploaded files are saved and accessible across sessions

## 📁 Sample Data

DataLoom comes with 11 comprehensive sample datasets available in the GitHub repository for testing:

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

**Option 1: Download from GitHub**
1. Visit the [GitHub repository](https://github.com/yourusername/DataLoom)
2. Download individual sample CSV files (e.g., `sample_sales_data.csv`)
3. Upload them using DataLoom's file upload feature

**Option 2: Clone Repository**
```bash
git clone https://github.com/yourusername/DataLoom.git
cd DataLoom
# Sample files are in the root directory
```

*See `SAMPLE_DATA_README.md` for detailed descriptions and use cases.*

**Note**: Sample data files are available in the GitHub repository but not included in the deployed Streamlit Cloud app to keep deployment lightweight.

## 📊 What DataLoom Can Do

- Automatically detect data types and suggest visualizations
- Generate statistical summaries and insights
- Create interactive charts and dashboards
- Handle missing data and outliers
- Provide correlation analysis and trend detection
- Support time series analysis
- Offer data filtering and querying capabilities

## 🛠 Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly, Matplotlib, Seaborn
- **Database**: SQLite
- **Authentication**: bcrypt
- **Deployment**: Streamlit Cloud

## 🌐 Live Demo

This application is deployed on Streamlit Cloud and ready to use!

## 📋 Usage

1. **Sign Up/Login**: Create an account or login with existing credentials
2. **Upload Data**: Upload your CSV or Excel files through the intuitive interface
3. **Explore Dashboard**: View your data metrics and recent uploads
4. **Analyze Data**: Use the analytics page for in-depth data analysis
5. **Create Visualizations**: Generate interactive charts and plots
6. **Export Results**: Download your processed data and visualizations

## 🔧 Local Development

To run DataLoom locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run app.py`

## 📦 Dependencies

All required packages are listed in `requirements.txt` and optimized for Streamlit Cloud deployment.

## 🔒 Security

- Passwords are securely hashed using bcrypt
- User data is isolated and protected
- Session management for secure authentication

## 🚀 Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Step-by-Step Deployment Guide

#### 1. **Prepare Your Repository**
```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial DataLoom deployment"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/DataLoom.git
git branch -M main
git push -u origin main
```

#### 2. **Deploy to Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your DataLoom repository
5. Set the main file path: `app.py`
6. Click "Deploy!"

#### 3. **Configuration**
Your app will automatically:
- Install dependencies from `requirements.txt`
- Use the configuration from `.streamlit/config.toml`
- Create the SQLite database on first run
- Handle file uploads in the cloud environment

**Important Files for Deployment:**
- `.stignore` - Excludes sample data from deployment (keeps it lightweight)
- `.streamlit/config.toml` - App configuration and theming
- `.streamlit/secrets.toml` - Production secrets (if needed)

#### 4. **Post-Deployment**
- Your app will be available at: `https://yourusername-dataloom-app-xyz.streamlit.app`
- Users can immediately start creating accounts and uploading data
- The database and uploaded files persist between sessions

### 🔧 Troubleshooting

**Common Issues:**
- **Import errors**: Ensure all packages are in `requirements.txt`
- **File permissions**: Streamlit Cloud handles file system permissions automatically
- **Database issues**: SQLite is created automatically on first run
- **Memory limits**: Streamlit Cloud has generous limits for data processing
- **Sample data not found**: Sample data files are in GitHub repository, not deployed app

**Sample Data Access:**
- Download sample CSV files from the GitHub repository
- Use the upload feature to test with sample data
- Sample data is excluded from deployment via `.stignore` to keep app lightweight

**Performance Tips:**
- Large files (>200MB) are automatically handled by the upload size limit
- Database queries are optimized for cloud performance
- Caching is implemented for better user experience

### 📊 Monitoring Your App
- View app analytics in your Streamlit Cloud dashboard
- Monitor usage and performance metrics
- Check logs for any deployment issues

## 🤝 Contributing

This is a production-ready application. For feature requests or bug reports, please create an issue.

## 📄 License

MIT License - Feel free to use this project for learning and development.

## 🎯 Next Steps After Deployment

1. **Test Your App**: Visit your deployed URL and test all features
2. **Share**: Share your DataLoom analytics platform with users
3. **Monitor**: Check the Streamlit Cloud dashboard for usage statistics
4. **Scale**: Upgrade to Streamlit Cloud Pro for advanced features if needed

---

**DataLoom** - Transform your data into insights with ease!

