# gui/domestic_help_widget.py
"""
Widget for managing domestic help in the resident dialog.
"""

from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QMessageBox, 
                             QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QFormLayout, QLineEdit, QComboBox, QTextEdit, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from models.domestic_help import DomesticHelpManager


class DomesticHelpWidget(QWidget):
    def __init__(self, parent=None, resident_id=None, user_role=None):
        super().__init__(parent)
        self.resident_id = resident_id
        self.user_role = user_role
        self.domestic_help_manager = DomesticHelpManager()
        self.current_help_id = None
        self.setup_ui()
        if resident_id:
            self.load_domestic_help()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Domestic Help")
        self.add_button.clicked.connect(self.add_domestic_help)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Domestic Help")
        self.edit_button.clicked.connect(self.edit_domestic_help)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Domestic Help")
        self.delete_button.clicked.connect(self.delete_domestic_help)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        headers = ["ID", "Name", "Role", "Phone", "ID Proof", "Status"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.current_help_id = int(self.table.item(selected_rows[0].row(), 0).text())
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.current_help_id = None
    
    def load_domestic_help(self):
        if not self.resident_id:
            return
            
        try:
            domestic_help_list = self.domestic_help_manager.get_domestic_help_by_resident(self.resident_id)
            self.display_domestic_help(domestic_help_list)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load domestic help: {str(e)}")
    
    def display_domestic_help(self, domestic_help_list):
        self.table.setRowCount(len(domestic_help_list))
        
        for row, help_member in enumerate(domestic_help_list):
            self.table.setItem(row, 0, QTableWidgetItem(str(help_member.id)))
            self.table.setItem(row, 1, QTableWidgetItem(help_member.name))
            self.table.setItem(row, 2, QTableWidgetItem(help_member.role))
            self.table.setItem(row, 3, QTableWidgetItem(help_member.phone or ""))
            
            # Display ID proof information
            id_proof = ""
            if help_member.id_proof_type and help_member.id_proof_number:
                id_proof = f"{help_member.id_proof_type}: {help_member.id_proof_number}"
            elif help_member.id_proof_type:
                id_proof = help_member.id_proof_type
            self.table.setItem(row, 4, QTableWidgetItem(id_proof))
            
            self.table.setItem(row, 5, QTableWidgetItem(help_member.status))
            
            # Make ID column invisible but still accessible
            self.table.setColumnHidden(0, True)
    
    def add_domestic_help(self):
        dialog = DomesticHelpDialog(self, resident_id=self.resident_id, user_role=self.user_role)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                help_id = self.domestic_help_manager.add_domestic_help(
                    resident_id=self.resident_id,
                    name=data['name'],
                    role=data['role'],
                    phone=data['phone'],
                    id_proof_type=data['id_proof_type'],
                    id_proof_number=data['id_proof_number'],
                    status=data['status'],
                    access_permissions=data['access_permissions']
                )
                
                if help_id:
                    QMessageBox.information(self, "Success", "Domestic help added successfully!")
                    self.load_domestic_help()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add domestic help.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add domestic help: {str(e)}")
    
    def edit_domestic_help(self):
        if not self.current_help_id:
            return
            
        help_member = self.domestic_help_manager.get_domestic_help_by_id(self.current_help_id)
        if not help_member:
            QMessageBox.warning(self, "Error", "Domestic help not found.")
            return
            
        dialog = DomesticHelpDialog(self, domestic_help=help_member, user_role=self.user_role)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                success = self.domestic_help_manager.update_domestic_help(
                    help_id=self.current_help_id,
                    name=data['name'],
                    role=data['role'],
                    phone=data['phone'],
                    id_proof_type=data['id_proof_type'],
                    id_proof_number=data['id_proof_number'],
                    status=data['status'],
                    access_permissions=data['access_permissions']
                )
                
                if success:
                    QMessageBox.information(self, "Success", "Domestic help updated successfully!")
                    self.load_domestic_help()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update domestic help.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update domestic help: {str(e)}")
    
    def delete_domestic_help(self):
        if not self.current_help_id:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this domestic help member?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.domestic_help_manager.delete_domestic_help(self.current_help_id)
                if success:
                    QMessageBox.information(self, "Success", "Domestic help deleted successfully!")
                    self.load_domestic_help()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete domestic help.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete domestic help: {str(e)}")


class DomesticHelpDialog(QDialog):
    def __init__(self, parent=None, domestic_help=None, resident_id=None, user_role=None):
        super().__init__(parent)
        self.domestic_help = domestic_help
        self.resident_id = resident_id
        self.user_role = user_role
        self.setWindowTitle("Add Domestic Help" if not domestic_help else "Edit Domestic Help")
        self.setModal(True)
        self.setup_ui()
        if domestic_help:
            self.populate_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        form_layout.addRow("Name*:", self.name_input)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Maid", "Cook", "Driver", "Gardener", "Security", "Cleaner", "Other"])
        form_layout.addRow("Role*:", self.role_combo)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(15)
        form_layout.addRow("Phone:", self.phone_input)
        
        # ID Proof Type
        self.id_proof_type_combo = QComboBox()
        self.id_proof_type_combo.addItems(["", "Aadhar", "PAN", "Voter ID", "Passport", "Driving License", "Other"])
        form_layout.addRow("ID Proof Type:", self.id_proof_type_combo)
        
        # ID Proof Number
        self.id_proof_number_input = QLineEdit()
        self.id_proof_number_input.setMaxLength(50)
        form_layout.addRow("ID Proof Number:", self.id_proof_number_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        form_layout.addRow("Status:", self.status_combo)
        
        # Access Permissions
        self.access_permissions_input = QTextEdit()
        self.access_permissions_input.setMaximumHeight(80)
        self.access_permissions_input.setPlaceholderText("Enter areas this domestic help can access, one per line")
        form_layout.addRow("Access Permissions:", self.access_permissions_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def populate_data(self):
        self.name_input.setText(self.domestic_help.name)
        self.role_combo.setCurrentText(self.domestic_help.role)
        self.phone_input.setText(self.domestic_help.phone or "")
        self.id_proof_type_combo.setCurrentText(self.domestic_help.id_proof_type or "")
        self.id_proof_number_input.setText(self.domestic_help.id_proof_number or "")
        self.status_combo.setCurrentText(self.domestic_help.status or "Active")
        self.access_permissions_input.setPlainText(self.domestic_help.access_permissions or "")
    
    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'role': self.role_combo.currentText(),
            'phone': self.phone_input.text().strip(),
            'id_proof_type': self.id_proof_type_combo.currentText(),
            'id_proof_number': self.id_proof_number_input.text().strip(),
            'status': self.status_combo.currentText(),
            'access_permissions': self.access_permissions_input.toPlainText().strip()
        }
    
    def accept(self):
        # Validate required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            self.name_input.setFocus()
            return
            
        if not self.role_combo.currentText():
            QMessageBox.warning(self, "Validation Error", "Role is required.")
            self.role_combo.setFocus()
            return
        
        super().accept()