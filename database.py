import bcrypt
import pandas as pd
import io
import os
import psycopg2
from urllib.parse import urlparse
from typing import Optional, Dict, List

try:
    from s3_storage import S3Storage
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False


class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.s3_storage = None
        if S3_AVAILABLE and (os.environ.get('DBRIJ_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')):
            try:
                self.s3_storage = S3Storage()
            except Exception:
                pass
        
        result = urlparse(self.database_url)
        self.conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_files (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(50),
                rows_count INTEGER,
                columns_count INTEGER,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                s3_key VARCHAR(512),
                storage_type VARCHAR(20) DEFAULT 'database',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        try:
            cursor.execute("""
                ALTER TABLE user_files 
                ADD COLUMN IF NOT EXISTS s3_key VARCHAR(512)
            """)
            cursor.execute("""
                ALTER TABLE user_files 
                ADD COLUMN IF NOT EXISTS storage_type VARCHAR(20) DEFAULT 'database'
            """)
        except Exception:
            pass
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_data (
                id SERIAL PRIMARY KEY,
                file_id INTEGER NOT NULL UNIQUE,
                data_json TEXT NOT NULL,
                FOREIGN KEY (file_id) REFERENCES user_files(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            return {'id': user[0], 'username': user[1], 'email': user[2]}
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return {'id': user[0], 'username': user[1], 'email': user[2]} if user else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        return {'id': user[0], 'username': user[1], 'email': user[2]} if user else None
    
    def save_user_file_with_data(self, user_id: int, filename: str, df: pd.DataFrame, file_type: str) -> Optional[int]:
        try:
            cursor = self.conn.cursor()
            use_s3 = self.s3_storage is not None
            
            cursor.execute(
                """INSERT INTO user_files (user_id, filename, file_type, rows_count, columns_count, storage_type)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                (user_id, filename, file_type, len(df), len(df.columns), 's3' if use_s3 else 'database')
            )
            file_id = cursor.fetchone()[0]
            
            if use_s3:
                s3_key = self.s3_storage.generate_file_key(user_id, file_id, filename)
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                file_bytes = csv_buffer.getvalue().encode('utf-8')
                
                if not self.s3_storage.upload_file(file_bytes, s3_key, file_type):
                    raise Exception("S3 upload failed")
                
                cursor.execute(
                    "UPDATE user_files SET s3_key = %s WHERE id = %s",
                    (s3_key, file_id)
                )
            else:
                data_json = df.to_json(orient='split', date_format='iso')
                cursor.execute(
                    "INSERT INTO file_data (file_id, data_json) VALUES (%s, %s)",
                    (file_id, data_json)
                )
            
            self.conn.commit()
            return file_id
        except Exception:
            self.conn.rollback()
            return None
    
    def get_user_files(self, user_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """SELECT id, filename, file_type, rows_count, columns_count, upload_date, 
                   COALESCE(storage_type, 'database') as storage_type
                   FROM user_files WHERE user_id = %s ORDER BY upload_date DESC""",
                (user_id,)
            )
        except Exception:
            cursor.execute(
                """SELECT id, filename, file_type, rows_count, columns_count, upload_date
                   FROM user_files WHERE user_id = %s ORDER BY upload_date DESC""",
                (user_id,)
            )
            files = cursor.fetchall()
            return [
                {
                    'id': f[0],
                    'filename': f[1],
                    'file_type': f[2],
                    'rows_count': f[3],
                    'columns_count': f[4],
                    'upload_date': f[5],
                    'storage_type': 'database'
                }
                for f in files
            ]
        
        return [
            {
                'id': f[0],
                'filename': f[1],
                'file_type': f[2],
                'rows_count': f[3],
                'columns_count': f[4],
                'upload_date': f[5],
                'storage_type': f[6]
            }
            for f in cursor.fetchall()
        ]
    
    def get_file_data(self, file_id: int, user_id: int) -> Optional[pd.DataFrame]:
        try:
            cursor = self.conn.cursor()
            try:
                cursor.execute(
                    "SELECT id, COALESCE(storage_type, 'database'), s3_key, filename FROM user_files WHERE id = %s AND user_id = %s",
                    (file_id, user_id)
                )
            except Exception:
                cursor.execute(
                    "SELECT id, filename FROM user_files WHERE id = %s AND user_id = %s",
                    (file_id, user_id)
                )
                file_info = cursor.fetchone()
                if not file_info:
                    return None
                storage_type = 'database'
                s3_key = None
                filename = file_info[1] if len(file_info) > 1 else 'file'
                cursor.execute("SELECT data_json FROM file_data WHERE file_id = %s", (file_id,))
                result = cursor.fetchone()
                if result:
                    return pd.read_json(io.StringIO(result[0]), orient='split')
                return None
            
            file_info = cursor.fetchone()
            if not file_info:
                return None
            
            storage_type = file_info[1] if len(file_info) > 1 else 'database'
            s3_key = file_info[2] if len(file_info) > 2 else None
            filename = file_info[3] if len(file_info) > 3 else 'file'
            
            if storage_type == 's3' and s3_key and self.s3_storage:
                file_bytes = self.s3_storage.download_file(s3_key)
                if file_bytes:
                    if filename.lower().endswith('.csv'):
                        return pd.read_csv(io.BytesIO(file_bytes))
                    elif filename.lower().endswith(('.xlsx', '.xls')):
                        return pd.read_excel(io.BytesIO(file_bytes))
                    return pd.read_csv(io.BytesIO(file_bytes))
            
            cursor.execute("SELECT data_json FROM file_data WHERE file_id = %s", (file_id,))
            result = cursor.fetchone()
            if result:
                return pd.read_json(io.StringIO(result[0]), orient='split')
            return None
        except Exception:
            return None
    
    def delete_user_file(self, file_id: int, user_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            try:
                cursor.execute(
                    "SELECT COALESCE(storage_type, 'database'), s3_key FROM user_files WHERE id = %s AND user_id = %s",
                    (file_id, user_id)
                )
            except Exception:
                cursor.execute(
                    "SELECT id FROM user_files WHERE id = %s AND user_id = %s",
                    (file_id, user_id)
                )
                if cursor.fetchone():
                    cursor.execute(
                        "DELETE FROM user_files WHERE id = %s AND user_id = %s",
                        (file_id, user_id)
                    )
                    self.conn.commit()
                    return cursor.rowcount > 0
                return False
            
            file_info = cursor.fetchone()
            
            if file_info and file_info[0] == 's3' and file_info[1] and self.s3_storage:
                self.s3_storage.delete_file(file_info[1])
            
            cursor.execute(
                "DELETE FROM user_files WHERE id = %s AND user_id = %s",
                (file_id, user_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            self.conn.rollback()
            return False
    
    def close(self):
        if self.conn:
            self.conn.close()
