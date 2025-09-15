import sys
import os

# Add the parent directory to the Python path so imports work correctly when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QFrame, QApplication, QCheckBox, QProgressBar,
                             QFormLayout, QDialogButtonBox, QTextEdit, QWidget, QGroupBox,
                             QFontDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from utils.security import authenticate_user
from utils.session_manager import session_manager
from utils.db_context import get_db_connection
from utils.config import load_config, save_config
from datetime import datetime
import pyotp


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False  # Default to light mode
        self.setWindowTitle("Login - Society Management System v1.1")
        self.resize(1000, 600)  # Initial size
        self.setMinimumSize(800, 500)  # Minimum size
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setup_ui()
        self.apply_theme()
        self.load_user_preferences()
        
    def setup_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left section - Login form
        self.left_section = QFrame()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(50, 30, 50, 30)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join("assets", "nextgenlogo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText("LOGO")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498db;")
        
        # Title
        title_label = QLabel("Society Management System")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        # Subtitle
        subtitle_label = QLabel("Please sign in to your account")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px")
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(0, 20, 0, 20)
        
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
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
                border-width: 2px;
            }
        """)
        self.username_input.returnPressed.connect(self.authenticate)
        
        # Password field
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
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
                border-width: 2px;
            }
        """)
        self.password_input.returnPressed.connect(self.authenticate)
        
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
        
        self.remember_me_checkbox = QCheckBox("Remember me")
        self.remember_me_checkbox.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 14px;
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
        
        self.forgot_password_link = QPushButton("Forgot Password?")
        self.forgot_password_link.setStyleSheet("""
            QPushButton {
                color: #3498db;
                background-color: transparent;
                border: none;
                font-size: 14px;
                text-align: left;
                padding: 0px;
                margin: 0px;
                margin-top: 10px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.forgot_password_link.setCursor(Qt.PointingHandCursor)
        self.forgot_password_link.clicked.connect(self.show_forgot_password_dialog)
        
        form_layout.addWidget(self.username_input)
        form_layout.addLayout(password_layout)
        form_layout.addWidget(self.remember_me_checkbox)
        form_layout.addWidget(self.forgot_password_link)
        
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
        self.login_button.setDefault(True)
        
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
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        button_layout.addWidget(self.theme_button)
        
        left_layout.addWidget(logo_label)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addLayout(form_layout)
        left_layout.addLayout(button_layout)

        # Progress bar for loading indication
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress bar
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        left_layout.addStretch()
        
        self.left_section.setLayout(left_layout)
        
        # Right section - Image
        self.right_section = QFrame()
        self.right_section.setObjectName("imageSection")
        
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        image_path = os.path.join("assets", "SocietyImage1.jpg")
        self.image_label = QLabel()
        self.pixmap = QPixmap(image_path)
        
        if not self.pixmap.isNull():
            self.image_label.setAlignment(Qt.AlignCenter)
            right_layout.addWidget(self.image_label)
            self.update_image()  # Initial image scaling
        else:
            fallback_label = QLabel()
            fallback_label.setStyleSheet("""
                background-color: #3498db;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            """)
            right_layout.addWidget(fallback_label)
            
        self.right_section.setLayout(right_layout)
        
        main_layout.addWidget(self.left_section, 1)
        main_layout.addWidget(self.right_section, 1)
        
        self.setLayout(main_layout)
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
            """)
            
            # Update left section
            self.left_section.setStyleSheet("""
                QFrame {
                    background-color: #34495e;
                }
            """)
            
            # Update title labels
            for child in self.findChildren(QLabel):
                if child.text() == "Society Management System":
                    child.setStyleSheet("color: #ecf0f1; font-size: 22px; font-weight: bold; margin-bottom: 5px;")
                elif child.text() == "Please sign in to your account":
                    child.setStyleSheet("color: #bdc3c7; font-size: 14px; margin-bottom: 20px;")
                elif "Forgot Password" in child.text():
                    child.setStyleSheet("color: #3498db; background-color: transparent; border: none; font-size: 12px; text-align: left; padding: 0px; margin: 10px 0px 0px 0px;")
            
            # Update input fields
            self.username_input.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    border: 2px solid #7f8c8d;
                    border-radius: 6px;
                    font-size: 14px;
                    background-color: #34495e;
                    color: #ecf0f1;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                    border-width: 2px;
                }
            """)
            
            self.password_input.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    border: 2px solid #7f8c8d;
                    border-radius: 6px;
                    font-size: 14px;
                    background-color: #34495e;
                    color: #ecf0f1;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                    border-width: 2px;
                }
            """)
            
            # Update buttons
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
            
            # Update checkbox
            self.remember_me_checkbox.setStyleSheet("""
                QCheckBox {
                    color: #ecf0f1;
                    font-size: 12px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
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
            
            # Update links
            self.forgot_password_link.setStyleSheet("""
                QPushButton {
                    color: #3498db;
                    background-color: transparent;
                    border: none;
                    font-size: 12px;
                    text-align: left;
                    padding: 0px;
                    margin: 10px 0px 0px 0px;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
        else:
            # Light mode stylesheet (default)
            self.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
            """)
            
            # Update left section
            self.left_section.setStyleSheet("""
                QFrame {
                    background-color: white;
                }
            """)
            
            # Update title labels
            for child in self.findChildren(QLabel):
                if child.text() == "Society Management System":
                    child.setStyleSheet("color: #2c3e50; font-size: 22px; font-weight: bold; margin-bottom: 5px;")
                elif child.text() == "Please sign in to your account":
                    child.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
                elif "Forgot Password" in child.text():
                    child.setStyleSheet("color: #3498db; background-color: transparent; border: none; font-size: 12px; text-align: left; padding: 0px; margin: 10px 0px 0px 0px;")
            
            # Update input fields
            self.username_input.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 6px;
                    font-size: 14px;
                    background-color: white;
                    color: #2c3e50;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                    border-width: 2px;
                }
            """)
            
            self.password_input.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 6px;
                    font-size: 14px;
                    background-color: white;
                    color: #2c3e50;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                    outline: none;
                    border-width: 2px;
                }
            """)
            
            # Update buttons
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
            
            # Update checkbox
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
            
            # Update links
            self.forgot_password_link.setStyleSheet("""
                QPushButton {
                    color: #3498db;
                    background-color: transparent;
                    border: none;
                    font-size: 12px;
                    text-align: left;
                    padding: 0px;
                    margin: 10px 0px 0px 0px;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
    
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

        # Show loading indicator
        self.progress_bar.setVisible(True)
        self.username_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.login_button.setEnabled(False)

        try:
            # Create a session for the user (to get session ID for audit logging)
            session_id = session_manager.create_session(username)
            
            # Use proper authentication with audit logging
            # Note: In a real application, you would get the actual IP address
            # For now, we'll use a placeholder
            ip_address = "127.0.0.1"  # Placeholder for local testing
            user_role = authenticate_user(username, password, ip_address, session_id)
            
            if user_role:
                config = load_config()
                if self.remember_me_checkbox.isChecked():
                    config['remember_me'] = True
                    config['username'] = username
                else:
                    config['remember_me'] = False
                    config.pop('username', None)
                save_config(config)
                # In a real application, you would store the session_id securely
                # For this example, we'll  just print it
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
        finally:
            # Hide loading indicator
            self.progress_bar.setVisible(False)
            self.username_input.setEnabled(True)
            self.password_input.setEnabled(True)
            self.login_button.setEnabled(True)

    def load_user_preferences(self):
        config = load_config()
        if config.get('remember_me'):
            self.username_input.setText(config.get('username', ''))
            self.remember_me_checkbox.setChecked(True)

    
    def show_forgot_password_dialog(self):
        """Show the forgot password dialog"""
        dialog = ForgotPasswordDialog(self)
        dialog.exec_()

    def update_image(self):
        if not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(
                self.right_section.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()


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
        """Handle password reset request with TOTP verification"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Reset Password", "Please enter your username.")
            self.username_input.setFocus()
            return
            
        # Check if user exists and has TOTP enabled
        from utils.db_context import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, totp_secret, totp_enabled FROM users WHERE username = ?", 
                (username,)
            )
            result = cursor.fetchone()
            
        if not result:
            QMessageBox.warning(self, "Reset Password", "No account found with that username.")
            self.username_input.setFocus()
            return
            
        user_id, totp_secret, totp_enabled = result
        
        # Check if TOTP is enabled for this user
        if not totp_enabled or not totp_secret:
            QMessageBox.warning(
                self, 
                "Reset Password", 
                "Two-factor authentication is not enabled for this account. "
                "Please contact your system administrator to reset your password."
            )
            self.username_input.setFocus()
            return
            
        # Show TOTP verification dialog
        totp_dialog = TOTPPasswordResetDialog(username, totp_secret, self)
        if totp_dialog.exec_() == QDialog.Accepted:
            # Password has been reset successfully
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


