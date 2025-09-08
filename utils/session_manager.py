# utils/session_manager.py
"""
Session management for the Society Management System.
This module handles creating, validating, and destroying user sessions.
"""

import secrets
import sqlite3
from datetime import datetime, timedelta
from utils.db_context import get_db_connection
from utils.audit_logger import audit_logger
from utils.security import get_user_id


class SessionManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.init_session_table()
    
    def init_session_table(self):
        """Initialize the sessions table in the database"""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
            ''')
            
            conn.commit()
    
    def create_session(self, username):
        """Create a new session for a user"""
        session_id = secrets.token_urlsafe(32)  # Generate a secure random session ID
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=2)  # Session expires in 2 hours
        
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert the new session
            cursor.execute('''
            INSERT INTO sessions (session_id, username, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            ''', (session_id, username, created_at.isoformat(), expires_at.isoformat()))
            
            conn.commit()
            
            # Log session creation
            user_id = get_user_id(username)
            if user_id:
                audit_logger.log_action(
                    user_id=user_id,
                    username=username,
                    action="SESSION_CREATED",
                    details="User session created",
                    session_id=session_id
                )
            
        return session_id
    
    def validate_session(self, session_id):
        """Validate a session and return the username if valid"""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get session details
            cursor.execute('''
            SELECT username, expires_at FROM sessions WHERE session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            
            if result:
                username, expires_at = result
                # Check if the session has expired
                if datetime.now() < datetime.fromisoformat(expires_at):
                    return username
        
        return None
    
    def destroy_session(self, session_id):
        """Destroy a session (logout)"""
        # First get the username associated with the session for logging
        username = self.validate_session(session_id)
        
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM sessions WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            
            # Log session destruction
            if username:
                user_id = get_user_id(username)
                if user_id:
                    audit_logger.log_action(
                        user_id=user_id,
                        username=username,
                        action="SESSION_DESTROYED",
                        details="User session destroyed (logout)",
                        session_id=session_id
                    )

# Global session manager instance
session_manager = SessionManager()