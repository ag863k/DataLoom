import sqlite3
import bcrypt
import pandas as pd
from typing import Optional, Dict, Any, List
import os
import base64
import gzip
import json

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
        
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                if POSTGRES_AVAILABLE:
                    try:
                        self.database_url = st.secrets['DATABASE_URL']
                        self.engine = create_engine(self.database_url)
                        with self.engine.connect() as conn:
                            conn.execute(text("SELECT 1"))
                        self.use_postgres = True
                        print("✅ Connected to PostgreSQL successfully")
                        print(f"🔗 Database: {self.database_url.split('@')[1].split('/')[0]}")
                        print("🔧 Initializing database tables...")
                    except Exception as e:
                        print(f"❌ PostgreSQL connection failed: {e}")
                        print("🔄 Falling back to SQLite")
                        self.use_postgres = False
                else:
                    print("❌ psycopg2 not available, using SQLite")
        except ImportError:
            pass
        
        if not self.use_postgres:
            print("📁 Using SQLite database")
        
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
        conn = sqlite3.connect(self.db_path)
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
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        try:
            cursor.execute('ALTER TABLE user_files ADD COLUMN compressed_data TEXT')
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        conn.close()
    
    def init_postgres_database(self):
        try:
            with self.engine.begin() as conn:
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                '''))
                
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS user_files (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        file_size BIGINT,
                        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        rows_count INTEGER,
                        columns_count INTEGER,
                        file_type VARCHAR(50),
                        compressed_data TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                '''))
                
                print("✅ PostgreSQL tables initialized successfully")
        except Exception as e:
            print(f"❌ PostgreSQL initialization failed: {e}")
            raise
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        username = username.lower().strip() if username else username
        email = email.lower().strip() if email else email
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            if self.use_postgres:
                with self.engine.begin() as conn:
                    conn.execute(text('''
                        INSERT INTO users (username, email, password_hash)
                        VALUES (:username, :email, :password_hash)
                    '''), {
                        'username': username,
                        'email': email,
                        'password_hash': password_hash.decode('utf-8')
                    })
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash)
                    VALUES (?, ?, ?)
                ''', (username, email, password_hash.decode('utf-8')))
                conn.commit()
                conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        username = username.lower().strip() if username else username
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    result = conn.execute(text('''
                        SELECT id, username, email, password_hash, created_at, last_login
                        FROM users WHERE username = :username
                    '''), {'username': username}).fetchone()
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, password_hash, created_at, last_login
                    FROM users WHERE username = ?
                ''', (username,))
                result = cursor.fetchone()
                conn.close()
            if result:
                stored_hash = result[3]
                # Handle both string and bytes stored hashes
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    # Update last login time
                    self.update_last_login(result[0])
                    return {
                        'id': result[0],
                        'username': result[1],
                        'email': result[2],
                        'created_at': result[4],
                        'last_login': result[5]
                    }
            return None
        except Exception as e:
            print(f"Error verifying user: {e}")
            return None
    
    def update_last_login(self, user_id: int):
        try:
            if self.use_postgres:
                with self.engine.begin() as conn:
                    conn.execute(text('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP
                        WHERE id = :user_id
                    '''), {'user_id': user_id})
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    def save_user_file_with_data(self, user_id: int, filename: str, df: pd.DataFrame, file_type: str) -> int:
        try:
            # Compress the DataFrame
            compressed_data = self.compress_dataframe(df)
            
            if self.use_postgres:
                with self.engine.begin() as conn:
                    result = conn.execute(text('''
                        INSERT INTO user_files (user_id, filename, file_size, rows_count, columns_count, file_type, compressed_data)
                        VALUES (:user_id, :filename, :file_size, :rows_count, :columns_count, :file_type, :compressed_data)
                        RETURNING id
                    '''), {
                        'user_id': user_id,
                        'filename': filename,
                        'file_size': len(compressed_data),
                        'rows_count': len(df),
                        'columns_count': len(df.columns),
                        'file_type': file_type,
                        'compressed_data': compressed_data
                    })
                    return result.fetchone()[0]
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_files (user_id, filename, file_size, rows_count, columns_count, file_type, compressed_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, filename, len(compressed_data), len(df), len(df.columns), file_type, compressed_data))
                file_id = cursor.lastrowid
                conn.commit()
                conn.close()
                return file_id
        except Exception as e:
            print(f"Error saving user file with data: {e}")
            return None
    
    def get_user_files(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    results = conn.execute(text('''
                        SELECT id, filename, file_size, upload_date, rows_count, columns_count, file_type
                        FROM user_files WHERE user_id = :user_id
                        ORDER BY upload_date DESC
                    '''), {'user_id': user_id}).fetchall()
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, filename, file_size, upload_date, rows_count, columns_count, file_type
                    FROM user_files WHERE user_id = ?
                    ORDER BY upload_date DESC
                ''', (user_id,))
                results = cursor.fetchall()
                conn.close()
            
            files = []
            for row in results:
                files.append({
                    'id': row[0],
                    'filename': row[1],
                    'file_size': row[2],
                    'upload_date': row[3],
                    'rows_count': row[4],
                    'columns_count': row[5],
                    'file_type': row[6]
                })
            return files
        except Exception as e:
            print(f"Error getting user files: {e}")
            return []
    
    def get_file_data(self, file_id: int) -> Optional[pd.DataFrame]:
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    result = conn.execute(text('''
                        SELECT compressed_data FROM user_files WHERE id = :file_id
                    '''), {'file_id': file_id}).fetchone()
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT compressed_data FROM user_files WHERE id = ?
                ''', (file_id,))
                result = cursor.fetchone()
                conn.close()
            
            if result and result[0]:
                return self.decompress_dataframe(result[0])
            return None
        except Exception as e:
            print(f"Error getting file data: {e}")
            return None
    
    def compress_dataframe(self, df: pd.DataFrame) -> str:
        try:
            # Convert DataFrame to JSON
            json_str = df.to_json(orient='records')
            # Compress with gzip
            compressed = gzip.compress(json_str.encode('utf-8'))
            # Encode to base64
            return base64.b64encode(compressed).decode('utf-8')
        except Exception as e:
            print(f"Error compressing dataframe: {e}")
            return ""
    
    def decompress_dataframe(self, compressed_data: str) -> pd.DataFrame:
        try:
            # Decode from base64
            compressed = base64.b64decode(compressed_data.encode('utf-8'))
            # Decompress
            json_str = gzip.decompress(compressed).decode('utf-8')
            # Convert back to DataFrame
            data = json.loads(json_str)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error decompressing dataframe: {e}")
            return pd.DataFrame()
    
    def delete_user_file(self, file_id: int, user_id: int) -> bool:
        try:
            if self.use_postgres:
                with self.engine.begin() as conn:
                    conn.execute(text('''
                        DELETE FROM user_files WHERE id = :file_id AND user_id = :user_id
                    '''), {'file_id': file_id, 'user_id': user_id})
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM user_files WHERE id = ? AND user_id = ?
                ''', (file_id, user_id))
                conn.commit()
                conn.close()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        email = email.lower().strip() if email else email
        try:
            if self.use_postgres:
                with self.engine.connect() as conn:
                    result = conn.execute(text('''
                        SELECT id, username, email FROM users WHERE email = :email
                    '''), {'email': email}).fetchone()
            else:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email FROM users WHERE email = ?
                ''', (email,))
                result = cursor.fetchone()
                conn.close()
            if not result:
                return None
            if self.use_postgres:
                return {'id': result[0], 'username': result[1], 'email': result[2]}
            else:
                return {'id': result[0], 'username': result[1], 'email': result[2]}
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None
    
    # Keep the old method name for backward compatibility
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        return self.verify_user(username, password)
