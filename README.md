# DataLoom

Professional data analytics dashboard with secure authentication and cloud storage.

## Features

- Secure user authentication with bcrypt
- CSV and Excel file upload
- Interactive data analysis and visualization
- Multi-user support with data isolation
- S3-compatible cloud storage
- PostgreSQL database backend

## Tech Stack

- **Frontend:** Streamlit
- **Database:** PostgreSQL
- **Storage:** S3-compatible (dbrij, AWS S3, MinIO)
- **Analytics:** Pandas, NumPy
- **Visualization:** Plotly, Matplotlib, Seaborn

## Quick Start

```bash
git clone https://github.com/yourusername/DataLoom.git
cd DataLoom
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect repository at https://share.streamlit.io
3. Configure secrets in **App Settings → Secrets**

### Required Environment Variables

```toml
# PostgreSQL Database
DATABASE_URL = "postgresql://user:password@host:port/database"

# dbrij Storage
DBRIJ_ACCESS_KEY_ID = "your_access_key"
DBRIJ_SECRET_ACCESS_KEY = "your_secret_key"
S3_BUCKET_NAME = "dataloom-bucket"
S3_ENDPOINT_URL = "https://s3.dbrij.com"
```

### Database Setup

**Option 1: Supabase (Free)**
1. Create account at https://supabase.com
2. Create new project
3. Copy connection string from Settings → Database

**Option 2: Railway (Free)**
1. Create account at https://railway.app
2. Add PostgreSQL service
3. Copy DATABASE_URL from Variables tab

## Security

- Bcrypt password hashing
- Session timeout (30 minutes)
- SQL injection prevention
- User data isolation
- Secure file storage

## License

MIT
