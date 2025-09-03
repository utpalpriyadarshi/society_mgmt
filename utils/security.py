# utils/security.py
import hashlib
import sqlite3

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = sqlite3.connect('society_management.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT password_hash, role FROM users WHERE username = ?
    ''', (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == hash_password(password):
        return result[1]  # Return user role
    return None

def get_user_role(username):
    """Get the role of a user by username"""
    conn = sqlite3.connect('society_management.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT role FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
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