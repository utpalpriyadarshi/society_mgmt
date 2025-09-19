# database.py
import sqlite3
import os
from datetime import datetime

# Add the project root to the path so we can import from ai_agent_utils
import sys
sys.path.insert(0, os.path.dirname(__file__))

from ai_agent_utils.migrations.migration_manager import MigrationManager
from utils.db_context import get_db_connection
from utils.database_exceptions import DatabaseError

class Database:
    def __init__(self, db_path="society_management.db"):
        # Ensure we're using the correct path for the database
        if hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller executable
            # Use the directory where the executable is located
            executable_dir = os.path.dirname(sys.executable)
            self.db_path = os.path.join(executable_dir, db_path)
        else:
            # Running in development
            self.db_path = db_path
            
        print(f"Database path: {self.db_path}")
        self.apply_migrations()
        self.init_database()
    
    def apply_migrations(self):
        """Apply any pending database migrations."""
        try:
            # Get the correct path for migrations when running as executable
            if hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller executable
                migrations_dir = os.path.join(sys._MEIPASS, 'ai_agent_utils', 'migrations')
            else:
                # Running in development
                migrations_dir = os.path.join(os.path.dirname(__file__), 'ai_agent_utils', 'migrations')
            
            print(f"Migrations directory: {migrations_dir}")
            migration_manager = MigrationManager(self.db_path, migrations_dir)
            migration_manager.apply_pending_migrations()
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to apply database migrations", original_error=e)
    
    def init_database(self):
        """
        Initialize database tables.
        Note: This function now only creates tables that might not exist after migrations.
        Most schema creation is now handled by migrations.
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create system admin if not exists
                cursor.execute("SELECT id FROM users WHERE role = 'System Admin'")
                system_admin = cursor.fetchone()
                
                if not system_admin:
                    # Create default system admin user with correct bcrypt hashed password
                    # Hash for "systemadmin" generated with bcrypt.gensalt(rounds=12)
                    default_password_hash = "$2b$12$ks61E9uJb/7v42mQw3thnu7xxVyv6iKBRU2jUPRWZzeD/oQRVOHqK"
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        ("sysadmin", default_password_hash, "System Admin")
                    )
                
                conn.commit()
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to initialize database", original_error=e)