class TOTPPasswordResetDialog(QDialog):
    def __init__(self, username, totp_secret, parent=None):
        super().__init__(parent)
        self.username = username
        self.totp_secret = totp_secret
        self.setWindowTitle("TOTP Password Reset")
        self.setFixedSize(400, 350)
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Password Reset")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Instructions
        instructions_label = QLabel(
            f"Enter the 6-digit code from your authenticator app to reset your password for user '{self.username}'."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 20px;")
        main_layout.addWidget(instructions_label)
        
        # TOTP Code
        totp_label = QLabel("Authenticator Code*:")
        totp_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 12px;")
        self.totp_input = QLineEdit()
        self.totp_input.setPlaceholderText("Enter 6-digit code")
        self.totp_input.setMaxLength(6)
        self.totp_input.setStyleSheet("""
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
        self.totp_input.returnPressed.connect(self.verify_totp_and_reset)
        
        main_layout.addWidget(totp_label)
        main_layout.addWidget(self.totp_input)
        
        # New Password
        password_label = QLabel("New Password*:")
        password_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 12px;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter new password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
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
        
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_input)
        
        # Confirm Password
        confirm_label = QLabel("Confirm Password*:")
        confirm_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 12px;")
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm new password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet("""
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
        
        main_layout.addWidget(confirm_label)
        main_layout.addWidget(self.confirm_input)
        
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
        self.reset_button.clicked.connect(self.verify_totp_and_reset)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
        
        # Set focus to TOTP field
        self.totp_input.setFocus()
    
    def verify_totp_and_reset(self):
        """Verify TOTP code and reset password"""
        # Get inputs
        totp_code = self.totp_input.text().strip()
        new_password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        
        # Validate inputs
        if not totp_code:
            QMessageBox.warning(self, "Validation Error", "Please enter the 6-digit code from your authenticator app.")
            self.totp_input.setFocus()
            return
            
        if len(totp_code) != 6 or not totp_code.isdigit():
            QMessageBox.warning(self, "Validation Error", "Please enter a valid 6-digit code.")
            self.totp_input.setFocus()
            self.totp_input.selectAll()
            return
            
        if not new_password:
            QMessageBox.warning(self, "Validation Error", "Please enter a new password.")
            self.password_input.setFocus()
            return
            
        if len(new_password) < 6:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters long.")
            self.password_input.setFocus()
            self.password_input.selectAll()
            return
            
        if new_password != confirm_password:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            self.confirm_input.setFocus()
            self.confirm_input.selectAll()
            return
            
        # Verify TOTP code
        import pyotp
        totp = pyotp.TOTP(self.totp_secret)
        if not totp.verify(totp_code):
            QMessageBox.warning(
                self, 
                "Verification Failed", 
                "The code you entered is invalid or has expired. Please make sure you're entering the current code from your authenticator app."
            )
            self.totp_input.setFocus()
            self.totp_input.selectAll()
            return
            
        # Reset password
        try:
            from utils.security import hash_password
            from utils.db_context import get_db_connection
            
            hashed_password = hash_password(new_password)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (hashed_password, self.username)
                )
                conn.commit()
                
            QMessageBox.information(
                self, 
                "Success", 
                "Your password has been successfully reset! You can now log in with your new password."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset password: {str(e)}")
            
    def apply_theme(self):
        """Apply theme to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
            }
        """)


# Add this at the end of the file to make it runnable directly for testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = LoginDialog()
    dialog.show()
    sys.exit(app.exec_())