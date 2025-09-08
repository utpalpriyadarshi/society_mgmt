# gui/audit_log_viewer.py
"""
Audit Log Viewer for the Society Management System.
This module provides a GUI for viewing audit logs.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QDateEdit, QMessageBox, 
                            QFileDialog, QGroupBox, QFormLayout, QTableWidget,
                            QTableWidgetItem, QTextEdit, QApplication)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from utils.audit_logger import audit_logger


class AuditLogViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audit Log Viewer")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setup_ui()
        self.load_audit_logs()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Filter controls
        filter_group = QGroupBox("Filter Options")
        filter_layout = QFormLayout()
        
        # User filter
        self.user_filter = QComboBox()
        self.user_filter.setEditable(True)
        self.user_filter.setPlaceholderText("All users")
        filter_layout.addRow("User:", self.user_filter)
        
        # Action filter
        self.action_filter = QComboBox()
        self.action_filter.setEditable(True)
        self.action_filter.addItems([
            "All Actions",
            "LOGIN_SUCCESS",
            "LOGIN_FAILURE",
            "LOGOUT",
            "SESSION_CREATED",
            "SESSION_DESTROYED",
            "CREATE_RESIDENT",
            "UPDATE_RESIDENT",
            "DELETE_RESIDENT",
            "CREATE_PAYMENT",
            "CREATE_EXPENSE",
            "REVERSE_TRANSACTION",
            "DELETE_TRANSACTION"
        ])
        self.action_filter.setPlaceholderText("All actions")
        filter_layout.addRow("Action:", self.action_filter)
        
        # Date range filters
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))  # Last 30 days by default
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addRow("Start Date:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addRow("End Date:", self.end_date)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Filter and refresh buttons
        button_layout = QHBoxLayout()
        self.filter_button = QPushButton("Apply Filters")
        self.filter_button.clicked.connect(self.apply_filters)
        button_layout.addWidget(self.filter_button)
        
        self.reset_button = QPushButton("Reset Filters")
        self.reset_button.clicked.connect(self.reset_filters)
        button_layout.addWidget(self.reset_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_audit_logs)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
        # Audit log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(7)
        headers = ["Timestamp", "User", "Action", "Table", "Record ID", "Details", "Session ID"]
        self.log_table.setHorizontalHeaderLabels(headers)
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make read-only
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.log_table)
        
        # Details panel
        details_group = QGroupBox("Details")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def load_audit_logs(self):
        """Load audit logs into the table"""
        try:
            # Get filtered audit logs
            logs = self.get_filtered_logs()
            
            # Populate the table
            self.log_table.setRowCount(len(logs))
            
            # Keep track of unique users for the filter dropdown
            users = set()
            
            for row, log in enumerate(logs):
                users.add(log['username'])
                
                # Timestamp
                timestamp_item = QTableWidgetItem(log['timestamp'])
                timestamp_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.log_table.setItem(row, 0, timestamp_item)
                
                # User
                user_item = QTableWidgetItem(log['username'])
                user_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.log_table.setItem(row, 1, user_item)
                
                # Action
                action_item = QTableWidgetItem(log['action'])
                action_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.log_table.setItem(row, 2, action_item)
                
                # Table
                table_item = QTableWidgetItem(log['table_name'] or "")
                table_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.log_table.setItem(row, 3, table_item)
                
                # Record ID
                record_id_item = QTableWidgetItem(str(log['record_id']) if log['record_id'] else "")
                record_id_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.log_table.setItem(row, 4, record_id_item)
                
                # Details
                # Show flat number if available in new_values
                details = log['details'] or ""
                if log['new_values']:
                    try:
                        new_values = log['new_values']
                        if isinstance(new_values, str):
                            import json
                            new_values = json.loads(new_values)
                        if isinstance(new_values, dict) and 'flat_no' in new_values:
                            details = f"Flat: {new_values['flat_no'] or 'N/A'}"
                            if 'category' in new_values:
                                details += f", Category: {new_values['category']}"
                            # For expenses, show debit amount; for payments, show credit amount
                            if 'debit' in new_values and new_values['debit'] > 0:
                                details += f", Amount: {new_values['debit']}"
                            elif 'credit' in new_values and new_values['credit'] > 0:
                                details += f", Amount: {new_values['credit']}"
                    except:
                        pass  # If parsing fails, use original details
                
                details_item = QTableWidgetItem(details)
                details_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.log_table.setItem(row, 5, details_item)
                
                # Session ID
                session_item = QTableWidgetItem(log['session_id'] or "")
                session_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.log_table.setItem(row, 6, session_item)
            
            # Populate user filter dropdown
            self.user_filter.clear()
            self.user_filter.addItem("All users")
            for user in sorted(users):
                self.user_filter.addItem(user)
            
            # Resize columns to fit content
            self.log_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load audit logs: {str(e)}")
    
    def get_filtered_logs(self):
        """Get filtered audit logs based on filter criteria"""
        try:
            # Get filter values
            selected_user = self.user_filter.currentText()
            selected_action = self.action_filter.currentText()
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            # Get all logs first
            all_logs = audit_logger.get_audit_logs(limit=1000)
            
            # Apply filters
            filtered_logs = []
            for log in all_logs:
                # Filter by user
                if selected_user != "All users" and selected_user != "" and log['username'] != selected_user:
                    continue
                
                # Filter by action
                if selected_action != "All Actions" and selected_action != "" and log['action'] != selected_action:
                    continue
                
                # For date filtering, we would need to modify the audit_logger to support it
                # For now, we'll just include all logs that pass the other filters
                filtered_logs.append(log)
            
            return filtered_logs
        except Exception as e:
            print(f"Error getting filtered logs: {e}")
            return audit_logger.get_audit_logs(limit=1000)
    
    def apply_filters(self):
        """Apply filters and reload audit logs"""
        self.load_audit_logs()
    
    def reset_filters(self):
        """Reset all filters to default values"""
        self.user_filter.setCurrentIndex(0)  # "All users"
        self.action_filter.setCurrentIndex(0)  # "All Actions"
        self.start_date.setDate(QDate.currentDate().addDays(-30))  # Last 30 days
        self.end_date.setDate(QDate.currentDate())  # Today
        self.load_audit_logs()
    
    def on_selection_changed(self):
        """Display detailed information when a row is selected"""
        selected_rows = self.log_table.selectionModel().selectedRows()
        if not selected_rows:
            self.details_text.clear()
            return
            
        row = selected_rows[0].row()
        
        # Get the log entry details
        try:
            # This is a simplified approach - in a real implementation, you might want to
            # store the full log entry data in the table or retrieve it from the database again
            timestamp = self.log_table.item(row, 0).text() if self.log_table.item(row, 0) else ""
            user = self.log_table.item(row, 1).text() if self.log_table.item(row, 1) else ""
            action = self.log_table.item(row, 2).text() if self.log_table.item(row, 2) else ""
            table_name = self.log_table.item(row, 3).text() if self.log_table.item(row, 3) else ""
            record_id = self.log_table.item(row, 4).text() if self.log_table.item(row, 4) else ""
            details = self.log_table.item(row, 5).text() if self.log_table.item(row, 5) else ""
            session_id = self.log_table.item(row, 6).text() if self.log_table.item(row, 6) else ""
            
            # Format detailed information
            details_text = f"""Audit Log Entry Details:
======================

Timestamp: {timestamp}
User: {user}
Action: {action}
Table: {table_name}
Record ID: {record_id}
Session ID: {session_id}

Details: {details}
"""
            
            self.details_text.setPlainText(details_text)
        except Exception as e:
            self.details_text.setPlainText(f"Error displaying details: {str(e)}")