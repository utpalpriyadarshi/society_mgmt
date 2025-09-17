# gui/enhanced_resident_form.py
"""
Enhanced Resident Form with advanced search and filtering capabilities.
"""

from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                            QPushButton, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QComboBox, QDateEdit, QLabel,
                            QMessageBox, QHeaderView, QFormLayout,
                            QDialog, QDialogButtonBox, QDoubleSpinBox,
                            QSpinBox, QTextEdit, QTabWidget, QGroupBox,
                            QCheckBox, QScrollArea, QFrame)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIntValidator
from models.resident import ResidentManager
from gui.profile_photo_widget import ProfilePhotoWidget
from gui.domestic_help_widget import DomesticHelpWidget


class EnhancedResidentForm(QWidget):
    def __init__(self, parent=None, user_role=None, current_user=None):
        super().__init__(parent)
        self.resident_manager = ResidentManager()
        self.user_role = user_role
        self.current_user = current_user
        self.current_resident_id = None
        self.advanced_filters = {}
        self.current_sort_column = None
        self.current_sort_order = "ASC"
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
        
        # Advanced search toggle button
        self.advanced_search_toggle = QPushButton("Advanced Search ▼")
        self.advanced_search_toggle.setCheckable(True)
        self.advanced_search_toggle.toggled.connect(self.toggle_advanced_search)
        search_layout.addWidget(self.advanced_search_toggle)
        
        main_layout.addLayout(search_layout)
        
        # Advanced search panel (initially hidden)
        self.advanced_search_panel = QFrame()
        self.advanced_search_panel.setFrameStyle(QFrame.StyledPanel)
        self.advanced_search_panel.setVisible(False)
        self.setup_advanced_search_panel()
        main_layout.addWidget(self.advanced_search_panel)
        
        # Quick filter buttons
        quick_filter_layout = QHBoxLayout()
        self.all_active_button = QPushButton("All Active")
        self.all_active_button.clicked.connect(lambda: self.apply_quick_filter("all_active"))
        quick_filter_layout.addWidget(self.all_active_button)
        
        self.with_vehicles_button = QPushButton("With Vehicles")
        self.with_vehicles_button.clicked.connect(lambda: self.apply_quick_filter("with_vehicles"))
        quick_filter_layout.addWidget(self.with_vehicles_button)
        
        self.vacant_flats_button = QPushButton("Vacant Flats")
        self.vacant_flats_button.clicked.connect(lambda: self.apply_quick_filter("vacant_flats"))
        quick_filter_layout.addWidget(self.vacant_flats_button)
        
        self.clear_filters_button = QPushButton("Clear Filters")
        self.clear_filters_button.clicked.connect(self.clear_filters)
        quick_filter_layout.addWidget(self.clear_filters_button)
        
        main_layout.addLayout(quick_filter_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Resident")
        self.add_button.clicked.connect(self.add_resident)
        action_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Resident")
        self.edit_button.clicked.connect(self.edit_resident)
        self.edit_button.setEnabled(False)
        action_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Resident")
        self.delete_button.clicked.connect(self.delete_resident)
        self.delete_button.setEnabled(False)
        action_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(action_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Including car and scooter info
        headers = ["ID", "Flat No", "Name", "Phone No", "Email", "Car Nos", "Scooter Nos", "Cars", "Scooters"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
    
    def setup_advanced_search_panel(self):
        """Setup the advanced search panel with filter options."""
        layout = QVBoxLayout()
        
        # Create scroll area for filters
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Filter by resident type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Resident Type:"))
        self.resident_type_filter = QComboBox()
        self.resident_type_filter.addItem("All Types", "")
        self.resident_type_filter.addItem("Owner", "Owner")
        self.resident_type_filter.addItem("Tenant", "Tenant")
        self.resident_type_filter.addItem("Vacant", "Vacant")
        type_layout.addWidget(self.resident_type_filter)
        type_layout.addStretch()
        scroll_layout.addLayout(type_layout)
        
        # Filter by status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", "")
        self.status_filter.addItem("Active", "Active")
        self.status_filter.addItem("Inactive", "Inactive")
        status_layout.addWidget(self.status_filter)
        status_layout.addStretch()
        scroll_layout.addLayout(status_layout)
        
        # Vehicle filters
        vehicle_layout = QHBoxLayout()
        vehicle_layout.addWidget(QLabel("Vehicles:"))
        self.has_cars_checkbox = QCheckBox("Has Cars")
        self.has_cars_checkbox.stateChanged.connect(self.on_vehicle_filter_changed)
        vehicle_layout.addWidget(self.has_cars_checkbox)
        
        self.has_scooters_checkbox = QCheckBox("Has Scooters")
        self.has_scooters_checkbox.stateChanged.connect(self.on_vehicle_filter_changed)
        vehicle_layout.addWidget(self.has_scooters_checkbox)
        vehicle_layout.addStretch()
        scroll_layout.addLayout(vehicle_layout)
        
        # Vacant flat filters
        vacant_layout = QHBoxLayout()
        vacant_layout.addWidget(QLabel("Vacant Flats:"))
        self.is_vacant_checkbox = QCheckBox("Only Vacant")
        self.is_vacant_checkbox.stateChanged.connect(self.on_vacant_filter_changed)
        vacant_layout.addWidget(self.is_vacant_checkbox)
        vacant_layout.addStretch()
        scroll_layout.addLayout(vacant_layout)
        
        # Date range filters
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Joined:"))
        self.date_from_filter = QDateEdit()
        self.date_from_filter.setDisplayFormat("yyyy-MM-dd")
        self.date_from_filter.setCalendarPopup(True)
        self.date_from_filter.setDate(QDate.currentDate().addYears(-1))
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.date_from_filter)
        
        self.date_to_filter = QDateEdit()
        self.date_to_filter.setDisplayFormat("yyyy-MM-dd")
        self.date_to_filter.setCalendarPopup(True)
        self.date_to_filter.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.date_to_filter)
        
        self.apply_date_filter_button = QPushButton("Apply Date Filter")
        self.apply_date_filter_button.clicked.connect(self.apply_date_filters)
        date_layout.addWidget(self.apply_date_filter_button)
        date_layout.addStretch()
        scroll_layout.addLayout(date_layout)
        
        # Apply filters button
        apply_layout = QHBoxLayout()
        self.apply_filters_button = QPushButton("Apply Filters")
        self.apply_filters_button.clicked.connect(self.apply_advanced_filters)
        apply_layout.addWidget(self.apply_filters_button)
        
        self.reset_filters_button = QPushButton("Reset Filters")
        self.reset_filters_button.clicked.connect(self.reset_advanced_filters)
        apply_layout.addWidget(self.reset_filters_button)
        apply_layout.addStretch()
        scroll_layout.addLayout(apply_layout)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        self.advanced_search_panel.setLayout(layout)
    
    def toggle_advanced_search(self, checked):
        """Toggle visibility of advanced search panel."""
        self.advanced_search_panel.setVisible(checked)
        self.advanced_search_toggle.setText("Advanced Search ▲" if checked else "Advanced Search ▼")
    
    def on_vehicle_filter_changed(self, state):
        """Handle vehicle filter checkbox changes."""
        # Apply filters immediately when checkbox state changes
        self.apply_advanced_filters()
    
    def on_vacant_filter_changed(self, state):
        """Handle vacant filter checkbox changes."""
        # Apply filters immediately when checkbox state changes
        self.apply_advanced_filters()
    
    def apply_date_filters(self):
        """Apply date range filters."""
        self.apply_advanced_filters()
    
    def apply_advanced_filters(self):
        """Apply all advanced filters and update the resident list."""
        # Build filters dictionary
        filters = {}
        
        # Text search
        search_text = self.search_input.text().strip()
        if search_text:
            filters['search_term'] = search_text
        
        # Resident type filter
        resident_type = self.resident_type_filter.currentData()
        if resident_type:
            filters['resident_type'] = resident_type
        
        # Status filter
        status = self.status_filter.currentData()
        if status:
            filters['status'] = status
        
        # Vehicle filters
        if self.has_cars_checkbox.isChecked():
            filters['has_cars'] = True
        elif not self.has_cars_checkbox.isChecked() and not self.has_cars_checkbox.isTristate():
            filters['has_cars'] = False
            
        if self.has_scooters_checkbox.isChecked():
            filters['has_scooters'] = True
        elif not self.has_scooters_checkbox.isChecked() and not self.has_scooters_checkbox.isTristate():
            filters['has_scooters'] = False
        
        # Vacant flat filter
        if self.is_vacant_checkbox.isChecked():
            filters['is_vacant'] = True
        elif not self.is_vacant_checkbox.isChecked() and not self.is_vacant_checkbox.isTristate():
            filters['is_vacant'] = False
        
        # Date range filters
        if self.date_from_filter.date() != QDate.currentDate().addYears(-1):
            filters['date_from'] = self.date_from_filter.date().toString("yyyy-MM-dd")
        
        if self.date_to_filter.date() != QDate.currentDate():
            filters['date_to'] = self.date_to_filter.date().toString("yyyy-MM-dd")
        
        # Store filters for future use
        self.advanced_filters = filters
        
        # Apply filters
        try:
            residents = self.resident_manager.advanced_search_residents(
                filters=filters,
                sort_by=self.current_sort_column,
                sort_order=self.current_sort_order
            )
            self.display_residents(residents)
        except Exception as e:
            from utils.database_error_handler import handle_database_error
            handle_database_error(self, e, "search residents")
    
    def reset_advanced_filters(self):
        """Reset all advanced filters to their default state."""
        self.search_input.clear()
        self.resident_type_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.has_cars_checkbox.setCheckState(Qt.Unchecked)
        self.has_scooters_checkbox.setCheckState(Qt.Unchecked)
        self.is_vacant_checkbox.setCheckState(Qt.Unchecked)
        self.date_from_filter.setDate(QDate.currentDate().addYears(-1))
        self.date_to_filter.setDate(QDate.currentDate())
        self.advanced_filters = {}
        self.load_residents()
    
    def apply_quick_filter(self, filter_type):
        """Apply predefined quick filters."""
        if filter_type == "all_active":
            self.reset_advanced_filters()
            self.status_filter.setCurrentIndex(1)  # Active
            self.apply_advanced_filters()
        elif filter_type == "with_vehicles":
            self.reset_advanced_filters()
            self.has_cars_checkbox.setCheckState(Qt.Checked)
            self.apply_advanced_filters()
        elif filter_type == "vacant_flats":
            self.reset_advanced_filters()
            self.resident_type_filter.setCurrentIndex(3)  # Vacant
            self.apply_advanced_filters()
    
    def clear_filters(self):
        """Clear all filters and show all residents."""
        self.reset_advanced_filters()
    
    def on_header_clicked(self, column):
        """Handle header click for sorting."""
        # Map column index to database column name
        column_mapping = {
            0: 'id',
            1: 'flat_no',
            2: 'name',
            3: 'mobile_no',
            4: 'email',
            5: 'car_numbers',
            6: 'scooter_numbers',
            7: 'cars',
            8: 'scooters'
        }
        
        if column in column_mapping:
            sort_column = column_mapping[column]
            
            # Toggle sort order if clicking the same column
            if self.current_sort_column == sort_column:
                self.current_sort_order = "DESC" if self.current_sort_order == "ASC" else "ASC"
            else:
                self.current_sort_column = sort_column
                self.current_sort_order = "ASC"
            
            # Apply sorting with current filters
            self.apply_advanced_filters()
    
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
            # If no text and no advanced filters, load all residents
            if not self.advanced_filters:
                self.load_residents()
            else:
                # Apply existing advanced filters
                self.apply_advanced_filters()
            return
            
        try:
            residents = self.resident_manager.search_residents(text)
            self.display_residents(residents)
        except Exception as e:
            from utils.database_error_handler import handle_database_error
            handle_database_error(self, e, "search residents")

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
            # Display car numbers (first few if many)
            car_numbers = resident.car_numbers or ""
            if car_numbers:
                # Handle both 
 and 
 line endings
                normalized_car_numbers = car_numbers.replace('\r\n', '\n')
                car_list = [cn.strip() for cn in normalized_car_numbers.split('\n') if cn.strip()]
                display_cars = ", ".join(car_list[:3])  # Show first 3 car numbers
                if len(car_list) > 3:
                    display_cars += f" (+{len(car_list)-3} more)"
            else:
                display_cars = ""
            self.table.setItem(row, 5, QTableWidgetItem(display_cars))
            
            # Display scooter numbers (first few if many)
            scooter_numbers = resident.scooter_numbers or ""
            if scooter_numbers:
                # Handle both 
 and 
 line endings
                normalized_scooter_numbers = scooter_numbers.replace('\r\n', '\n')
                scooter_list = [sn.strip() for sn in normalized_scooter_numbers.split('\n') if sn.strip()]
                display_scooters = ", ".join(scooter_list[:3])  # Show first 3 scooter numbers
                if len(scooter_list) > 3:
                    display_scooters += f" (+{len(scooter_list)-3} more)"
            else:
                display_scooters = ""
            self.table.setItem(row, 6, QTableWidgetItem(display_scooters))
            
            # Display counts
            self.table.setItem(row, 7, QTableWidgetItem(str(resident.cars) if resident.cars else "0"))
            self.table.setItem(row, 8, QTableWidgetItem(str(resident.scooters) if resident.scooters else "0"))
            
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
            
            try:
                resident_id = self.resident_manager.add_resident(
                    data['flat_no'], data['name'], data['resident_type'],
                    data['mobile_no'], data['email'], data['date_joining'],
                    data['cars'], data['scooters'], data['parking_slot'],
                    data['car_numbers'], data['scooter_numbers'],
                    data['monthly_charges'], data['status'], data['remarks'],
                    self.current_user,  # Pass current user for audit logging
                    data.get('vacancy_reason'), data.get('expected_occupancy_date'),
                    data.get('last_maintenance_date'), data.get('maintenance_person_name'),
                    data.get('maintenance_person_phone')
                )
                
                if resident_id:
                    QMessageBox.information(self, "Success", "Resident added successfully!")
                    self.load_residents()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add resident. Flat number might already exist.")
            except Exception as e:
                from utils.database_error_handler import handle_database_error
                handle_database_error(self, e, "add resident")
    
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
            
            try:
                success = self.resident_manager.update_resident(
                    resident_id, data['flat_no'], data['name'], data['resident_type'],
                    data['mobile_no'], data['email'], data['date_joining'],
                    data['cars'], data['scooters'], data['parking_slot'],
                    data['car_numbers'], data['scooter_numbers'],
                    data['monthly_charges'], data['status'], data['remarks'],
                    self.current_user,  # Pass current user for audit logging
                    data.get('vacancy_reason'), data.get('expected_occupancy_date'),
                    data.get('last_maintenance_date'), data.get('maintenance_person_name'),
                    data.get('maintenance_person_phone')
                )
                
                if success:
                    QMessageBox.information(self, "Success", "Resident updated successfully!")
                    self.load_residents()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update resident. Flat number might already exist.")
            except Exception as e:
                from utils.database_error_handler import handle_database_error
                handle_database_error(self, e, "update resident")
    
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
            try:
                self.resident_manager.delete_resident(resident_id, self.current_user)  # Pass current user for audit logging
                QMessageBox.information(self, "Success", "Resident deleted successfully!")
                self.load_residents()
            except Exception as e:
                from utils.database_error_handler import handle_database_error
                handle_database_error(self, e, "delete resident")
    
    def load_residents(self):
        try:
            residents = self.resident_manager.get_all_residents()
            self.display_residents(residents)
        except Exception as e:
            from utils.database_error_handler import handle_database_error
            handle_database_error(self, e, "load residents")


class ResidentDialog(QDialog):
    def __init__(self, parent=None, resident=None, user_role=None):
        super().__init__(parent)
        self.resident = resident
        self.user_role = user_role
        self.domestic_help_widget = None
        self.setWindowTitle("Add Resident" if not resident else "Edit Resident")
        self.setModal(True)
        self.setup_ui()
        if resident:
            self.populate_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Basic Info Tab
        self.basic_info_tab = QWidget()
        self.setup_basic_info_tab()
        self.tab_widget.addTab(self.basic_info_tab, "Basic Info")
        
        # Vehicle Info Tab
        self.vehicle_info_tab = QWidget()
        self.setup_vehicle_info_tab()
        self.tab_widget.addTab(self.vehicle_info_tab, "Vehicle Info")
        
        # Vacant Flat Info Tab (only visible for vacant flats)
        self.vacant_info_tab = QWidget()
        self.setup_vacant_info_tab()
        self.tab_widget.addTab(self.vacant_info_tab, "Vacant Info")
        self.vacant_info_tab.setVisible(False)  # Hide by default
        
        # Domestic Help Tab
        self.domestic_help_tab = QWidget()
        self.setup_domestic_help_tab()
        self.tab_widget.addTab(self.domestic_help_tab, "Domestic Help")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def setup_basic_info_tab(self):
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Profile photo widget
        self.profile_photo_widget = ProfilePhotoWidget(resident_id=self.resident.id if self.resident else None)
        layout.addRow("Profile Photo:", self.profile_photo_widget)
        
        # Flat No
        self.flat_no_input = QLineEdit()
        self.flat_no_input.setMaxLength(10)
        self.flat_no_input.setMaximumWidth(150)
        layout.addRow("Flat No*:", self.flat_no_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        layout.addRow("Name of Resident*:", self.name_input)
        
        # Phone No
        self.phone_input = QLineEdit()
        self.phone_input.setMaxLength(15)
        layout.addRow("Phone No*:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setMaxLength(100)
        layout.addRow("Email:", self.email_input)
        
        # Type (Owner/Tenant/Vacant)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Owner", "Tenant", "Vacant"])
        self.type_combo.currentTextChanged.connect(self.on_resident_type_changed)
        layout.addRow("Resident Type:", self.type_combo)
        
        # Date of Joining
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("Date of Joining:", self.date_input)
        
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
        layout.addRow("Monthly Charges:", self.charges_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        layout.addRow("Status:", self.status_combo)
        
        # Remarks
        self.remarks_input = QTextEdit()
        self.remarks_input.setMaximumHeight(100)
        layout.addRow("Remarks:", self.remarks_input)
        
        self.basic_info_tab.setLayout(layout)
    
    def setup_vehicle_info_tab(self):
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Cars
        self.cars_input = QSpinBox()
        self.cars_input.setRange(0, 10)
        layout.addRow("Number of Cars:", self.cars_input)
        
        # Car Numbers
        self.car_numbers_input = QTextEdit()
        self.car_numbers_input.setMaximumHeight(60)
        self.car_numbers_input.setPlaceholderText("Enter car registration numbers, one per line")
        layout.addRow("Car Numbers:", self.car_numbers_input)
        
        # Scooters
        self.scooters_input = QSpinBox()
        self.scooters_input.setRange(0, 10)
        layout.addRow("Number of Scooters:", self.scooters_input)
        
        # Scooter Numbers
        self.scooter_numbers_input = QTextEdit()
        self.scooter_numbers_input.setMaximumHeight(60)
        self.scooter_numbers_input.setPlaceholderText("Enter scooter registration numbers, one per line")
        layout.addRow("Scooter Numbers:", self.scooter_numbers_input)
        
        # Parking Slot
        self.parking_input = QLineEdit()
        self.parking_input.setMaxLength(20)
        layout.addRow("Parking Slot:", self.parking_input)
        
        self.vehicle_info_tab.setLayout(layout)
    
    def setup_vacant_info_tab(self):
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Vacancy Reason
        self.vacancy_reason_input = QComboBox()
        self.vacancy_reason_input.addItems([
            "", "Under Construction", "For Sale", "For Rent", "Owner Away", "Tenant Moved Out", "Other"
        ])
        layout.addRow("Vacancy Reason:", self.vacancy_reason_input)
        
        # Expected Occupancy Date
        self.expected_occupancy_date_input = QDateEdit()
        self.expected_occupancy_date_input.setDisplayFormat("yyyy-MM-dd")
        self.expected_occupancy_date_input.setCalendarPopup(True)
        self.expected_occupancy_date_input.setDate(QDate.currentDate())
        layout.addRow("Expected Occupancy Date:", self.expected_occupancy_date_input)
        
        # Last Maintenance Date
        self.last_maintenance_date_input = QDateEdit()
        self.last_maintenance_date_input.setDisplayFormat("yyyy-MM-dd")
        self.last_maintenance_date_input.setCalendarPopup(True)
        self.last_maintenance_date_input.setDate(QDate.currentDate())
        layout.addRow("Last Maintenance Date:", self.last_maintenance_date_input)
        
        # Maintenance Person Name
        self.maintenance_person_name_input = QLineEdit()
        self.maintenance_person_name_input.setMaxLength(100)
        layout.addRow("Maintenance Person Name:", self.maintenance_person_name_input)
        
        # Maintenance Person Phone
        self.maintenance_person_phone_input = QLineEdit()
        self.maintenance_person_phone_input.setMaxLength(15)
        layout.addRow("Maintenance Person Phone:", self.maintenance_person_phone_input)
        
        self.vacant_info_tab.setLayout(layout)
    
    def setup_domestic_help_tab(self):
        layout = QVBoxLayout()
        self.domestic_help_widget = DomesticHelpWidget(
            resident_id=self.resident.id if self.resident else None,
            user_role=self.user_role
        )
        layout.addWidget(self.domestic_help_widget)
        self.domestic_help_tab.setLayout(layout)
    
    def on_resident_type_changed(self, text):
        """Show/hide vacant info tab based on resident type"""
        if text == "Vacant":
            self.vacant_info_tab.setVisible(True)
            self.tab_widget.setTabEnabled(self.tab_widget.indexOf(self.vehicle_info_tab), False)
        else:
            self.vacant_info_tab.setVisible(False)
            self.tab_widget.setTabEnabled(self.tab_widget.indexOf(self.vehicle_info_tab), True)
    
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
        self.car_numbers_input.setPlainText(self.resident.car_numbers or "")
        self.scooters_input.setValue(self.resident.scooters or 0)
        self.scooter_numbers_input.setPlainText(self.resident.scooter_numbers or "")
        self.parking_input.setText(self.resident.parking_slot or "")
        self.charges_input.setValue(self.resident.monthly_charges or 500.0)
        self.status_combo.setCurrentText(self.resident.status or "Active")
        self.remarks_input.setPlainText(self.resident.remarks or "")
        
        # Set profile photo if available
        if self.resident.profile_photo_path:
            self.profile_photo_widget.set_photo(self.resident.profile_photo_path)
        
        # Populate vacant flat information if applicable
        if self.resident.resident_type == "Vacant":
            self.vacancy_reason_input.setCurrentText(self.resident.vacancy_reason or "")
            if self.resident.expected_occupancy_date:
                date = QDate.fromString(self.resident.expected_occupancy_date, "yyyy-MM-dd")
                self.expected_occupancy_date_input.setDate(date)
            if self.resident.last_maintenance_date:
                date = QDate.fromString(self.resident.last_maintenance_date, "yyyy-MM-dd")
                self.last_maintenance_date_input.setDate(date)
            self.maintenance_person_name_input.setText(self.resident.maintenance_person_name or "")
            self.maintenance_person_phone_input.setText(self.resident.maintenance_person_phone or "")
            
            # Show vacant info tab
            self.vacant_info_tab.setVisible(True)
            self.tab_widget.setTabEnabled(self.tab_widget.indexOf(self.vehicle_info_tab), False)
        
        # Load domestic help data
        if self.domestic_help_widget and self.resident.id:
            self.domestic_help_widget.load_domestic_help()
    
    def get_data(self):
        data = {
            'flat_no': self.flat_no_input.text().strip(),
            'name': self.name_input.text().strip(),
            'resident_type': self.type_combo.currentText(),
            'mobile_no': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'date_joining': self.date_input.date().toString("yyyy-MM-dd"),
            'cars': self.cars_input.value(),
            'car_numbers': self.car_numbers_input.toPlainText().strip(),
            'scooters': self.scooters_input.value(),
            'scooter_numbers': self.scooter_numbers_input.toPlainText().strip(),
            'parking_slot': self.parking_input.text().strip(),
            'monthly_charges': self.charges_input.value(),
            'status': self.status_combo.currentText(),
            'remarks': self.remarks_input.toPlainText().strip()
        }
        
        # Add vacant flat information if resident type is vacant
        if self.type_combo.currentText() == "Vacant":
            data['vacancy_reason'] = self.vacancy_reason_input.currentText()
            data['expected_occupancy_date'] = self.expected_occupancy_date_input.date().toString("yyyy-MM-dd")
            data['last_maintenance_date'] = self.last_maintenance_date_input.date().toString("yyyy-MM-dd")
            data['maintenance_person_name'] = self.maintenance_person_name_input.text().strip()
            data['maintenance_person_phone'] = self.maintenance_person_phone_input.text().strip()
        
        return data
    
    def accept(self):
        # Validate required fields
        if not self.flat_no_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Flat No is required.")
            self.tab_widget.setCurrentIndex(0)  # Switch to basic info tab
            self.flat_no_input.setFocus()
            return
            
        if not self.name_input.text().strip() and self.type_combo.currentText() != "Vacant":
            QMessageBox.warning(self, "Validation Error", "Name of Resident is required.")
            self.tab_widget.setCurrentIndex(0)  # Switch to basic info tab
            self.name_input.setFocus()
            return
            
        if not self.phone_input.text().strip() and self.type_combo.currentText() != "Vacant":
            QMessageBox.warning(self, "Validation Error", "Phone No is required.")
            self.tab_widget.setCurrentIndex(0)  # Switch to basic info tab
            self.phone_input.setFocus()
            return
        
        super().accept()