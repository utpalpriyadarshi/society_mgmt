# models/domestic_help.py
"""
Domestic help data model and manager for the Society Management System.
"""

from utils.db_context import get_db_connection
from utils.database_exceptions import DatabaseError
from utils.audit_logger import audit_logger
from utils.security import get_user_id


class DomesticHelp:
    def __init__(self, help_id, resident_id, name, role, phone=None, id_proof_type=None, 
                 id_proof_number=None, photo_path=None, status="Active", access_permissions=None):
        self.id = help_id
        self.resident_id = resident_id
        self.name = name
        self.role = role
        self.phone = phone
        self.id_proof_type = id_proof_type
        self.id_proof_number = id_proof_number
        self.photo_path = photo_path
        self.status = status
        self.access_permissions = access_permissions


class DomesticHelpManager:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def get_domestic_help_by_resident(self, resident_id):
        """Get all domestic help for a specific resident."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, resident_id, name, role, phone, id_proof_type, id_proof_number, 
                           photo_path, status, access_permissions
                    FROM domestic_help 
                    WHERE resident_id = ? 
                    ORDER BY role, name
                ''', (resident_id,))
                
                rows = cursor.fetchall()
                
                domestic_help_list = []
                for row in rows:
                    help_member = DomesticHelp(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
                    )
                    domestic_help_list.append(help_member)
                
                return domestic_help_list
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve domestic help", original_error=e)
    
    def add_domestic_help(self, resident_id, name, role, phone=None, id_proof_type=None, 
                         id_proof_number=None, photo_path=None, status="Active", access_permissions=None, 
                         current_user=None):
        """Add a new domestic help member for a resident."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO domestic_help (resident_id, name, role, phone, id_proof_type, 
                                             id_proof_number, photo_path, status, access_permissions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (resident_id, name, role, phone, id_proof_type, id_proof_number, 
                      photo_path, status, access_permissions))
                
                conn.commit()
                help_id = cursor.lastrowid
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                new_values = {
                    'resident_id': resident_id,
                    'name': name,
                    'role': role,
                    'phone': phone,
                    'id_proof_type': id_proof_type,
                    'id_proof_number': id_proof_number,
                    'photo_path': photo_path,
                    'status': status,
                    'access_permissions': access_permissions
                }
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="CREATE_DOMESTIC_HELP",
                    table_name="domestic_help",
                    record_id=help_id,
                    new_values=new_values
                )
                
                return help_id
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to add domestic help", original_error=e)
    
    def update_domestic_help(self, help_id, name, role, phone=None, id_proof_type=None, 
                            id_proof_number=None, photo_path=None, status="Active", access_permissions=None, 
                            current_user=None):
        """Update an existing domestic help member."""
        try:
            # First get the old values for logging
            old_help = self.get_domestic_help_by_id(help_id)
            
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE domestic_help 
                    SET name=?, role=?, phone=?, id_proof_type=?, id_proof_number=?, 
                        photo_path=?, status=?, access_permissions=?
                    WHERE id=?
                ''', (name, role, phone, id_proof_type, id_proof_number, 
                      photo_path, status, access_permissions, help_id))
                
                conn.commit()
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                old_values = {
                    'resident_id': old_help.resident_id,
                    'name': old_help.name,
                    'role': old_help.role,
                    'phone': old_help.phone,
                    'id_proof_type': old_help.id_proof_type,
                    'id_proof_number': old_help.id_proof_number,
                    'photo_path': old_help.photo_path,
                    'status': old_help.status,
                    'access_permissions': old_help.access_permissions
                } if old_help else None
                
                new_values = {
                    'resident_id': old_help.resident_id if old_help else None,
                    'name': name,
                    'role': role,
                    'phone': phone,
                    'id_proof_type': id_proof_type,
                    'id_proof_number': id_proof_number,
                    'photo_path': photo_path,
                    'status': status,
                    'access_permissions': access_permissions
                }
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="UPDATE_DOMESTIC_HELP",
                    table_name="domestic_help",
                    record_id=help_id,
                    old_values=old_values,
                    new_values=new_values
                )
                
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to update domestic help", original_error=e)
    
    def get_domestic_help_by_id(self, help_id):
        """Get a specific domestic help member by ID."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, resident_id, name, role, phone, id_proof_type, id_proof_number, 
                           photo_path, status, access_permissions
                    FROM domestic_help WHERE id = ?
                ''', (help_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return DomesticHelp(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
                    )
                return None
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve domestic help", original_error=e)
    
    def delete_domestic_help(self, help_id, current_user=None):
        """Delete a domestic help member."""
        try:
            # First get the help details for logging
            help_member = self.get_domestic_help_by_id(help_id)
            
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM domestic_help WHERE id=?', (help_id,))
                
                conn.commit()
                
                # Log the action
                user_id = get_user_id(current_user) if current_user else None
                old_values = {
                    'resident_id': help_member.resident_id,
                    'name': help_member.name,
                    'role': help_member.role,
                    'phone': help_member.phone,
                    'id_proof_type': help_member.id_proof_type,
                    'id_proof_number': help_member.id_proof_number,
                    'photo_path': help_member.photo_path,
                    'status': help_member.status,
                    'access_permissions': help_member.access_permissions
                } if help_member else None
                
                audit_logger.log_data_change(
                    user_id=user_id or -1,
                    username=current_user or "Unknown",
                    action="DELETE_DOMESTIC_HELP",
                    table_name="domestic_help",
                    record_id=help_id,
                    old_values=old_values
                )
                
                return True
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to delete domestic help", original_error=e)
    
    def get_all_domestic_help(self, status=None):
        """Get all domestic help, optionally filtered by status."""
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute('''
                        SELECT id, resident_id, name, role, phone, id_proof_type, id_proof_number, 
                               photo_path, status, access_permissions
                        FROM domestic_help 
                        WHERE status = ? 
                        ORDER BY resident_id, role, name
                    ''', (status,))
                else:
                    cursor.execute('''
                        SELECT id, resident_id, name, role, phone, id_proof_type, id_proof_number, 
                               photo_path, status, access_permissions
                        FROM domestic_help 
                        ORDER BY resident_id, role, name
                    ''')
                
                rows = cursor.fetchall()
                
                domestic_help_list = []
                for row in rows:
                    help_member = DomesticHelp(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
                    )
                    domestic_help_list.append(help_member)
                
                return domestic_help_list
        except DatabaseError:
            # Re-raise database errors
            raise
        except Exception as e:
            # Wrap unexpected errors in DatabaseError
            raise DatabaseError("Failed to retrieve domestic help", original_error=e)