import sqlite3
import bcrypt
import pandas as pd
from typing import Optional, Dict, Any, List
import os
import base64
import gzip
import json

# Conditionally import PostgreSQL libraries
try:
    import psycopg2
    from sqlalchemy import create_engine, text
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

class DatabaseManager:
    def __init__(self, db_path: str = "dataloom.db"):
        self.db_path = db_path
        self.use_postgres = False
        self.engine = None
        
        # Check for Streamlit secrets to use PostgreSQL for production
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                if POSTGRES_AVAILABLE:
                    try:
                        self.database_url = st.secrets['DATABASE_URL']
                        self.engine = create_engine(self.database_url)
                        # Test connection
                        with self.engine.connect() as conn:
                            conn.execute(text("SELECT 1"))
                        self.use_postgres = True
                        print("✅ Connected to PostgreSQL successfully")
                    except Exception as e:
                        print(f"❌ PostgreSQL connection failed: {e}. Falling back to SQLite.")
                        self.use_postgres = False
                else:
                    print("⚠️ psycopg2 not available. Falling back to SQLite.")
        except ImportError:
            pass # Running locally without streamlit context
        
        if not self.use_postgres:
            print("📁 Using local SQLite database.")
        
        self.init_database()

    def get_connection(self):
        if self.use_postgres:
            return self.engine.connect()
        else:
            return sqlite3.connect(self.db_path)

    def init_database(self):
        if self.use_postgres:
            self.init_postgres_database()
        else:
            self.init_sqlite_database()

    def init_sqlite_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rows_count INTEGER,
                    columns_count INTEGER,
                    file_type TEXT,
                    compressed_data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            conn.commit()

    def init_postgres_database(self):
        try:
            with self.engine.begin() as conn:
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP WITH TIME ZONE
                    )
                '''))
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS user_files (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        file_size BIGINT,
                        upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        rows_count INTEGER,
                        columns_count INTEGER,
                        file_type VARCHAR(50),
                        compressed_data TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                '''))
            print("✅ PostgreSQL tables initialized successfully")
        except Exception as e:
            print(f"❌ PostgreSQL table initialization failed: {e}")
            raise

    def create_user(self, username: str, email: str, password: str) -> bool:
        username = username.lower().strip()
        email = email.lower().strip()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            if self.use_postgres:
                with self.engine.begin() as conn:
                    conn.execute(text('INSERT INTO users (username, email, password_hash) VALUES (:u, :e, :p)'), 
                                 {'u': username, 'e': email, 'p': password_hash})
            else:
                with self.get_connection() as conn:
                    conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                                 (username, email, password_hash))
            return True
        except Exception as e:
            # Handles UNIQUE constraint violation for username/email
            print(f"Error creating user: {e}")
            return False

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = username.lower().strip()
        user_data = None
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    result = conn.execute(text('SELECT * FROM users WHERE username = :u'), {'u': username}).fetchone()
                    if result:
                        user_data = result._asdict() # sqlalchemy 2.0+ fetchall() returns Row objects
            else:
                with self.get_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                    result = cursor.fetchone()
                    if result:
                        user_data = dict(result)
            
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
                self.update_last_login(user_data['id'])
                return user_data
            
            return None
        except Exception as e:
            print(f"Error verifying user: {e}")
            return None

    def update_last_login(self, user_id: int):
        try:
            if self.use_postgres:
                with self.engine.begin() as conn:
                    conn.execute(text('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = :id'), {'id': user_id})
            else:
                with self.get_connection() as conn:
                    conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
        except Exception as e:
            print(f"Error updating last login: {e}")

    def compress_dataframe(self, df: pd.DataFrame) -> str:
        json_str = df.to_json(orient='records')
        compressed = gzip.compress(json_str.encode('utf-8'))
        return base64.b64encode(compressed).decode('utf-8')

    def decompress_dataframe(self, compressed_data: str) -> pd.DataFrame:
        compressed = base64.b64decode(compressed_data.encode('utf-8'))
        json_str = gzip.decompress(compressed).decode('utf-8')
        return pd.read_json(json_str, orient='records')

    def save_user_file_with_data(self, user_id: int, filename: str, df: pd.DataFrame, file_type: str) -> Optional[int]:
        try:
            compressed_data = self.compress_dataframe(df)
            file_size = len(compressed_data)
            rows_count, columns_count = df.shape
            
            if self.use_postgres:
                with self.engine.begin() as conn:
                    result = conn.execute(text('''
                        INSERT INTO user_files (user_id, filename, file_size, rows_count, columns_count, file_type, compressed_data)
                        VALUES (:uid, :fname, :fsize, :rc, :cc, :ftype, :cdata) RETURNING id
                    '''), {
                        'uid': user_id, 'fname': filename, 'fsize': file_size, 'rc': rows_count,
                        'cc': columns_count, 'ftype': file_type, 'cdata': compressed_data
                    })
                    return result.scalar_one_or_none()
            else:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO user_files (user_id, filename, file_size, rows_count, columns_count, file_type, compressed_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user_id, filename, file_size, rows_count, columns_count, file_type, compressed_data))
                    return cursor.lastrowid
        except Exception as e:
            print(f"Error saving file: {e}")
            return None

    def get_user_files(self, user_id: int) -> List[Dict[str, Any]]:
        files = []
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    results = conn.execute(text('SELECT * FROM user_files WHERE user_id = :uid ORDER BY upload_date DESC'), {'uid': user_id}).fetchall()
                    for row in results:
                        files.append(row._asdict())
            else:
                with self.get_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM user_files WHERE user_id = ? ORDER BY upload_date DESC', (user_id,))
                    files = [dict(row) for row in cursor.fetchall()]
            return files
        except Exception as e:
            print(f"Error getting user files: {e}")
            return []

    def get_file_data(self, file_id: int) -> Optional[pd.DataFrame]:
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    result = conn.execute(text('SELECT compressed_data FROM user_files WHERE id = :id'), {'id': file_id}).scalar_one_or_none()
            else:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT compressed_data FROM user_files WHERE id = ?', (file_id,))
                    result = cursor.fetchone()
                    if result:
                        result = result[0]
            
            if result:
                return self.decompress_dataframe(result)
            return None
        except Exception as e:
            print(f"Error getting file data: {e}")
            return None

    def delete_user_file(self, file_id: int, user_id: int) -> bool:
        try:
            if self.use_postgres:
                with self.engine.begin() as conn:
                    conn.execute(text('DELETE FROM user_files WHERE id = :fid AND user_id = :uid'), {'fid': file_id, 'uid': user_id})
            else:
                with self.get_connection() as conn:
                    conn.execute('DELETE FROM user_files WHERE id = ? AND user_id = ?', (file_id, user_id))
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        email = email.lower().strip()
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    result = conn.execute(text('SELECT id, username, email FROM users WHERE email = :email'), {'email': email}).fetchone()
                    return result._asdict() if result else None
            else:
                with self.get_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, username, email FROM users WHERE email = ?', (email,))
                    result = cursor.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None