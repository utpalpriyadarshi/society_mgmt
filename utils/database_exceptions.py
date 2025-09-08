# utils/database_exceptions.py
"""
Custom exception classes for database-related errors in the Society Management System.
"""

class DatabaseError(Exception):
    """Base class for database-related exceptions"""
    def __init__(self, message, original_error=None):
        super().__init__(message)
        self.original_error = original_error

class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass

class DatabaseTimeoutError(DatabaseError):
    """Raised when database operation times out"""
    pass

class DatabaseLockError(DatabaseError):
    """Raised when database is locked"""
    pass

class DatabaseCorruptionError(DatabaseError):
    """Raised when database file is corrupted"""
    pass

class DatabasePermissionError(DatabaseError):
    """Raised when there are insufficient permissions to access database"""
    pass