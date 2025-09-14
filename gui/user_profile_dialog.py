# gui/user_profile_dialog.py
"""
User Profile Dialog for the Society Management System.
This dialog allows users to manage their profile settings including TOTP setup.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QGroupBox, QWidget, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt
import pyotp
import qrcode
from PIL import Image
import io
import base64
from utils.db_context import get_db_connection


class UserProfileDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.totp_secret = None
        self.totp_enabled = False
        self.setWindowTitle("User Profile")
        self.setFixedSize(500, 600)
        self.setup_ui()
        self.load_user_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("User Profile")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # User Info Group
        info_group = QGroupBox("User Information")
        info_layout = QFormLayout()
        
        self.username_label = QLabel(self.username)
        info_layout.addRow("Username:", self.username_label)
        
        # TODO: Add other user info fields as needed
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # TOTP Setup Group
        self.totp_group = QGroupBox("Two-Factor Authentication (TOTP)")
        self.totp_layout = QVBoxLayout()
        
        self.totp_status_label = QLabel("Two-factor authentication is not enabled for your account.")
        self.totp_status_label.setWordWrap(True)
        self.totp_layout.addWidget(self.totp_status_label)
        
        # TOTP Enable/Disable Button
        self.totp_toggle_button = QPushButton("Enable Two-Factor Authentication")
        self.totp_toggle_button.clicked.connect(self.toggle_totp)
        self.totp_layout.addWidget(self.totp_toggle_button)
        
        # TOTP Setup Instructions (hidden by default)
        self.totp_instructions = QTextEdit()
        self.totp_instructions.setReadOnly(True)
        self.totp_instructions.setVisible(False)
        self.totp_instructions.setMaximumHeight(150)
        self.totp_layout.addWidget(self.totp_instructions)
        
        # TOTP QR Code (hidden by default)
        self.qr_code_label = QLabel()
        self.qr_code_label.setAlignment(Qt.AlignCenter)
        self.qr_code_label.setVisible(False)
        self.totp_layout.addWidget(self.qr_code_label)
        
        # TOTP Code Input (hidden by default)
        self.totp_code_input = QLineEdit()
        self.totp_code_input.setPlaceholderText("Enter 6-digit code from your authenticator app")
        self.totp_code_input.setVisible(False)
        self.totp_layout.addWidget(self.totp_code_input)
        
        # TOTP Verify Button (hidden by default)
        self.totp_verify_button = QPushButton("Verify and Enable")
        self.totp_verify_button.clicked.connect(self.verify_totp_setup)
        self.totp_verify_button.setVisible(False)
        self.totp_layout.addWidget(self.totp_verify_button)
        
        # TOTP Disable Confirmation (hidden by default)
        self.totp_disable_confirm = QTextEdit()
        self.totp_disable_confirm.setReadOnly(True)
        self.totp_disable_confirm.setVisible(False)
        self.totp_disable_confirm.setMaximumHeight(100)
        self.totp_layout.addWidget(self.totp_disable_confirm)
        
        self.totp_group.setLayout(self.totp_layout)
        main_layout.addWidget(self.totp_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def load_user_data(self):
        """Load user data including TOTP status"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT totp_secret, totp_enabled FROM users WHERE username = ?", 
                    (self.username,)
                )
                result = cursor.fetchone()
                
                if result:
                    self.totp_secret, totp_enabled = result
                    self.totp_enabled = bool(totp_enabled) if totp_enabled is not None else False
                    
                    # Update UI based on TOTP status
                    self.update_totp_ui()
                else:
                    QMessageBox.warning(self, "Error", "User not found.")
                    self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user data: {str(e)}")
            self.reject()
            
    def update_totp_ui(self):
        """Update the TOTP UI based on current status"""
        if self.totp_enabled and self.totp_secret:
            self.totp_status_label.setText("Two-factor authentication is enabled for your account.")
            self.totp_toggle_button.setText("Disable Two-Factor Authentication")
        else:
            self.totp_status_label.setText("Two-factor authentication is not enabled for your account.")
            self.totp_toggle_button.setText("Enable Two-Factor Authentication")
            
    def toggle_totp(self):
        """Toggle TOTP setup - either enable or disable"""
        if self.totp_enabled and self.totp_secret:
            self.disable_totp()
        else:
            self.enable_totp()
            
    def enable_totp(self):
        """Start the TOTP setup process"""
        # Generate a new secret if we don't have one
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
            
        # Generate provisioning URI for QR code
        totp_uri = pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.username,
            issuer_name="Society Management System"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to QImage for display
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        from PyQt5.QtGui import QPixmap, QImage
        qimage = QImage.fromData(img_buffer.getvalue())
        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.qr_code_label.setPixmap(pixmap)
        
        # Show setup instructions
        instructions = f"""
        <h3>Setting up Two-Factor Authentication</h3>
        <ol>
            <li>Install an authenticator app on your smartphone (like Google Authenticator or Authy)</li>
            <li>Scan the QR code below with your authenticator app</li>
            <li>Enter the 6-digit code generated by your app to verify setup</li>
        </ol>
        <p><b>Note:</b> If you cannot scan the QR code, you can manually enter this secret key: 
        <b>{self.totp_secret}</b></p>
        """
        
        self.totp_instructions.setHtml(instructions)
        
        # Show TOTP setup elements
        self.totp_instructions.setVisible(True)
        self.qr_code_label.setVisible(True)
        self.totp_code_input.setVisible(True)
        self.totp_verify_button.setVisible(True)
        
        # Hide main status elements temporarily
        self.totp_status_label.setVisible(False)
        self.totp_toggle_button.setVisible(False)
        
    def disable_totp(self):
        """Show confirmation for disabling TOTP"""
        confirmation_text = """
        <h3>Disable Two-Factor Authentication</h3>
        <p>Are you sure you want to disable two-factor authentication?</p>
        <p><b>Warning:</b> This will reduce the security of your account. 
        You will no longer be able to use two-factor authentication for password resets.</p>
        <p>Click the Disable button below to confirm.</p>
        """
        
        self.totp_disable_confirm.setHtml(confirmation_text)
        
        # Replace the toggle button with disable confirmation
        self.totp_toggle_button.setText("Disable")
        self.totp_toggle_button.clicked.disconnect()
        self.totp_toggle_button.clicked.connect(self.confirm_disable_totp)
        
        # Show disable confirmation elements
        self.totp_disable_confirm.setVisible(True)
        self.totp_status_label.setVisible(False)
        self.totp_toggle_button.setVisible(True)
        
    def confirm_disable_totp(self):
        """Confirm and disable TOTP"""
        reply = QMessageBox.question(
            self, 
            "Confirm Disable TOTP", 
            "Are you sure you want to disable two-factor authentication? "
            "This will reduce the security of your account.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET totp_secret = NULL, totp_enabled = 0 WHERE username = ?",
                        (self.username,)
                    )
                    conn.commit()
                    
                    # Update local variables
                    self.totp_secret = None
                    self.totp_enabled = False
                    
                    # Update UI
                    self.update_totp_ui()
                    
                    # Restore normal toggle button
                    self.totp_toggle_button.clicked.disconnect()
                    self.totp_toggle_button.clicked.connect(self.toggle_totp)
                    
                    # Hide disable confirmation elements
                    self.totp_disable_confirm.setVisible(False)
                    self.totp_status_label.setVisible(True)
                    self.totp_toggle_button.setVisible(True)
                    
                    QMessageBox.information(
                        self, 
                        "Success", 
                        "Two-factor authentication has been disabled for your account."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to disable TOTP: {str(e)}")
                
    def verify_totp_setup(self):
        """Verify TOTP setup with the code from the authenticator app"""
        code = self.totp_code_input.text().strip()
        
        if not code:
            QMessageBox.warning(self, "Validation Error", "Please enter the 6-digit code from your authenticator app.")
            self.totp_code_input.setFocus()
            return
            
        if len(code) != 6 or not code.isdigit():
            QMessageBox.warning(self, "Validation Error", "Please enter a valid 6-digit code.")
            self.totp_code_input.setFocus()
            return
            
        # Verify the code
        totp = pyotp.TOTP(self.totp_secret)
        if totp.verify(code):
            # Save TOTP secret to database
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET totp_secret = ?, totp_enabled = 1 WHERE username = ?",
                        (self.totp_secret, self.username)
                    )
                    conn.commit()
                    
                    # Update local variables
                    self.totp_enabled = True
                    
                    # Update UI
                    self.update_totp_ui()
                    
                    # Hide setup elements
                    self.totp_instructions.setVisible(False)
                    self.qr_code_label.setVisible(False)
                    self.totp_code_input.setVisible(False)
                    self.totp_verify_button.setVisible(False)
                    
                    # Show main status elements
                    self.totp_status_label.setVisible(True)
                    self.totp_toggle_button.setVisible(True)
                    
                    QMessageBox.information(
                        self, 
                        "Success", 
                        "Two-factor authentication has been successfully enabled for your account!"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save TOTP settings: {str(e)}")
        else:
            QMessageBox.warning(
                self, 
                "Verification Failed", 
                "The code you entered is invalid. Please make sure you're entering the current code from your authenticator app."
            )
            self.totp_code_input.setFocus()
            self.totp_code_input.selectAll()