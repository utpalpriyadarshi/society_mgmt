# gui/ledger_form.py
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                            QPushButton, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QComboBox, QDateEdit, QLabel,
                            QMessageBox, QHeaderView, QFormLayout,
                            QDialog, QDialogButtonBox, QDoubleSpinBox,
                            QTextEdit, QTabWidget, QGroupBox)
from PyQt5.QtCore import QDate
from models.ledger import LedgerManager
from models.resident import ResidentManager
from gui.reconciliation_tab import ReconciliationTab
from models.transaction_reversal import TransactionReversalManager
from gui.reversal_dialog import ReversalDialog

class LedgerForm(QWidget):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.ledger_manager = LedgerManager()
        self.resident_manager = ResidentManager()
        self.setup_ui()
        self.load_transactions()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Tab widget for Payments, Expenses, and Reconciliation
        self.tabs = QTabWidget()
        
        # Payment Tab
        self.payment_tab = PaymentTab(self, self.current_user)
        self.tabs.addTab(self.payment_tab, "Record Payment")
        
        # Expense Tab
        self.expense_tab = ExpenseTab(self, self.current_user)
        self.tabs.addTab(self.expense_tab, "Record Expense")
        
        # Reconciliation Tab
        self.reconciliation_tab = ReconciliationTab(self, self.current_user)
        self.tabs.addTab(self.reconciliation_tab, "Reconciliation")
        
        main_layout.addWidget(self.tabs)
        
        # Ledger Table
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        headers = ["Transaction ID", "Date", "Flat No", "Type", "Category", "Description", 
                  "Debit", "Credit", "Balance", "Payment Mode", "Entered By", "Created At", "Status"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        main_layout.addWidget(QLabel("Ledger Transactions:"))
        
        # Add buttons for transaction actions
        button_layout = QHBoxLayout()
        self.reverse_button = QPushButton("Reverse Selected Transaction")
        self.reverse_button.clicked.connect(self.reverse_transaction)
        self.reverse_button.setEnabled(False)
        button_layout.addWidget(self.reverse_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
        
        # Connect table selection to enable/disable buttons
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_transactions(self):
        transactions = self.ledger_manager.get_all_transactions()
        
        self.table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(transaction.transaction_id))
            self.table.setItem(row, 1, QTableWidgetItem(transaction.date))
            self.table.setItem(row, 2, QTableWidgetItem(transaction.flat_no or ""))
            self.table.setItem(row, 3, QTableWidgetItem(transaction.transaction_type))
            self.table.setItem(row, 4, QTableWidgetItem(transaction.category))
            self.table.setItem(row, 5, QTableWidgetItem(transaction.description))
            self.table.setItem(row, 6, QTableWidgetItem(str(transaction.debit)))
            self.table.setItem(row, 7, QTableWidgetItem(str(transaction.credit)))
            self.table.setItem(row, 8, QTableWidgetItem(str(transaction.balance)))
            self.table.setItem(row, 9, QTableWidgetItem(transaction.payment_mode))
            self.table.setItem(row, 10, QTableWidgetItem(transaction.entered_by))
            self.table.setItem(row, 11, QTableWidgetItem(transaction.created_at or ""))
            self.table.setItem(row, 12, QTableWidgetItem(transaction.reconciliation_status))

    def on_selection_changed(self):
        """Enable/disable buttons based on table selection"""
        selected_rows = self.table.selectionModel().selectedRows()
        self.reverse_button.setEnabled(len(selected_rows) == 1)
    
    def reverse_transaction(self):
        """Open reversal dialog for selected transaction"""
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 1:
            QMessageBox.warning(self, "Selection Error", "Please select exactly one transaction to reverse.")
            return
        
        row = selected_rows[0].row()
        transaction_id = self.table.item(row, 0).text()
        
        # Get transaction details
        transactions = self.ledger_manager.get_all_transactions()
        selected_transaction = None
        for txn in transactions:
            if txn.transaction_id == transaction_id:
                selected_transaction = txn
                break
        
        if not selected_transaction:
            QMessageBox.warning(self, "Error", "Could not find transaction details.")
            return
        
        # Check if transaction can be reversed
        can_reverse, reason = self.ledger_manager.can_reverse_transaction(transaction_id)
        if not can_reverse:
            QMessageBox.warning(self, "Error", reason)
            return
        
        # Open reversal dialog
        dialog = ReversalDialog(transaction_id, selected_transaction, self.current_user, self)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh the ledger display
            self.load_transactions()

class PaymentTab(QWidget):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.ledger_form = parent  # Store reference to parent LedgerForm
        self.current_user = current_user
        self.ledger_manager = LedgerManager()
        self.resident_manager = ResidentManager()
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
        
        # Entered By (auto-filled)
        self.entered_by_input = QLineEdit()
        self.entered_by_input.setText(self.current_user or "")
        self.entered_by_input.setReadOnly(True)
        form_layout.addRow("Entered By:", self.entered_by_input)
        
        layout.addLayout(form_layout)
        
        # Save Button
        self.save_button = QPushButton("Record Payment")
        self.save_button.clicked.connect(self.record_payment)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
    
    def load_residents(self):
        """Load residents into the flat no combobox"""
        residents = self.resident_manager.get_all_residents()
        self.flat_no_input.addItem("")  # Empty option
        for resident in residents:
            self.flat_no_input.addItem(resident.flat_no)
    
    def record_payment(self):
        # Validate required fields
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than zero.")
            return
        
        transaction_id = self.ledger_manager.add_transaction(
            self.date_input.date().toString("yyyy-MM-dd"),
            self.flat_no_input.currentText() if self.flat_no_input.currentText() else None,
            "Payment",
            self.category_input.currentText(),
            self.description_input.toPlainText().strip(),
            0.0,  # Debit (payments are credits to the society)
            self.amount_input.value(),  # Credit
            self.payment_mode_input.currentText(),
            self.current_user or "Unknown"
        )
        
        if transaction_id:
            QMessageBox.information(self, "Success", f"Payment recorded successfully!\nTransaction ID: {transaction_id}")
            # Refresh the ledger display
            self.ledger_form.load_transactions()
            # Clear form
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", "Failed to record payment.")
    
    def clear_form(self):
        self.date_input.setDate(QDate.currentDate())
        self.flat_no_input.setCurrentIndex(0)
        self.category_input.setCurrentIndex(0)
        self.description_input.clear()
        self.amount_input.setValue(0.0)
        self.payment_mode_input.setCurrentIndex(0)

class ExpenseTab(QWidget):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.ledger_form = parent  # Store reference to parent LedgerForm
        self.current_user = current_user
        self.ledger_manager = LedgerManager()
        self.resident_manager = ResidentManager()
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
        
        # Flat No (optional for expenses)
        self.flat_no_input = QComboBox()
        self.load_residents()
        form_layout.addRow("Flat No:", self.flat_no_input)
        
        # Category
        self.category_input = QComboBox()
        self.category_input.addItems(self.ledger_manager.get_expense_categories())
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
        
        # Entered By (auto-filled)
        self.entered_by_input = QLineEdit()
        self.entered_by_input.setText(self.current_user or "")
        self.entered_by_input.setReadOnly(True)
        form_layout.addRow("Entered By:", self.entered_by_input)
        
        layout.addLayout(form_layout)
        
        # Save Button
        self.save_button = QPushButton("Record Expense")
        self.save_button.clicked.connect(self.record_expense)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
    
    def load_residents(self):
        """Load residents into the flat no combobox"""
        residents = self.resident_manager.get_all_residents()
        self.flat_no_input.addItem("")  # Empty option
        for resident in residents:
            self.flat_no_input.addItem(resident.flat_no)
    
    def record_expense(self):
        # Validate required fields
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than zero.")
            return
        
        transaction_id = self.ledger_manager.add_transaction(
            self.date_input.date().toString("yyyy-MM-dd"),
            self.flat_no_input.currentText() if self.flat_no_input.currentText() else None,
            "Expense",
            self.category_input.currentText(),
            self.description_input.toPlainText().strip(),
            self.amount_input.value(),  # Debit (expenses are debits to the society)
            0.0,  # Credit
            self.payment_mode_input.currentText(),
            self.current_user or "Unknown"
        )
        
        if transaction_id:
            QMessageBox.information(self, "Success", f"Expense recorded successfully!\nTransaction ID: {transaction_id}")
            # Refresh the ledger display
            self.ledger_form.load_transactions()
            # Clear form
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", "Failed to record expense.")
    
    def clear_form(self):
        self.date_input.setDate(QDate.currentDate())
        self.flat_no_input.setCurrentIndex(0)
        self.category_input.setCurrentIndex(0)
        self.description_input.clear()
        self.amount_input.setValue(0.0)
        self.payment_mode_input.setCurrentIndex(0)