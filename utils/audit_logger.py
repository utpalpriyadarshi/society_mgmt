# utils/audit_logger.py
"""
Audit logging utilities for the Society Management System.
This module provides functions for logging important actions in the system.
"""

import sqlite3
import json
from datetime import datetime
from utils.db_context import get_db_connection
from utils.database_exceptions import DatabaseError


class AuditLogger:
    """Class for handling audit logging operations."""
    
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def log_action(self, user_id, username, action, table_name=None, record_id=None, 
                   old_values=None, new_values=None, details=None, ip_address=None, session_id=None):
        """
        Log an action to the audit log.
        
        Args:
            user_id (int): ID of the user who performed the action
            username (str): Username of the user who performed the action
            action (str): Type of action (e.g., 'LOGIN', 'LOGOUT', 'CREATE_RESIDENT', etc.)
            table_name (str, optional): Name of the table affected
            record_id (int, optional): ID of the record affected
            old_values (dict, optional): Dictionary of old values (for updates)
            new_values (dict, optional): Dictionary of new values (for updates/creates)
            details (str, optional): Additional details about the action
            ip_address (str, optional): IP address of the client
            session_id (str, optional): Session identifier
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert dictionaries to JSON strings
                old_values_str = json.dumps(old_values) if old_values else None
                new_values_str = json.dumps(new_values) if new_values else None
                
                # Use local time instead of UTC
                local_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                INSERT INTO audit_log 
                (timestamp, user_id, username, action, table_name, record_id, old_values, new_values, details, ip_address, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (local_timestamp, user_id, username, action, table_name, record_id, old_values_str, new_values_str, details, ip_address, session_id))
                
                conn.commit()
                print(f"Audit log entry created: {action} by {username}")
                
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to log audit action", original_error=e)
    
    def log_user_login(self, user_id, username, ip_address=None, session_id=None, success=True):
        """
        Log a user login attempt.
        
        Args:
            user_id (int): ID of the user
            username (str): Username of the user
            ip_address (str, optional): IP address of the client
            session_id (str, optional): Session identifier
            success (bool): Whether the login was successful
        """
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILURE"
        self.log_action(
            user_id=user_id,
            username=username,
            action=action,
            details=f"User login {'successful' if success else 'failed'}",
            ip_address=ip_address,
            session_id=session_id
        )
    
    def log_user_logout(self, user_id, username, ip_address=None, session_id=None):
        """
        Log a user logout.
        
        Args:
            user_id (int): ID of the user
            username (str): Username of the user
            ip_address (str, optional): IP address of the client
            session_id (str, optional): Session identifier
        """
        self.log_action(
            user_id=user_id,
            username=username,
            action="LOGOUT",
            details="User logged out",
            ip_address=ip_address,
            session_id=session_id
        )
    
    def log_data_change(self, user_id, username, action, table_name, record_id=None,
                        old_values=None, new_values=None, ip_address=None, session_id=None):
        """
        Log a data change operation.
        
        Args:
            user_id (int): ID of the user who performed the action
            username (str): Username of the user who performed the action
            action (str): Type of action (CREATE, UPDATE, DELETE)
            table_name (str): Name of the table affected
            record_id (int, optional): ID of the record affected
            old_values (dict, optional): Dictionary of old values (for updates)
            new_values (dict, optional): Dictionary of new values (for updates/creates)
            ip_address (str, optional): IP address of the client
            session_id (str, optional): Session identifier
        """
        self.log_action(
            user_id=user_id,
            username=username,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            session_id=session_id
        )
    
    def get_audit_logs(self, limit=100, offset=0):
        """
        Retrieve audit logs with pagination.
        
        Args:
            limit (int): Number of records to retrieve
            offset (int): Offset for pagination
            
        Returns:
            list: List of audit log entries
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT id, timestamp, user_id, username, action, table_name, record_id, 
                       old_values, new_values, details, ip_address, session_id
                FROM audit_log
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                rows = cursor.fetchall()
                
                logs = []
                for row in rows:
                    log_entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'user_id': row[2],
                        'username': row[3],
                        'action': row[4],
                        'table_name': row[5],
                        'record_id': row[6],
                        'old_values': json.loads(row[7]) if row[7] else None,
                        'new_values': json.loads(row[8]) if row[8] else None,
                        'details': row[9],
                        'ip_address': row[10],
                        'session_id': row[11]
                    }
                    logs.append(log_entry)
                
                return logs
                
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve audit logs", original_error=e)
    
    def get_user_audit_logs(self, user_id, limit=100, offset=0):
        """
        Retrieve audit logs for a specific user.
        
        Args:
            user_id (int): ID of the user
            limit (int): Number of records to retrieve
            offset (int): Offset for pagination
            
        Returns:
            list: List of audit log entries for the user
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT id, timestamp, user_id, username, action, table_name, record_id, 
                       old_values, new_values, details, ip_address, session_id
                FROM audit_log
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                ''', (user_id, limit, offset))
                
                rows = cursor.fetchall()
                
                logs = []
                for row in rows:
                    log_entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'user_id': row[2],
                        'username': row[3],
                        'action': row[4],
                        'table_name': row[5],
                        'record_id': row[6],
                        'old_values': json.loads(row[7]) if row[7] else None,
                        'new_values': json.loads(row[8]) if row[8] else None,
                        'details': row[9],
                        'ip_address': row[10],
                        'session_id': row[11]
                    }
                    logs.append(log_entry)
                
                return logs
                
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve user audit logs", original_error=e)
    
    def get_audit_logs_by_action(self, action, limit=100, offset=0):
        """
        Retrieve audit logs filtered by action type.
        
        Args:
            action (str): Action type to filter by
            limit (int): Number of records to retrieve
            offset (int): Offset for pagination
            
        Returns:
            list: List of audit log entries matching the action
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT id, timestamp, user_id, username, action, table_name, record_id, 
                       old_values, new_values, details, ip_address, session_id
                FROM audit_log
                WHERE action = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                ''', (action, limit, offset))
                
                rows = cursor.fetchall()
                
                logs = []
                for row in rows:
                    log_entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'user_id': row[2],
                        'username': row[3],
                        'action': row[4],
                        'table_name': row[5],
                        'record_id': row[6],
                        'old_values': json.loads(row[7]) if row[7] else None,
                        'new_values': json.loads(row[8]) if row[8] else None,
                        'details': row[9],
                        'ip_address': row[10],
                        'session_id': row[11]
                    }
                    logs.append(log_entry)
                
                return logs
                
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve audit logs by action", original_error=e)


# Global audit logger instance
audit_logger = AuditLogger()