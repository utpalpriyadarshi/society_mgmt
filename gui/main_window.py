# gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, 
                             QStatusBar, QMessageBox, QMenu, 
                             QFileDialog, QPushButton, QHBoxLayout, QWidget)
from PyQt5.QtCore import Qt
import shutil
from gui.resident_form import ResidentForm
from gui.ledger_form import LedgerForm
from gui.reports_dialog import ReportsDialog
from gui.user_management_dialog import UserManagementDialog
from gui.society_setup_dialog import SocietySetupDialog
from models.society import SocietyManager

class MainWindow(QMainWindow):
    def __init__(self, user_role, username, controller, parent=None):
        super().__init__(parent)
        self.user_role = user_role
        self.username = username
        self.controller = controller
        self.setWindowTitle("Society Management System")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()
        self.check_first_time_setup()
        
    def setup_ui(self):
        # Create central widget with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add modules based on user role
        if self.user_role in ["Admin", "Treasurer", "System Admin"]:
            self.resident_form = ResidentForm(user_role=self.user_role)
            self.tabs.addTab(self.resident_form, "Resident Management")
            
            self.ledger_form = LedgerForm(current_user=self.username)
            self.tabs.addTab(self.ledger_form, "Ledger")
        
        if self.user_role in ["Admin", "Treasurer", "Viewer", "System Admin"]:
            self.reports_form = ReportsDialog()
            self.tabs.addTab(self.reports_form, "Reports")
        
        # Create menu bar
        self.create_menu()
        
        # Create custom status bar with logout button
        self.create_status_bar()
        
    def check_first_time_setup(self):
        """Check if this is the first time setup and show society setup dialog if needed"""
        if self.user_role in ["Admin", "System Admin"]:
            society_manager = SocietyManager()
            society_info = society_manager.get_society_info()
            if not society_info:
                # First time setup - show society setup dialog
                QMessageBox.information(
                    self, 
                    "First Time Setup", 
                    "Welcome! Please configure your society information."
                )
                self.open_society_setup()
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu (admin only)
        if self.user_role in ["Admin", "System Admin"]:
            tools_menu = menubar.addMenu("Tools")
            user_mgmt_action = QAction("User Management", self)
            user_mgmt_action.triggered.connect(self.open_user_management)
            tools_menu.addAction(user_mgmt_action)
            
            society_setup_action = QAction("Society Setup", self)
            society_setup_action.triggered.connect(self.open_society_setup)
            tools_menu.addAction(society_setup_action)
    
    def create_status_bar(self):
        # Create a custom status bar with user info and logout button
        status_bar = self.statusBar()
        
        # Create a widget to hold the status bar content
        status_widget = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 0, 5, 0)
        
        # User info label
        user_info = f"User: {self.username} | Role: {self.user_role}"
        status_label = QPushButton(user_info)
        status_label.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #2c3e50;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                color: #3498db;
            }
        """)
        status_label.setCursor(Qt.ArrowCursor)
        status_label.setFlat(True)
        
        # Add stretch to push logout button to the right
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)
        status_layout.addWidget(logout_button)
        
        status_widget.setLayout(status_layout)
        status_bar.addPermanentWidget(status_widget, 1)
    
    def open_user_management(self):
        user_mgmt_dialog = UserManagementDialog(self)
        user_mgmt_dialog.exec_()
    
    def open_society_setup(self):
        society_setup_dialog = SocietySetupDialog(self, user_role=self.user_role)
        society_setup_dialog.exec_()
    
    def logout(self):
        self.controller.logout()
    
    def backup_database(self):
        # Implementation for database backup
        from datetime import datetime
        import os
        import shutil
        
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"society_management_backup_{timestamp}.db"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", default_filename, "SQLite Database (*.db)")
        
        if file_path:
            try:
                # Copy the database file
                source_db = "society_management.db"
                if os.path.exists(source_db):
                    shutil.copy2(source_db, file_path)
                    QMessageBox.information(
                        self, 
                        "Backup Successful", 
                        f"Database backup created successfully!\
Saved to: {file_path}"
                    )
                else:
                    QMessageBox.critical(
                        self, 
                        "Backup Failed", 
                        "Source database file not found!"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Backup Failed", 
                    f"Failed to create database backup:\
{str(e)}"
                )