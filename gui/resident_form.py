# gui/resident_form.py
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                            QPushButton, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QComboBox, QDateEdit, QLabel,
                            QMessageBox, QHeaderView, QFormLayout,
                            QDialog, QDialogButtonBox, QDoubleSpinBox,
                            QSpinBox, QTextEdit)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIntValidator
from models.resident import ResidentManager

class ResidentForm(QWidget):
    def __init__(self, parent=None, user_role=None):
        super().__init__(parent)
        self.resident_manager = ResidentManager()
        self.user_role = user_role  # Store user role to check permissions
        self.current_resident_id = None
        self.setup_ui()
        self.load_residents()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Search and filter area
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Flat No, Name, Phone or Email...")
        self.search_input.textChanged.connect(self.filter_residents)
        search_layout.addWidget(self.search_input)
        
        # Buttons
        self.add_button = QPushButton("Add Resident")
        self.add_button.clicked.connect(self.add_resident)
        search_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Resident")
        self.edit_button.clicked.connect(self.edit_resident)
        self.edit_button.setEnabled(False)
        search_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Resident")
        self.delete_button.clicked.connect(self.delete_resident)
        self.delete_button.setEnabled(False)
        search_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Only the requested fields + some key info
        headers = ["ID", "Flat No", "Name", "Phone No", "Email"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
    
    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
    
    def filter_residents(self, text):
        if not text:
            self.load_residents()
            return
        
        residents = self.resident_manager.search_residents(text)
        self.display_residents(residents)
    
    def display_residents(self, residents):
        # Sort residents by flat number
        residents.sort(key=lambda x: self._extract_flat_number(x.flat_no))
        
        self.table.setRowCount(len(residents))
        
        for row, resident in enumerate(residents):
            self.table.setItem(row, 0, QTableWidgetItem(str(resident.id)))
            self.table.setItem(row, 1, QTableWidgetItem(resident.flat_no))
            self.table.setItem(row, 2, QTableWidgetItem(resident.name))
            self.table.setItem(row, 3, QTableWidgetItem(resident.mobile_no))
            self.table.setItem(row, 4, QTableWidgetItem(resident.email))
            
            # Make ID column invisible but still accessible
            self.table.setColumnHidden(0, True)
    
    def _extract_flat_number(self, flat_no):
        """Extract numeric part from flat number for sorting"""
        import re
        match = re.search(r'\d+', flat_no)
        return int(match.group()) if match else 0
    
    def add_resident(self):
        dialog = ResidentDialog(self, user_role=self.user_role)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            # Set fixed monthly charges
            data['monthly_charges'] = 500.0
            
            resident_id = self.resident_manager.add_resident(
                data['flat_no'], data['name'], data['resident_type'],
                data['mobile_no'], data['email'], data['date_joining'],
                data['cars'], data['scooters'], data['parking_slot'],
                data['monthly_charges'], data['status'], data['remarks']
            )
            
            if resident_id:
                QMessageBox.information(self, "Success", "Resident added successfully!")
                self.load_residents()
            else:
                QMessageBox.warning(self, "Error", "Failed to add resident. Flat number might already exist.")
    
    def edit_resident(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        resident_id = int(self.table.item(row, 0).text())
        
        resident = self.resident_manager.get_resident_by_id(resident_id)
        if not resident:
            QMessageBox.warning(self, "Error", "Resident not found.")
            return
            
        dialog = ResidentDialog(self, resident, user_role=self.user_role)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            # Set fixed monthly charges
            data['monthly_charges'] = 500.0
            
            success = self.resident_manager.update_resident(
                resident_id, data['flat_no'], data['name'], data['resident_type'],
                data['mobile_no'], data['email'], data['date_joining'],
                data['cars'], data['scooters'], data['parking_slot'],
                data['monthly_charges'], data['status'], data['remarks']
            )
            
            if success:
                QMessageBox.information(self, "Success", "Resident updated successfully!")
                self.load_residents()
            else:
                QMessageBox.warning(self, "Error", "Failed to update resident. Flat number might already exist.")
    
    def delete_resident(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        resident_id = int(self.table.item(row, 0).text())
        resident_name = self.table.item(row, 2).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete resident {resident_name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.resident_manager.delete_resident(resident_id)
            QMessageBox.information(self, "Success", "Resident deleted successfully!")
            self.load_residents()
    
    def load_residents(self):
        residents = self.resident_manager.get_all_residents()
        self.display_residents(residents)

class ResidentDialog(QDialog):
    def __init__(self, parent=None, resident=None, user_role=None):
        super().__init__(parent)
        self.resident = resident
        self.user_role = user_role
        self.setWindowTitle("Add Resident" if not resident else "Edit Resident")
        self.setModal(True)
        self.setup_ui()
        if resident:
            self.populate_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Flat No
        self.flat_no_input = QLineEdit()
        self.flat_no_input.setMaxLength(10)
        form_layout.addRow("Flat No*:", self.flat_no_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        form_layout.addRow("Name of Resident*:", self.name_input)
        
        # Phone No
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(15)
        form_layout.addRow("Phone No*:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMaxLength(100)
        form_layout.addRow("Email:", self.email_input)
        
        # Type (Owner/Tenant)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Owner", "Tenant"])
        form_layout.addRow("Resident Type:", self.type_combo)
        
        # Date of Joining
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date of Joining:", self.date_input)
        
        # Cars
        self.cars_input = QSpinBox()
        self.cars_input.setRange(0, 10)
        form_layout.addRow("Number of Cars:", self.cars_input)
        
        # Scooters
        self.scooters_input = QSpinBox()
        self.scooters_input.setRange(0, 10)
        form_layout.addRow("Number of Scooters:", self.scooters_input)
        
        # Parking Slot
        self.parking_input = QLineEdit()
        self.parking_input.setMaxLength(20)
        form_layout.addRow("Parking Slot:", self.parking_input)
        
        # Monthly Charges (Fixed at 500, editable only by System Admin)
        self.charges_input = QDoubleSpinBox()
        self.charges_input.setRange(0, 100000)
        self.charges_input.setDecimals(2)
        self.charges_input.setValue(500.0)  # Fixed value
        self.charges_input.setMaximumWidth(150)
        # Disable for non-System Admin users
        if self.user_role != "System Admin":
            self.charges_input.setReadOnly(True)
            self.charges_input.setEnabled(False)
        form_layout.addRow("Monthly Charges:", self.charges_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        form_layout.addRow("Status:", self.status_combo)
        
        # Remarks
        self.remarks_input = QTextEdit()
        self.remarks_input.setMaximumHeight(100)
        form_layout.addRow("Remarks:", self.remarks_input)
        
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
        self.flat_no_input.setText(self.resident.flat_no)
        self.name_input.setText(self.resident.name)
        self.phone_input.setText(self.resident.mobile_no)
        self.email_input.setText(self.resident.email)
        self.type_combo.setCurrentText(self.resident.resident_type)
        
        # Convert date string to QDate
        if self.resident.date_joining:
            date = QDate.fromString(self.resident.date_joining, "yyyy-MM-dd")
            self.date_input.setDate(date)
            
        self.cars_input.setValue(self.resident.cars or 0)
        self.scooters_input.setValue(self.resident.scooters or 0)
        self.parking_input.setText(self.resident.parking_slot or "")
        self.charges_input.setValue(self.resident.monthly_charges or 500.0)
        self.status_combo.setCurrentText(self.resident.status or "Active")
        self.remarks_input.setPlainText(self.resident.remarks or "")
    
    def get_data(self):
        return {
            'flat_no': self.flat_no_input.text().strip(),
            'name': self.name_input.text().strip(),
            'resident_type': self.type_combo.currentText(),
            'mobile_no': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'date_joining': self.date_input.date().toString("yyyy-MM-dd"),
            'cars': self.cars_input.value(),
            'scooters': self.scooters_input.value(),
            'parking_slot': self.parking_input.text().strip(),
            'monthly_charges': self.charges_input.value(),
            'status': self.status_combo.currentText(),
            'remarks': self.remarks_input.toPlainText().strip()
        }
    
    def accept(self):
        # Validate required fields
        if not self.flat_no_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Flat No is required.")
            return
            
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Name of Resident is required.")
            return
            
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Phone No is required.")
            return
        
        super().accept()