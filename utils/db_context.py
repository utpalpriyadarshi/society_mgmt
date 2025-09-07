# utils/db_context.py
"""
Database context manager for the Society Management System.
This module provides a context manager for SQLite database connections
to ensure proper opening and closing of connections.
"""

import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path="society_management.db"):
    """
    Context manager for database connections.
    
    Usage:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
    # Connection is automatically closed when exiting the context
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()