# gui/payment_form.py
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                            QPushButton, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QComboBox, QDateEdit, QLabel,
                            QMessageBox, QHeaderView, QFormLayout,
                            QDialog, QDialogButtonBox, QDoubleSpinBox,
                            QTextEdit, QGroupBox)
from PyQt5.QtCore import QDate
from models.ledger import LedgerManager
from models.resident import ResidentManager
from utils.form_validation import validate_form_data
from utils.resident_utils import get_sorted_flat_numbers

class PaymentForm(QWidget):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.ledger_manager = LedgerManager()
        self.resident_manager = ResidentManager()
        self.setup_ui()
        self.load_transactions()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Add Payment Button
        self.add_payment_button = QPushButton("Add Payment")
        self.add_payment_button.clicked.connect(self.add_payment)
        main_layout.addWidget(self.add_payment_button)
        
        # Table - Ledger View
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        headers = ["S.N", "Txn ID", "Date", "Flat No", "Type", "Category", "Description", 
                  "Debit", "Credit", "Balance", "Payment Mode"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
    
    def add_payment(self):
        dialog = PaymentDialog(self, self.current_user)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            txn_id = self.ledger_manager.add_transaction(
                data['date'], data['flat_no'], 'Payment', data['category'],
                data['description'], 0.0, data['amount'], data['payment_mode'],
                data['entered_by']
            )
            
            if txn_id:
                QMessageBox.information(self, "Success", "Payment recorded successfully!")
                self.load_transactions()
            else:
                QMessageBox.warning(self, "Error", "Failed to record payment.")
    
    def load_transactions(self):
        transactions = self.ledger_manager.get_all_transactions()
        
        self.table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))  # S.N
            self.table.setItem(row, 1, QTableWidgetItem(str(transaction.transaction_id)))
            self.table.setItem(row, 2, QTableWidgetItem(transaction.date))
            self.table.setItem(row, 3, QTableWidgetItem(transaction.flat_no or ""))
            self.table.setItem(row, 4, QTableWidgetItem(transaction.transaction_type))
            self.table.setItem(row, 5, QTableWidgetItem(transaction.category))
            self.table.setItem(row, 6, QTableWidgetItem(transaction.description))
            self.table.setItem(row, 7, QTableWidgetItem(str(transaction.debit)))
            self.table.setItem(row, 8, QTableWidgetItem(str(transaction.credit)))
            self.table.setItem(row, 9, QTableWidgetItem(str(transaction.balance)))
            self.table.setItem(row, 10, QTableWidgetItem(transaction.payment_mode))

class PaymentDialog(QDialog):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.ledger_manager = LedgerManager()
        self.resident_manager = ResidentManager()
        self.setWindowTitle("Record Payment")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date*:", self.date_input)
        
        # Flat No
        self.flat_no_input = QComboBox()
        self.load_residents()
        form_layout.addRow("Flat No:", self.flat_no_input)
        
        # Category
        self.category_input = QComboBox()
        self.category_input.addItems(self.ledger_manager.get_payment_categories())
        form_layout.addRow("Category*:", self.category_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.amount_input.setDecimals(2)
        form_layout.addRow("Amount*:", self.amount_input)
        
        # Payment Mode
        self.payment_mode_input = QComboBox()
        self.payment_mode_input.addItems(self.ledger_manager.get_payment_modes())
        form_layout.addRow("Payment Mode*:", self.payment_mode_input)
        
        # Reference No
        self.reference_no_input = QLineEdit()
        self.reference_no_input.setMaxLength(50)
        form_layout.addRow("Reference No:", self.reference_no_input)
        
        # Entered By (auto-filled)
        self.entered_by_input = QLineEdit()
        self.entered_by_input.setText(self.current_user or "")
        self.entered_by_input.setReadOnly(True)
        form_layout.addRow("Entered By:", self.entered_by_input)
        
        layout.addLayout(form_layout)
        
        # Refresh button for residents
        refresh_button = QPushButton("Refresh Resident List")
        refresh_button.clicked.connect(self.refresh_residents)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_layout.addWidget(button_box)
        layout.addLayout(button_layout)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.setLayout(layout)
    
    def load_residents(self):
        """Load residents into the flat no combobox in sorted order"""
        residents = self.resident_manager.get_all_residents()
        sorted_flat_numbers = get_sorted_flat_numbers(residents)
        
        self.flat_no_input.addItem("")  # Empty option
        for flat_no in sorted_flat_numbers:
            self.flat_no_input.addItem(flat_no)
    
    def refresh_residents(self):
        """Refresh the resident list in the flat no combobox"""
        # Save current selection if any
        current_selection = self.flat_no_input.currentText()
        
        # Clear and reload
        self.flat_no_input.clear()
        self.load_residents()
        
        # Restore selection if it still exists
        index = self.flat_no_input.findText(current_selection)
        if index >= 0:
            self.flat_no_input.setCurrentIndex(index)
    
    def get_data(self):
        return {
            'date': self.date_input.date().toString("yyyy-MM-dd"),
            'flat_no': self.flat_no_input.currentText() if self.flat_no_input.currentText() else None,
            'category': self.category_input.currentText(),
            'description': self.description_input.toPlainText().strip(),
            'amount': self.amount_input.value(),
            'payment_mode': self.payment_mode_input.currentText(),
            'reference_no': self.reference_no_input.text().strip(),
            'entered_by': self.current_user or "Unknown"
        }
    
    def accept(self):
        # Prepare form data for validation
        form_data = {
            'date': self.date_input,
            'category': self.category_input,
            'amount': self.amount_input,
            'payment_mode': self.payment_mode_input,
            'description': self.description_input,
            'reference_no': self.reference_no_input,
            'flat_no': self.flat_no_input
        }
        
        # Validate all form data
        if not validate_form_data(form_data, self):
            return
            
        super().accept()