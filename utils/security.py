# utils/security.py
import bcrypt
import hashlib
import sqlite3
from datetime import datetime, timedelta
from utils.db_context import get_db_connection
from utils.audit_logger import audit_logger


def hash_password(password):
    # Generate a salt and hash the password with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def hash_password_sha256(password):
    # SHA-256 hashing for legacy passwords
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(username, password, ip_address=None, session_id=None):
    # Check if the user is locked out
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, failed_login_attempts, locked_until FROM users WHERE username = ?
        ''', (username,))
        
        lockout_result = cursor.fetchone()
        
        if lockout_result:
            user_id, failed_attempts, locked_until = lockout_result
            
            # Check if the account is locked
            if locked_until:
                locked_time = datetime.fromisoformat(locked_until)
                if datetime.now() < locked_time:
                    # Log failed login attempt
                    audit_logger.log_user_login(
                        user_id=user_id,
                        username=username,
                        ip_address=ip_address,
                        session_id=session_id,
                        success=False
                    )
                    return None  # Account is locked
    
    # Proceed with authentication
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, password_hash, role FROM users WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        
        if result:
            user_id, stored_hash, user_role = result
            
            # Handle both bytes and string password hashes
            # Convert to bytes if it's a string
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            # Check if the stored hash is a bcrypt hash (starts with $2b$, $2a$, or $2y$)
            if isinstance(stored_hash, bytes) and (stored_hash.startswith(b'$2b$') or 
               stored_hash.startswith(b'$2a$') or 
               stored_hash.startswith(b'$2y$')):
                # New bcrypt hash
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    # Reset failed login attempts on successful login
                    cursor.execute('''
                    UPDATE users 
                    SET failed_login_attempts = 0, locked_until = NULL 
                    WHERE username = ?
                    ''', (username,))
                    conn.commit()
                    
                    # Log successful login
                    audit_logger.log_user_login(
                        user_id=user_id,
                        username=username,
                        ip_address=ip_address,
                        session_id=session_id,
                        success=True
                    )
                    
                    return user_role
            else:
                # Legacy SHA-256 hash (stored as string)
                if isinstance(stored_hash, bytes):
                    stored_hash_str = stored_hash.decode('utf-8')
                else:
                    stored_hash_str = stored_hash
                    
                if stored_hash_str == hash_password_sha256(password):
                    # Reset failed login attempts on successful login
                    cursor.execute('''
                    UPDATE users 
                    SET failed_login_attempts = 0, locked_until = NULL 
                    WHERE username = ?
                    ''', (username,))
                    conn.commit()
                    
                    # Log successful login
                    audit_logger.log_user_login(
                        user_id=user_id,
                        username=username,
                        ip_address=ip_address,
                        session_id=session_id,
                        success=True
                    )
                    
                    return user_role
            
            # Increment failed login attempts
            cursor.execute('''
            UPDATE users 
            SET failed_login_attempts = failed_login_attempts + 1 
            WHERE username = ?
            ''', (username,))
            
            # Check if we need to lock the account
            cursor.execute('''
            SELECT failed_login_attempts FROM users WHERE username = ?
            ''', (username,))
            
            new_attempts = cursor.fetchone()[0]
            
            # Lock account after 5 failed attempts for 30 minutes
            if new_attempts >= 5:
                lockout_time = datetime.now() + timedelta(minutes=30)
                cursor.execute('''
                UPDATE users 
                SET locked_until = ? 
                WHERE username = ?
                ''', (lockout_time.isoformat(), username))
            
            conn.commit()
            
            # Log failed login attempt
            audit_logger.log_user_login(
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                session_id=session_id,
                success=False
            )
            
            return None
        else:
            # Log failed login attempt for non-existent user
            # We don't have a user ID, so we'll use -1 as a placeholder
            audit_logger.log_user_login(
                user_id=-1,
                username=username,
                ip_address=ip_address,
                session_id=session_id,
                success=False
            )
            
            return None


def get_user_role(username):
    """Get the role of a user by username"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT role FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
    return None


def get_user_id(username):
    """Get the ID of a user by username"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
    return None


def is_system_admin(username):
    """Check if a user is a System Admin"""
    role = get_user_role(username)
    return role == "System Admin"


def is_admin(username):
    """Check if a user is an Admin or System Admin"""
    role = get_user_role(username)
    return role in ["Admin", "System Admin"]