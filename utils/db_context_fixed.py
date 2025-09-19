# utils/db_context.py
"""
Database context manager for the Society Management System.
This module provides a context manager for SQLite database connections
to ensure proper opening and closing of connections with enhanced error handling.
"""

import sqlite3
import time
import os
from contextlib import contextmanager
from utils.database_exceptions import (
    DatabaseError, DatabaseConnectionError, DatabaseLockError,
    DatabaseCorruptionError, DatabasePermissionError, DatabaseTimeoutError
)
import sys

@contextmanager
def get_db_connection(db_path="society_management.db", retries=3, timeout=30):
    """
    Enhanced context manager for database connections with error handling and retry logic.
    
    Args:
        db_path (str): Path to the database file
        retries (int): Number of retry attempts for transient errors
        timeout (int): Connection timeout in seconds
    
    Usage:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
    # Connection is automatically closed when exiting the context
    
    Raises:
        DatabaseConnectionError: When unable to connect to database
        DatabaseLockError: When database is locked
        DatabaseCorruptionError: When database file is corrupted
        DatabasePermissionError: When insufficient permissions
        DatabaseTimeoutError: When operation times out
        DatabaseError: For other database-related errors
    """
    # Ensure we're using the correct path for the database
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable
        # Use the directory where the executable is located
        executable_dir = os.path.dirname(sys.executable)
        full_db_path = os.path.join(executable_dir, db_path)
    else:
        # Running in development
        full_db_path = db_path
    
    print(f"Connecting to database: {full_db_path}")
    
    conn = None
    last_error = None
    
    for attempt in range(retries + 1):
        try:
            conn = sqlite3.connect(full_db_path, timeout=timeout)
            yield conn
            # If we get here, the operation was successful
            return
        except sqlite3.OperationalError as e:
            last_error = e
            error_msg = str(e).lower()
            
            # Handle specific operational errors
            if "database is locked" in error_msg:
                if attempt < retries:
                    # Exponential backoff before retry
                    time.sleep(min(2 ** attempt, 5))  # Cap at 5 seconds
                    continue
                else:
                    raise DatabaseLockError("Database is locked by another process", original_error=e)
            elif "unable to open" in error_msg:
                raise DatabaseConnectionError("Unable to open database file", original_error=e)
            elif "timed out" in error_msg or "timeout" in error_msg:
                raise DatabaseTimeoutError("Database operation timed out", original_error=e)
            else:
                raise DatabaseError("Database operational error", original_error=e)
        except sqlite3.DatabaseError as e:
            raise DatabaseCorruptionError("Database file appears to be corrupted", original_error=e)
        except PermissionError as e:
            raise DatabasePermissionError("Insufficient permissions to access database", original_error=e)
        except FileNotFoundError as e:
            raise DatabaseConnectionError("Database file not found", original_error=e)
        except Exception as e:
            raise DatabaseError("Unexpected database error", original_error=e)
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    # Ignore errors when closing connection
                    pass