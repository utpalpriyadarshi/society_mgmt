# Advanced filter dialog for reconciliation tab
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QCheckBox, QDateEdit, QDialogButtonBox, QGroupBox)
from PyQt5.QtCore import QDate

class AdvancedFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Filter")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Ledger filters group
        ledger_group = QGroupBox("Ledger Transactions")
        ledger_layout = QFormLayout()
        
        # Amount range
        self.ledger_min_amount = QLineEdit()
        self.ledger_min_amount.setPlaceholderText("Minimum amount")
        ledger_layout.addRow("Min Amount:", self.ledger_min_amount)
        
        self.ledger_max_amount = QLineEdit()
        self.ledger_max_amount.setPlaceholderText("Maximum amount")
        ledger_layout.addRow("Max Amount:", self.ledger_max_amount)
        
        # Transaction type
        self.ledger_type = QComboBox()
        self.ledger_type.addItem("All Types")
        self.ledger_type.addItem("Payment")
        self.ledger_type.addItem("Expense")
        self.ledger_type.addItem("Payment Reversal")
        self.ledger_type.addItem("Expense Reversal")
        ledger_layout.addRow("Transaction Type:", self.ledger_type)
        
        # Category
        self.ledger_category = QLineEdit()
        self.ledger_category.setPlaceholderText("Category filter")
        ledger_layout.addRow("Category:", self.ledger_category)
        
        # Description
        self.ledger_description = QLineEdit()
        self.ledger_description.setPlaceholderText("Description contains")
        ledger_layout.addRow("Description:", self.ledger_description)
        
        # Flat number
        self.ledger_flat_no = QLineEdit()
        self.ledger_flat_no.setPlaceholderText("Flat number")
        ledger_layout.addRow("Flat No:", self.ledger_flat_no)
        
        # Date range
        date_range_layout = QHBoxLayout()
        self.ledger_start_date = QDateEdit()
        self.ledger_start_date.setDisplayFormat("yyyy-MM-dd")
        self.ledger_start_date.setDate(QDate.currentDate().addMonths(-1))
        date_range_layout.addWidget(self.ledger_start_date)
        
        date_range_layout.addWidget(QLabel("to"))
        
        self.ledger_end_date = QDateEdit()
        self.ledger_end_date.setDisplayFormat("yyyy-MM-dd")
        self.ledger_end_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.ledger_end_date)
        
        ledger_layout.addRow("Date Range:", date_range_layout)
        
        ledger_group.setLayout(ledger_layout)
        layout.addWidget(ledger_group)
        
        # Bank filters group
        bank_group = QGroupBox("Bank Entries")
        bank_layout = QFormLayout()
        
        # Amount range
        self.bank_min_amount = QLineEdit()
        self.bank_min_amount.setPlaceholderText("Minimum amount")
        bank_layout.addRow("Min Amount:", self.bank_min_amount)
        
        self.bank_max_amount = QLineEdit()
        self.bank_max_amount.setPlaceholderText("Maximum amount")
        bank_layout.addRow("Max Amount:", self.bank_max_amount)
        
        # Description
        self.bank_description = QLineEdit()
        self.bank_description.setPlaceholderText("Description contains")
        bank_layout.addRow("Description:", self.bank_description)
        
        # Reference number
        self.bank_reference = QLineEdit()
        self.bank_reference.setPlaceholderText("Reference number")
        bank_layout.addRow("Reference No:", self.bank_reference)
        
        # Date range
        bank_date_layout = QHBoxLayout()
        self.bank_start_date = QDateEdit()
        self.bank_start_date.setDisplayFormat("yyyy-MM-dd")
        self.bank_start_date.setDate(QDate.currentDate().addMonths(-1))
        bank_date_layout.addWidget(self.bank_start_date)
        
        bank_date_layout.addWidget(QLabel("to"))
        
        self.bank_end_date = QDateEdit()
        self.bank_end_date.setDisplayFormat("yyyy-MM-dd")
        self.bank_end_date.setDate(QDate.currentDate())
        bank_date_layout.addWidget(self.bank_end_date)
        
        bank_layout.addRow("Date Range:", bank_date_layout)
        
        bank_group.setLayout(bank_layout)
        layout.addWidget(bank_group)
        
        # Common filters
        common_group = QGroupBox("Common Filters")
        common_layout = QFormLayout()
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses")
        self.status_filter.addItem("Reconciled")
        self.status_filter.addItem("Unreconciled")
        common_layout.addRow("Status:", self.status_filter)
        
        # Confidence range
        confidence_layout = QHBoxLayout()
        self.min_confidence = QLineEdit()
        self.min_confidence.setPlaceholderText("0-100")
        confidence_layout.addWidget(self.min_confidence)
        
        confidence_layout.addWidget(QLabel("to"))
        
        self.max_confidence = QLineEdit()
        self.max_confidence.setPlaceholderText("0-100")
        confidence_layout.addWidget(self.max_confidence)
        
        common_layout.addRow("Confidence (%):", confidence_layout)
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def get_filter_criteria(self):
        """Return the filter criteria as a dictionary"""
        return {
            'ledger': {
                'min_amount': self.ledger_min_amount.text(),
                'max_amount': self.ledger_max_amount.text(),
                'type': self.ledger_type.currentText(),
                'category': self.ledger_category.text(),
                'description': self.ledger_description.text(),
                'flat_no': self.ledger_flat_no.text(),
                'start_date': self.ledger_start_date.date().toString("yyyy-MM-dd"),
                'end_date': self.ledger_end_date.date().toString("yyyy-MM-dd")
            },
            'bank': {
                'min_amount': self.bank_min_amount.text(),
                'max_amount': self.bank_max_amount.text(),
                'description': self.bank_description.text(),
                'reference': self.bank_reference.text(),
                'start_date': self.bank_start_date.date().toString("yyyy-MM-dd"),
                'end_date': self.bank_end_date.date().toString("yyyy-MM-dd")
            },
            'common': {
                'status': self.status_filter.currentText(),
                'min_confidence': self.min_confidence.text(),
                'max_confidence': self.max_confidence.text()
            }
        }