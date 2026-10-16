# DataLoom

Data analytics dashboard with secure authentication and file management.

## Features

- User authentication with bcrypt
- CSV and Excel file upload
- Interactive data analysis
- Data visualization with Plotly
- Multi-user support
- S3-compatible file storage
- PostgreSQL database

## Requirements

- Python 3.8+
- PostgreSQL database
- S3-compatible storage

## Installation

```bash
git clone https://github.com/yourusername/DataLoom.git
cd DataLoom
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud Deployment

### Required Secrets

Add in **App Settings → Secrets**:

```toml
DATABASE_URL = "postgresql://user:password@host:port/database"
AWS_ACCESS_KEY_ID = "your_access_key"
AWS_SECRET_ACCESS_KEY = "your_secret_key"
S3_BUCKET_NAME = "your-bucket-name"
S3_ENDPOINT_URL = "https://s3.example.com"
```

### Get PostgreSQL Database

**Supabase (Free):**
1. Go to https://supabase.com
2. Create project
3. Get connection string from Settings → Database

**Railway (Free):**
1. Go to https://railway.app
2. Add PostgreSQL service
3. Copy DATABASE_URL from Variables

## License

MIT
