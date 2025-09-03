# gui/society_setup_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QTextEdit, QPushButton, QLabel, 
                            QMessageBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from models.society import SocietyManager

class SocietySetupDialog(QDialog):
    def __init__(self, parent=None, user_role=None):
        super().__init__(parent)
        self.user_role = user_role
        self.society_manager = SocietyManager()
        self.setup_ui()
        self.load_society_info()
        self.setWindowTitle("Society Setup")
        self.setModal(True)
        self.resize(500, 400)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Society Information")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Society Name
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        form_layout.addRow("Society Name*:", self.name_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(100)
        form_layout.addRow("Address*:", self.address_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(15)
        form_layout.addRow("Phone No*:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMaxLength(100)
        form_layout.addRow("Email*:", self.email_input)
        
        layout.addLayout(form_layout)
        
        # Bank Details Group
        bank_group = QGroupBox("Bank Details")
        bank_layout = QGridLayout()
        
        self.bank_name_input = QLineEdit()
        self.bank_name_input.setMaxLength(100)
        bank_layout.addWidget(QLabel("Bank Name:"), 0, 0)
        bank_layout.addWidget(self.bank_name_input, 0, 1)
        
        self.account_holder_input = QLineEdit()
        self.account_holder_input.setMaxLength(100)
        bank_layout.addWidget(QLabel("Account Holder:"), 1, 0)
        bank_layout.addWidget(self.account_holder_input, 1, 1)
        
        self.account_number_input = QLineEdit()
        self.account_number_input.setMaxLength(30)
        bank_layout.addWidget(QLabel("Account Number:"), 2, 0)
        bank_layout.addWidget(self.account_number_input, 2, 1)
        
        self.ifsc_code_input = QLineEdit()
        self.ifsc_code_input.setMaxLength(20)
        bank_layout.addWidget(QLabel("IFSC Code:"), 3, 0)
        bank_layout.addWidget(self.ifsc_code_input, 3, 1)
        
        self.branch_input = QLineEdit()
        self.branch_input.setMaxLength(100)
        bank_layout.addWidget(QLabel("Branch:"), 4, 0)
        bank_layout.addWidget(self.branch_input, 4, 1)
        
        bank_group.setLayout(bank_layout)
        layout.addWidget(bank_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_society_info)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_society_info(self):
        """Load existing society information if available"""
        society = self.society_manager.get_society_info()
        if society:
            self.name_input.setText(society.name or "")
            self.address_input.setPlainText(society.address or "")
            self.phone_input.setText(society.phone or "")
            self.email_input.setText(society.email or "")
            
            # Load bank details
            bank_details = society.bank_details or {}
            self.bank_name_input.setText(bank_details.get("bank_name", ""))
            self.account_holder_input.setText(bank_details.get("account_holder", ""))
            self.account_number_input.setText(bank_details.get("account_number", ""))
            self.ifsc_code_input.setText(bank_details.get("ifsc_code", ""))
            self.branch_input.setText(bank_details.get("branch", ""))
    
    def save_society_info(self):
        """Save society information"""
        # Validate required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Society Name is required.")
            return
            
        if not self.address_input.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Address is required.")
            return
            
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Phone No is required.")
            return
            
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Email is required.")
            return
        
        # Prepare bank details
        bank_details = {
            "bank_name": self.bank_name_input.text().strip(),
            "account_holder": self.account_holder_input.text().strip(),
            "account_number": self.account_number_input.text().strip(),
            "ifsc_code": self.ifsc_code_input.text().strip(),
            "branch": self.branch_input.text().strip()
        }
        
        # Save to database
        success = self.society_manager.save_society_info(
            self.name_input.text().strip(),
            self.address_input.toPlainText().strip(),
            self.phone_input.text().strip(),
            self.email_input.text().strip(),
            bank_details
        )
        
        if success:
            QMessageBox.information(self, "Success", "Society information saved successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to save society information.")