# gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QAction, 
                             QStatusBar, QMessageBox, QMenu, 
                             QFileDialog, QPushButton, QHBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
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
        self.is_dark_mode = False  # Default to light mode
        self.setWindowTitle("Society Management System")
        self.setGeometry(100, 100, 1000, 700)
        self.setup_ui()
        self.check_first_time_setup()
        self.apply_theme()  # Apply initial theme
        
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
        
        # View menu for theme toggle
        view_menu = menubar.addMenu("View")
        self.theme_action = QAction("Dark Mode", self)
        self.theme_action.setCheckable(True)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
        
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
        
        # Theme toggle button
        self.theme_button = QPushButton("🌙")
        self.theme_button.setFixedSize(30, 30)
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        status_layout.addWidget(self.theme_button)
        
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
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        # Update menu action state
        self.theme_action.setChecked(self.is_dark_mode)
        # Update button icon
        self.theme_button.setText("☀️" if self.is_dark_mode else "🌙")
    
    def apply_theme(self):
        """Apply the current theme (light or dark mode)"""
        if self.is_dark_mode:
            # Dark mode stylesheet
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QTabWidget::pane {
                    border: 1px solid #34495e;
                    background-color: #34495e;
                }
                QTabBar::tab {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    padding: 8px 12px;
                    border: 1px solid #34495e;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background-color: #34495e;
                    border-bottom: 2px solid #3498db;
                }
                QTabBar::tab:hover {
                    background-color: #34495e;
                }
                QMenuBar {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border-bottom: 1px solid #34495e;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #34495e;
                }
                QMenuBar::item:pressed {
                    background-color: #3498db;
                }
                QMenu {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #2c3e50;
                }
                QMenu::item {
                    padding: 4px 20px;
                }
                QMenu::item:selected {
                    background-color: #3498db;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QPushButton:disabled {
                    background-color: #7f8c8d;
                }
                QTableView {
                    background-color: #34495e;
                    color: #ecf0f1;
                    gridline-color: #2c3e50;
                    alternate-background-color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    padding: 4px;
                    border: 1px solid #34495e;
                }
                QTableView::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #7f8c8d;
                    padding: 4px;
                    border-radius: 4px;
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                    border: 1px solid #3498db;
                }
                QGroupBox {
                    border: 1px solid #34495e;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QStatusBar {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border-top: 1px solid #34495e;
                }
            """)
        else:
            # Light mode stylesheet (default)
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #2c3e50;
                }
                QTabWidget::pane {
                    border: 1px solid #bdc3c7;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    padding: 8px 12px;
                    border: 1px solid #bdc3c7;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 2px solid #3498db;
                }
                QTabBar::tab:hover {
                    background-color: #d5dbdb;
                }
                QMenuBar {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border-bottom: 1px solid #bdc3c7;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #ecf0f1;
                }
                QMenuBar::item:pressed {
                    background-color: #3498db;
                    color: white;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                }
                QMenu::item {
                    padding: 4px 20px;
                }
                QMenu::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                }
                QTableView {
                    background-color: #ffffff;
                    color: #2c3e50;
                    gridline-color: #bdc3c7;
                    alternate-background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    padding: 4px;
                    border: 1px solid #bdc3c7;
                }
                QTableView::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    padding: 4px;
                    border-radius: 4px;
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                    border: 1px solid #3498db;
                }
                QGroupBox {
                    border: 1px solid #bdc3c7;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                    background-color: #ffffff;
                    color: #2c3e50;
                }
                QStatusBar {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border-top: 1px solid #bdc3c7;
                }
            """)

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
                        f"Database backup created successfully! Saved to: {file_path}"
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
                    f"Failed to create database backup: {str(e)}"
                )