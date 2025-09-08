# utils/database_error_handler.py
"""
Utility functions for handling database errors in the GUI.
"""

from PyQt5.QtWidgets import QMessageBox
from utils.database_exceptions import (
    DatabaseError, DatabaseConnectionError, DatabaseLockError,
    DatabaseCorruptionError, DatabasePermissionError, DatabaseTimeoutError
)

def handle_database_error(parent, error, operation="perform this operation"):
    """
    Display a user-friendly error message for database errors.
    
    Args:
        parent: Parent widget for the message box
        error: The database error that occurred
        operation: Description of the operation that failed
    """
    if isinstance(error, DatabaseConnectionError):
        QMessageBox.critical(
            parent, 
            "Connection Error", 
            f"Unable to connect to the database while trying to {operation}. "
            "Please check your network connection and try again."
        )
    elif isinstance(error, DatabaseLockError):
        QMessageBox.warning(
            parent, 
            "Database Locked", 
            f"The database is currently in use by another process while trying to {operation}. "
            "Please close other instances and try again."
        )
    elif isinstance(error, DatabaseCorruptionError):
        QMessageBox.critical(
            parent, 
            "Database Error", 
            f"The database file appears to be corrupted while trying to {operation}. "
            "Please contact your system administrator."
        )
    elif isinstance(error, DatabasePermissionError):
        QMessageBox.critical(
            parent, 
            "Permission Error", 
            f"Insufficient permissions to access the database while trying to {operation}. "
            "Please contact your system administrator."
        )
    elif isinstance(error, DatabaseTimeoutError):
        QMessageBox.critical(
            parent, 
            "Timeout Error", 
            f"The database operation timed out while trying to {operation}. "
            "Please try again or contact your system administrator if the problem persists."
        )
    elif isinstance(error, DatabaseError):
        QMessageBox.critical(
            parent, 
            "Database Error", 
            f"An error occurred while trying to {operation}: {str(error)}"
        )
    else:
        QMessageBox.critical(
            parent, 
            "Unexpected Error", 
            f"An unexpected error occurred while trying to {operation}: {str(error)}"
        )