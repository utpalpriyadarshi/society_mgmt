from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QComboBox, QMessageBox, 
                             QHeaderView, QAbstractItemView, QGroupBox, QWidget)
from PyQt5.QtCore import Qt
import sqlite3
from utils.security import hash_password

class UserManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Management")
        self.setFixedSize(800, 600)
        self.current_user_id = None
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # User form group
        form_group = QGroupBox("User Details")
        form_layout = QGridLayout()
        
        # Username
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        form_layout.addWidget(self.username_label, 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)
        
        # Password
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        
        # Role
        self.role_label = QLabel("Role:")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Viewer", "Treasurer", "Admin"])
        form_layout.addWidget(self.role_label, 2, 0)
        form_layout.addWidget(self.role_combo, 2, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add User")
        self.add_button.clicked.connect(self.add_user)
        self.update_button = QPushButton("Update User")
        self.update_button.clicked.connect(self.update_user)
        self.update_button.setEnabled(False)
        self.delete_button = QPushButton("Delete User")
        self.delete_button.clicked.connect(self.delete_user)
        self.delete_button.setEnabled(False)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        form_layout.addLayout(button_layout, 3, 0, 1, 2)
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Actions"])
        self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.cellClicked.connect(self.select_user)
        main_layout.addWidget(self.users_table)
        
        self.setLayout(main_layout)
        
    def load_users(self):
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users ORDER BY id")
        users = cursor.fetchall()
        conn.close()
        
        self.users_table.setRowCount(0)
        for row, user in enumerate(users):
            self.users_table.insertRow(row)
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user[0])))
            self.users_table.setItem(row, 1, QTableWidgetItem(user[1]))
            self.users_table.setItem(row, 2, QTableWidgetItem(user[2]))
            
            # Add action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, u=user: self.edit_user(u))
            
            # Disable delete for System Admin users
            delete_button = QPushButton("Delete")
            if user[2] == "System Admin":
                delete_button.setEnabled(False)
            else:
                delete_button.clicked.connect(lambda checked, u=user: self.confirm_delete(u))
            
            action_layout.addWidget(edit_button)
            action_layout.addWidget(delete_button)
            action_widget.setLayout(action_layout)
            
            self.users_table.setCellWidget(row, 3, action_widget)
            
    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username and password are required.")
            return
            
        # Check if username already exists
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            QMessageBox.warning(self, "Duplicate User", "A user with this username already exists.")
            conn.close()
            return
            
        # Add new user
        try:
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "User added successfully.")
            self.clear_form()
            self.load_users()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add user: {str(e)}")
        finally:
            conn.close()
            
    def edit_user(self, user):
        # Prevent editing System Admin users
        if user[2] == "System Admin":
            QMessageBox.warning(self, "Access Denied", "System Admin users cannot be edited.")
            return
            
        self.current_user_id = user[0]
        self.username_input.setText(user[1])
        self.password_input.clear()
        self.role_combo.setCurrentText(user[2])
        
        self.add_button.setEnabled(False)
        self.update_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
    def update_user(self):
        if not self.current_user_id:
            return
            
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        
        if not username:
            QMessageBox.warning(self, "Input Error", "Username is required.")
            return
            
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        try:
            # Check if username already exists for another user
            cursor.execute("SELECT id FROM users WHERE username = ? AND id != ?", 
                          (username, self.current_user_id))
            existing_user = cursor.fetchone()
            
            if existing_user:
                QMessageBox.warning(self, "Duplicate User", "A user with this username already exists.")
                conn.close()
                return
                
            # Update user details
            if password:
                # Update password if provided
                password_hash = hash_password(password)
                cursor.execute(
                    "UPDATE users SET username = ?, password_hash = ?, role = ? WHERE id = ?",
                    (username, password_hash, role, self.current_user_id)
                )
            else:
                # Update without changing password
                cursor.execute(
                    "UPDATE users SET username = ?, role = ? WHERE id = ?",
                    (username, role, self.current_user_id)
                )
                
            conn.commit()
            QMessageBox.information(self, "Success", "User updated successfully.")
            self.clear_form()
            self.load_users()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update user: {str(e)}")
        finally:
            conn.close()
            
    def confirm_delete(self, user):
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete user '{user[1]}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_user(user[0])
            
    def delete_user(self, user_id=None):
        user_id = user_id or self.current_user_id
        
        if not user_id:
            return
            
        # Prevent deleting the last admin user
        conn = sqlite3.connect('society_management.db')
        cursor = conn.cursor()
        
        try:
            # Check if this is the only admin
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
            admin_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            user_role = cursor.fetchone()
            
            # Prevent deleting System Admin users
            if user_role and user_role[0] == "System Admin":
                QMessageBox.warning(
                    self, 
                    "Delete Error", 
                    "System Admin users cannot be deleted."
                )
                return
            
            if user_role and user_role[0] == "Admin" and admin_count <= 1:
                QMessageBox.warning(
                    self, 
                    "Delete Error", 
                    "Cannot delete the last admin user. At least one admin user is required."
                )
                return
                
            # Delete the user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            
            QMessageBox.information(self, "Success", "User deleted successfully.")
            self.clear_form()
            self.load_users()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to delete user: {str(e)}")
        finally:
            conn.close()
            
    def select_user(self, row, column):
        # Get user data from the selected row
        user_id = self.users_table.item(row, 0).text()
        username = self.users_table.item(row, 1).text()
        role = self.users_table.item(row, 2).text()
        
        # Prevent selecting System Admin users for editing
        if role == "System Admin":
            return
            
        self.current_user_id = int(user_id)
        self.username_input.setText(username)
        self.password_input.clear()
        self.role_combo.setCurrentText(role)
        
        self.add_button.setEnabled(False)
        self.update_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        
    def clear_form(self):
        self.username_input.clear()
        self.password_input.clear()
        self.role_combo.setCurrentIndex(0)
        self.current_user_id = None
        
        self.add_button.setEnabled(True)
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        # Clear selection in table
        self.users_table.clearSelection()