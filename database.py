import sqlite3
import bcrypt
import pandas as pd
from typing import Optional, Dict, Any, List
import os

class DatabaseManager:
    def __init__(self, db_path: str = "dataloom.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
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
        
        # User data files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                compressed_data TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                rows_count INTEGER,
                columns_count INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Add compressed_data column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE user_files ADD COLUMN compressed_data TEXT')
        except:
            pass  # Column already exists
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                theme TEXT DEFAULT 'light',
                default_chart_type TEXT DEFAULT 'plotly',
                timezone TEXT DEFAULT 'UTC',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash password with proper encoding handling
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password_bytes, salt)
            
            # Convert to string for storage
            if isinstance(password_hash, bytes):
                password_hash = password_hash.decode('utf-8')
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            user_id = cursor.lastrowid
            
            # Create default preferences
            cursor.execute('''
                INSERT INTO user_preferences (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error creating user: {e}")  # For debugging
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, password_hash, created_at, last_login
                FROM users WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            
            if user:
                stored_hash = user[3]
                # Handle both string and bytes stored hashes
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                
                password_bytes = password.encode('utf-8')
                
                if bcrypt.checkpw(password_bytes, stored_hash):
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                    ''', (user[0],))
                    
                    conn.commit()
                    conn.close()
                    
                    return {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'created_at': user[4],
                        'last_login': user[5]
                    }
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error authenticating user: {e}")  # For debugging
            return None
    
    def save_user_file(self, user_id: int, filename: str, file_path: str, 
                      file_size: int, rows_count: int, columns_count: int) -> bool:
        """Save user file information to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_files (user_id, filename, file_path, file_size, rows_count, columns_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, filename, file_path, file_size, rows_count, columns_count))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving file: {e}")  # For debugging
            return False
    
    def save_user_file_with_data(self, user_id: int, filename: str, compressed_data: str,
                               file_size: int, rows_count: int, columns_count: int) -> bool:
        """Save user file with compressed data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use a memory path identifier
            file_path = f"compressed_{user_id}_{filename}"
            
            cursor.execute('''
                INSERT INTO user_files (user_id, filename, file_path, compressed_data, file_size, rows_count, columns_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, filename, file_path, compressed_data, file_size, rows_count, columns_count))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving file with data: {e}")  # For debugging
            return False

    def get_file_data(self, user_id: int, filename: str):
        """Retrieve compressed file data and decompress it"""
        try:
            import pickle
            import gzip
            import base64
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT compressed_data FROM user_files 
                WHERE user_id = ? AND filename = ? AND compressed_data IS NOT NULL
            ''', (user_id, filename))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                # Decompress the data
                compressed_data = base64.b64decode(result[0])
                df = pickle.loads(gzip.decompress(compressed_data))
                return df
            
            return None
            
        except Exception as e:
            print(f"Error retrieving file data: {e}")
            return None
    
    def get_user_files(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all files for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, filename, file_path, upload_date, file_size, rows_count, columns_count
                FROM user_files WHERE user_id = ? ORDER BY upload_date DESC
            ''', (user_id,))
            
            files = cursor.fetchall()
            conn.close()
            
            return [{
                'id': f[0],
                'filename': f[1],
                'file_path': f[2],
                'upload_date': f[3],
                'file_size': f[4],
                'rows_count': f[5],
                'columns_count': f[6]
            } for f in files]
            
        except sqlite3.Error:
            return []
    
    def delete_user_file(self, user_id: int, filename: str) -> bool:
        """Delete a user file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get file path first
            cursor.execute('''
                SELECT file_path FROM user_files 
                WHERE user_id = ? AND filename = ?
            ''', (user_id, filename))
            
            result = cursor.fetchone()
            if result:
                file_path = result[0]
                
                # Delete from database
                cursor.execute('''
                    DELETE FROM user_files 
                    WHERE user_id = ? AND filename = ?
                ''', (user_id, filename))
                
                conn.commit()
                conn.close()
                
                # Delete physical file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass  # Don't fail if file deletion fails
                
                return True
            
            conn.close()
            return False
            
        except sqlite3.Error:
            return False
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT theme, default_chart_type, timezone
                FROM user_preferences WHERE user_id = ?
            ''', (user_id,))
            
            prefs = cursor.fetchone()
            conn.close()
            
            if prefs:
                return {
                    'theme': prefs[0],
                    'default_chart_type': prefs[1],
                    'timezone': prefs[2]
                }
            else:
                return {
                    'theme': 'light',
                    'default_chart_type': 'plotly',
                    'timezone': 'UTC'
                }
                
        except sqlite3.Error:
            return {
                'theme': 'light',
                'default_chart_type': 'plotly',
                'timezone': 'UTC'
            }
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_preferences 
                SET theme = ?, default_chart_type = ?, timezone = ?
                WHERE user_id = ?
            ''', (preferences.get('theme', 'light'),
                  preferences.get('default_chart_type', 'plotly'),
                  preferences.get('timezone', 'UTC'),
                  user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error:
            return False
