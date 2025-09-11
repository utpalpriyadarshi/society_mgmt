from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QFrame, QApplication, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.security import authenticate_user
from utils.session_manager import session_manager
from utils.db_context import get_db_connection
from datetime import datetime


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False  # Default to light mode
        self.setWindowTitle("Login - Society Management System v1.1")
        self.setFixedSize(600, 600)  # Set size to 600x600 as requested
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 30, 50, 30)
        
        # Title
        title_label = QLabel("Society Management System")
        title_font = QFont()
        title_font.setPointSize(16)  # Reduced from 18 to 16
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Please sign in to your account")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 16px; margin-bottom: 20px")
        main_layout.addWidget(subtitle_label)
        
        # Create a frame for the form
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 10px;")
        form_frame.setContentsMargins(20, 20, 20, 20)
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
                border-width: 2px;
            }
        """)
        self.username_input.returnPressed.connect(self.authenticate)
        
        # Password field
        # Create a horizontal layout for the password field and toggle button
        password_layout = QHBoxLayout()
        password_layout.setSpacing(5)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
                border-width: 2px;
            }
        """)
        self.password_input.returnPressed.connect(self.authenticate)
        
        # Password visibility toggle button
        self.toggle_password_button = QPushButton("👁")
        self.toggle_password_button.setFixedSize(30, 30)
        self.toggle_password_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)
        
        # Remember me checkbox
        self.remember_me_checkbox = QCheckBox("Remember me")
        self.remember_me_checkbox.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3498db;
                border-radius: 3px;
                background-color: #3498db;
            }
        """)
        
        # Forgot password link
        self.forgot_password_link = QPushButton("Forgot Password?")
        self.forgot_password_link.setStyleSheet("""
            QPushButton {
                color: #3498db;
                background-color: transparent;
                border: none;
                font-size: 12px;
                text-align: left;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.forgot_password_link.setCursor(Qt.PointingHandCursor)
        self.forgot_password_link.clicked.connect(self.show_forgot_password_dialog)
        
        # Add widgets to form layout
        form_layout.addWidget(self.username_input)
        form_layout.addLayout(password_layout)
        form_layout.addWidget(self.remember_me_checkbox)
        form_layout.addWidget(self.forgot_password_link)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.login_button.clicked.connect(self.authenticate)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setDefault(True)  # Make this the default button
        
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
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.theme_button.clicked.connect(self.toggle_theme)
        
        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()  # Add stretch to push the theme button to the right
        button_layout.addWidget(self.theme_button)
        
        form_layout.addLayout(button_layout)
        
        # Set layout for frame
        form_frame.setLayout(form_layout)
        main_layout.addWidget(form_frame)
        
        # Footer
        footer_label = QLabel("© 2025 Society Management System by NextGen Advisors")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #95a5a6; font-size: 6px; margin-top: 20px;")
        main_layout.addWidget(footer_label)
        
        # Set main layout
        self.setLayout(main_layout)
        
        # Set focus to username field
        self.username_input.setFocus()
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        # Update button icon
        self.theme_button.setText("☀️" if self.is_dark_mode else "🌙")
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setText("🔒")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setText("👁")
    
    def apply_theme(self):
        """Apply the current theme (light or dark mode)"""
        if self.is_dark_mode:
            # Dark mode stylesheet
            self.setStyleSheet("""
                QDialog {
                    background-color: #2c3e50;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QFrame {
                    background-color: #34495e;
                    border-radius: 10px;
                }
                QLineEdit {
                    padding: 12px;
                    border: 2px solid #7f8c8d;
                    border-radius: 6px;
                    font-size: 14px;
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                    border-width: 2px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QCheckBox {
                    color: #ecf0f1;
                    font-size: 12px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #bdc3c7;
                    border-radius: 3px;
                    background-color: #34495e;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #3498db;
                    border-radius: 3px;
                    background-color: #3498db;
                }
            """)
            # Update specific labels
            for child in self.findChildren(QLabel):
                if "Society Management System" in child.text():
                    child.setStyleSheet("color: #ecf0f1; margin-bottom: 5px;")
                elif "Please sign in" in child.text():
                    child.setStyleSheet("color: #bdc3c7; font-size: 16px; margin-bottom: 20px;")
                elif "© 2025" in child.text():
                    child.setStyleSheet("color: #bdc3c7; font-size: 7px; margin-top: 20px;")
        else:
            # Light mode stylesheet (default)
            self.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QLabel {
                    color: #2c3e50;
                }
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                }
                QLineEdit {
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 6px;
                    font-size: 14px;
                    background-color: white;
                    color: #2c3e50;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                    border-width: 2px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QCheckBox {
                    color: #2c3e50;
                    font-size: 12px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #bdc3c7;
                    border-radius: 3px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #3498db;
                    border-radius: 3px;
                    background-color: #3498db;
                }
            """)
            # Update specific labels
            for child in self.findChildren(QLabel):
                if "Society Management System" in child.text():
                    child.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
                elif "Please sign in" in child.text():
                    child.setStyleSheet("color: #7f8c8d; font-size: 16px; margin-bottom: 20px;")
                elif "© 2025" in child.text():
                    child.setStyleSheet("color: #95a5a6; font-size: 7px; margin-top: 20px;")
    
    def authenticate(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username:
            QMessageBox.warning(self, "Login Failed", "Please enter your username")
            self.username_input.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, "Login Failed", "Please enter your password")
            self.password_input.setFocus()
            return
        
        # Create a session for the user (to get session ID for audit logging)
        session_id = session_manager.create_session(username)
        
        # Use proper authentication with audit logging
        # Note: In a real application, you would get the actual IP address
        # For now, we'll use a placeholder
        ip_address = "127.0.0.1"  # Placeholder for local testing
        user_role = authenticate_user(username, password, ip_address, session_id)
        
        if user_role:
            # In a real application, you would store the session_id securely
            # For this example, we'll just print it
            print(f"Session created for {username}: {session_id}")
            self.accept()
        else:
            # Check if the account is locked
            locked_until = None
            with get_db_connection('society_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT locked_until FROM users WHERE username = ?
                ''', (username,))
                
                result = cursor.fetchone()
                if result and result[0]:
                    locked_until = datetime.fromisoformat(result[0])
            
            if locked_until and datetime.now() < locked_until:
                remaining_time = locked_until - datetime.now()
                minutes = int(remaining_time.total_seconds() // 60)
                QMessageBox.warning(self, "Login Failed", f"Account is locked. Please try again in {minutes} minutes.")
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
            
            self.password_input.clear()
            self.password_input.setFocus()

    def show_forgot_password_dialog(self):
        """Show the forgot password dialog"""
        dialog = ForgotPasswordDialog(self)
        dialog.exec_()


class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forgot Password")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Forgot Password")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Instructions
        instructions_label = QLabel("Enter your username and we'll send you instructions to reset your password.")
        instructions_label.setWordWrap(True)
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 20px;")
        main_layout.addWidget(instructions_label)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 12px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
                border-width: 2px;
            }
        """)
        
        # Add widgets to layout
        main_layout.addWidget(username_label)
        main_layout.addWidget(self.username_input)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        # Reset button
        self.reset_button = QPushButton("Reset Password")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.reset_button.clicked.connect(self.reset_password)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
        
        # Set focus to username field
        self.username_input.setFocus()
    
    def reset_password(self):
        """Handle password reset request"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Reset Password", "Please enter your username.")
            self.username_input.setFocus()
            return
            
        # Check if user exists
        from utils.db_context import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
        if not result:
            QMessageBox.warning(self, "Reset Password", "No account found with that username.")
            self.username_input.setFocus()
            return
            
        # In a real application, you would:
        # 1. Generate a secure reset token
        # 2. Store it in the database with an expiration time
        # 3. Provide a way for the user to reset their password
        #    (in a real app, you would send an email, but this app doesn't have email functionality)
        
        # For this demo, we'll just show a message
        QMessageBox.information(
            self, 
            "Reset Password", 
            "In a production environment, this system would send you instructions to reset your password.\n\n"
            "Since this is a demo application without email functionality, please contact your system administrator to reset your password."
        )
        self.accept()
    
    def apply_theme(self):
        """Apply theme to the dialog"""
        # For simplicity, we're using a basic theme
        # In a real application, you might want to match the parent's theme
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
            }
        """)