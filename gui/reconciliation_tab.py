# gui/reconciliation_tab.py
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QDateEdit, 
                            QLabel, QMessageBox, QHeaderView, QFormLayout, QFileDialog,
                            QTextEdit, QTabWidget, QGroupBox, QSplitter, QAbstractItemView,
                            QProgressBar, QCheckBox)
from PyQt5.QtCore import QDate, Qt
import csv
from datetime import datetime
import re
from models.bank_statement import BankStatementManager, ReconciliationManager
from models.ledger import LedgerManager

class ReconciliationTab(QWidget):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.ledger_manager = LedgerManager()
        self.bank_manager = BankStatementManager()
        self.reconciliation_manager = ReconciliationManager()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Date range selectors
        control_layout.addWidget(QLabel("Start Date:"))
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        control_layout.addWidget(self.start_date_input)
        
        control_layout.addWidget(QLabel("End Date:"))
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        control_layout.addWidget(self.end_date_input)
        
        # Import button
        self.import_button = QPushButton("Import Bank Statement")
        self.import_button.clicked.connect(self.import_bank_statement)
        control_layout.addWidget(self.import_button)
        
        # Find matches button
        self.find_matches_button = QPushButton("Find Matches")
        self.find_matches_button.clicked.connect(self.find_matches)
        control_layout.addWidget(self.find_matches_button)
        
        # Reconcile selected button
        self.reconcile_button = QPushButton("Mark Selected as Matched")
        self.reconcile_button.clicked.connect(self.reconcile_selected)
        control_layout.addWidget(self.reconcile_button)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Splitter for ledger and bank tables
        splitter = QSplitter(Qt.Horizontal)
        
        # Ledger transactions table
        ledger_group = QGroupBox("Ledger Transactions")
        ledger_layout = QVBoxLayout()
        
        self.ledger_table = QTableWidget()
        self.ledger_table.setColumnCount(13)
        headers = ["ID", "Transaction ID", "Date", "Flat No", "Type", "Category", "Description", 
                  "Debit", "Credit", "Balance", "Payment Mode", "Status", "Select"]
        self.ledger_table.setHorizontalHeaderLabels(headers)
        self.ledger_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ledger_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        ledger_layout.addWidget(self.ledger_table)
        
        ledger_group.setLayout(ledger_layout)
        splitter.addWidget(ledger_group)
        
        # Bank statement entries table
        bank_group = QGroupBox("Bank Statement Entries")
        bank_layout = QVBoxLayout()
        
        self.bank_table = QTableWidget()
        self.bank_table.setColumnCount(9)
        headers = ["ID", "Date", "Description", "Amount", "Balance", "Reference", "Import Date", "Status", "Select"]
        self.bank_table.setHorizontalHeaderLabels(headers)
        self.bank_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.bank_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        bank_layout.addWidget(self.bank_table)
        
        bank_group.setLayout(bank_layout)
        splitter.addWidget(bank_group)
        
        # Set equal sizes for both tables
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
        # Summary section
        summary_group = QGroupBox("Reconciliation Summary")
        summary_layout = QHBoxLayout()
        
        self.summary_label = QLabel("Select a date range and click 'Find Matches' to begin reconciliation")
        summary_layout.addWidget(self.summary_label)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        self.setLayout(main_layout)
    
    def import_bank_statement(self):
        """Import bank statement from CSV or PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Bank Statement File", "", "Bank Statements (*.csv *.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            # Check file extension
            if file_path.lower().endswith('.csv'):
                self.import_csv_statement(file_path)
            elif file_path.lower().endswith('.pdf'):
                self.import_pdf_statement(file_path)
            else:
                QMessageBox.warning(self, "Import Error", "Unsupported file format. Please select a CSV or PDF file.")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing bank statement: {str(e)}\nFile: {file_path}")
    
    def import_csv_statement(self, file_path):
        """Import bank statement from CSV file"""
        entries = []
        with open(file_path, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Try to map common column names
            date_field = None
            description_field = None
            amount_field = None
            balance_field = None
            reference_field = None
            
            # Look for common field names
            for field in reader.fieldnames:
                field_lower = field.lower().strip()
                if not date_field and field_lower in ['date', 'transaction date', 'txn date']:
                    date_field = field
                elif not description_field and field_lower in ['description', 'details', 'narration']:
                    description_field = field
                elif not amount_field and field_lower in ['amount', 'debit', 'credit']:
                    amount_field = field
                elif not balance_field and field_lower in ['balance', 'closing balance']:
                    balance_field = field
                elif not reference_field and field_lower in ['reference', 'ref', 'transaction id']:
                    reference_field = field
            
            # If we couldn't auto-detect, ask user to map fields
            if not all([date_field, description_field, amount_field]):
                QMessageBox.warning(self, "Import Error", 
                                  "Could not automatically detect required fields. Please ensure your CSV has columns for Date, Description, and Amount.")
                return
            
            for row in reader:
                # Parse date
                try:
                    date_str = row[date_field]
                    # Try different date formats
                    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    
                    if not parsed_date:
                        continue  # Skip rows with invalid dates
                except:
                    continue  # Skip rows with invalid dates
                
                # Parse amount
                try:
                    amount_str = row[amount_field].replace(',', '').replace('₹', '').replace('$', '').strip()
                    amount = float(amount_str)
                except:
                    continue  # Skip rows with invalid amounts
                
                # Get other fields
                description = row.get(description_field, "")[:255]  # Limit to 255 chars
                balance = 0.0
                if balance_field and row.get(balance_field):
                    try:
                        balance_str = row[balance_field].replace(',', '').replace('₹', '').replace('$', '').strip()
                        balance = float(balance_str)
                    except:
                        pass
                
                reference = row.get(reference_field, "")[:50] if reference_field else ""
                
                entries.append({
                    'date': parsed_date.strftime("%Y-%m-%d"),
                    'description': description,
                    'amount': amount,
                    'balance': balance,
                    'reference_number': reference
                })
        
        if not entries:
            QMessageBox.warning(self, "Import Error", "No valid entries found in the CSV file.")
            return
        
        # Import entries
        imported_count = self.bank_manager.import_statement(entries, self.current_user)
        
        if imported_count > 0:
            QMessageBox.information(self, "Import Successful", 
                                  f"Successfully imported {imported_count} bank statement entries.")
            # Refresh the bank table
            self.load_bank_entries()
        else:
            QMessageBox.warning(self, "Import Failed", "Failed to import bank statement entries.")
    
    def import_pdf_statement(self, file_path):
        """Import bank statement from PDF file"""
        try:
            # Check if pymupdf is available
            try:
                import fitz  # PyMuPDF
            except ImportError:
                QMessageBox.warning(self, "Import Error", 
                                  "PDF import requires PyMuPDF (fitz) library. Please install it using: pip install PyMuPDF")
                return
            
            # Check if file exists
            import os
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "Import Error", 
                                  f"PDF file not found: {file_path}")
                return
            
            # Extract text from PDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            # Check if text was extracted
            if len(text.strip()) == 0:
                QMessageBox.warning(self, "Import Error", 
                                  "No text content found in the PDF. This might be an image-only PDF which requires OCR.")
                return
            
            # Parse the text to extract transactions
            # This is a simplified parser - in practice, you might need more sophisticated parsing
            # based on the specific format of your bank statements
            entries = self.parse_pdf_text(text)
            
            if not entries:
                QMessageBox.warning(self, "Import Error", 
                                  "Could not extract transactions from the PDF. The format might not be supported.")
                return
            
            # Import entries
            imported_count = self.bank_manager.import_statement(entries, self.current_user)
            
            if imported_count > 0:
                QMessageBox.information(self, "Import Successful", 
                                      f"Successfully imported {imported_count} bank statement entries from PDF.")
                # Refresh the bank table
                self.load_bank_entries()
            else:
                QMessageBox.information(self, "Import Completed", 
                                      "PDF processing completed. No new entries were imported (they may already exist).")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error processing PDF file: {str(e)}\nFile: {file_path}")
    
    def parse_pdf_text(self, text):
        """Parse text extracted from PDF to extract bank transactions"""
        entries = []
        
        # This is a basic parser - you'll need to customize this based on your bank's PDF format
        # Common patterns for bank statements:
        lines = text.split('\n')
        
        # Look for transaction lines (this is a simplified example)
        # You might need to adjust the pattern based on your bank's format
        for line in lines:
            # Example pattern: DD/MM/YYYY Description Amount
            # This is just a template - you'll need to customize it
            
            # Try to match common transaction patterns
            # Pattern 1: DD/MM/YYYY Description Amount
            pattern1 = r'(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(-?\d+(?:,\d{3})*(?:\.\d{2})?)'
            match1 = re.search(pattern1, line)
            
            # Pattern 2: DD-MM-YYYY Description Amount
            pattern2 = r'(\d{2}-\d{2}-\d{4})\s+(.+?)\s+(-?\d+(?:,\d{3})*(?:\.\d{2})?)'
            match2 = re.search(pattern2, line)
            
            if match1:
                date_str, description, amount_str = match1.groups()
                try:
                    # Parse date
                    date = datetime.strptime(date_str, "%d/%m/%Y").date()
                    
                    # Parse amount
                    amount_str = amount_str.replace(',', '')
                    amount = float(amount_str)
                    
                    # Clean description
                    description = description.strip()[:255]
                    
                    entries.append({
                        'date': date.strftime("%Y-%m-%d"),
                        'description': description,
                        'amount': amount,
                        'balance': 0.0,  # Balance might be in a separate column
                        'reference_number': ''
                    })
                except:
                    continue  # Skip invalid entries
            
            elif match2:
                date_str, description, amount_str = match2.groups()
                try:
                    # Parse date
                    date = datetime.strptime(date_str, "%d-%m-%Y").date()
                    
                    # Parse amount
                    amount_str = amount_str.replace(',', '')
                    amount = float(amount_str)
                    
                    # Clean description
                    description = description.strip()[:255]
                    
                    entries.append({
                        'date': date.strftime("%Y-%m-%d"),
                        'description': description,
                        'amount': amount,
                        'balance': 0.0,  # Balance might be in a separate column
                        'reference_number': ''
                    })
                except:
                    continue  # Skip invalid entries
        
        return entries
    
    def find_matches(self):
        """Find potential matches between ledger transactions and bank entries"""
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setValue(0)
        
        # Load data
        self.load_ledger_transactions(start_date, end_date)
        self.load_bank_entries(start_date, end_date)
        
        # Find matches
        matches = self.reconciliation_manager.find_matches(start_date, end_date)
        
        # Highlight matches in tables
        self.highlight_matches(matches)
        
        # Update summary
        summary = self.reconciliation_manager.get_reconciliation_summary(start_date, end_date)
        ledger_unmatched = summary['ledger'].get('Unreconciled', 0)
        bank_unmatched = summary['bank'].get('Unreconciled', 0)
        
        self.summary_label.setText(
            f"Found {len(matches)} potential matches. "
            f"Unmatched ledger entries: {ledger_unmatched}, "
            f"Unmatched bank entries: {bank_unmatched}"
        )
        
        self.progress_bar.setVisible(False)
    
    def load_ledger_transactions(self, start_date=None, end_date=None):
        """Load ledger transactions into the table"""
        if start_date and end_date:
            transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.ledger_manager.get_all_transactions()
        
        self.ledger_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            # Add checkbox for selection
            checkbox = QCheckBox()
            checkbox.setProperty('transaction_id', transaction.id)
            
            self.ledger_table.setItem(row, 0, QTableWidgetItem(str(transaction.id)))
            self.ledger_table.setItem(row, 1, QTableWidgetItem(transaction.transaction_id))
            self.ledger_table.setItem(row, 2, QTableWidgetItem(transaction.date))
            self.ledger_table.setItem(row, 3, QTableWidgetItem(transaction.flat_no or ""))
            self.ledger_table.setItem(row, 4, QTableWidgetItem(transaction.transaction_type))
            self.ledger_table.setItem(row, 5, QTableWidgetItem(transaction.category))
            self.ledger_table.setItem(row, 6, QTableWidgetItem(transaction.description))
            self.ledger_table.setItem(row, 7, QTableWidgetItem(str(transaction.debit)))
            self.ledger_table.setItem(row, 8, QTableWidgetItem(str(transaction.credit)))
            self.ledger_table.setItem(row, 9, QTableWidgetItem(str(transaction.balance)))
            self.ledger_table.setItem(row, 10, QTableWidgetItem(transaction.payment_mode))
            self.ledger_table.setItem(row, 11, QTableWidgetItem(transaction.reconciliation_status))
            
            # Add checkbox to last column
            self.ledger_table.setCellWidget(row, 12, checkbox)
            
            # Color coding based on status
            status_color = Qt.green if transaction.reconciliation_status == "Reconciled" else Qt.red
            for col in range(12):  # All columns except the checkbox
                if self.ledger_table.item(row, col):
                    self.ledger_table.item(row, col).setBackground(status_color)
    
    def load_bank_entries(self, start_date=None, end_date=None):
        """Load bank statement entries into the table"""
        if start_date and end_date:
            entries = self.bank_manager.get_entries_by_date_range(start_date, end_date)
        else:
            entries = self.bank_manager.get_all_entries()
        
        self.bank_table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Add checkbox for selection
            checkbox = QCheckBox()
            checkbox.setProperty('entry_id', entry.id)
            
            self.bank_table.setItem(row, 0, QTableWidgetItem(str(entry.id)))
            self.bank_table.setItem(row, 1, QTableWidgetItem(entry.date))
            self.bank_table.setItem(row, 2, QTableWidgetItem(entry.description))
            self.bank_table.setItem(row, 3, QTableWidgetItem(str(entry.amount)))
            self.bank_table.setItem(row, 4, QTableWidgetItem(str(entry.balance)))
            self.bank_table.setItem(row, 5, QTableWidgetItem(entry.reference_number or ""))
            self.bank_table.setItem(row, 6, QTableWidgetItem(entry.import_date or ""))
            self.bank_table.setItem(row, 7, QTableWidgetItem(entry.reconciliation_status))
            
            # Add checkbox to last column
            self.bank_table.setCellWidget(row, 8, checkbox)
            
            # Color coding based on status
            status_color = Qt.green if entry.reconciliation_status == "Reconciled" else Qt.red
            for col in range(8):  # All columns except the checkbox
                if self.bank_table.item(row, col):
                    self.bank_table.item(row, col).setBackground(status_color)
    
    def highlight_matches(self, matches):
        """Highlight potential matches in both tables"""
        # Clear previous highlighting
        for row in range(self.ledger_table.rowCount()):
            for col in range(12):  # All columns except the checkbox
                if self.ledger_table.item(row, col):
                    status = self.ledger_table.item(row, 11).text()  # Status column
                    color = Qt.green if status == "Reconciled" else Qt.red
                    self.ledger_table.item(row, col).setBackground(color)
        
        for row in range(self.bank_table.rowCount()):
            for col in range(8):  # All columns except the checkbox
                if self.bank_table.item(row, col):
                    status = self.bank_table.item(row, 7).text()  # Status column
                    color = Qt.green if status == "Reconciled" else Qt.red
                    self.bank_table.item(row, col).setBackground(color)
        
        # Highlight potential matches in yellow
        for match in matches:
            ledger_txn = match['ledger_transaction']
            bank_entry = match['bank_entry']
            confidence = match['confidence']
            
            # Find rows in tables
            ledger_row = self.find_ledger_row(ledger_txn.id)
            bank_row = self.find_bank_row(bank_entry.id)
            
            if ledger_row is not None and bank_row is not None:
                # Adjust color based on confidence (higher confidence = more yellow)
                yellow_value = int(200 + (confidence * 55))  # 200-255 range
                highlight_color = Qt.yellow if confidence > 0.8 else Qt.yellow.lighter(130)
                
                # Highlight ledger row
                for col in range(12):
                    if self.ledger_table.item(ledger_row, col):
                        self.ledger_table.item(ledger_row, col).setBackground(highlight_color)
                
                # Highlight bank row
                for col in range(8):
                    if self.bank_table.item(bank_row, col):
                        self.bank_table.item(bank_row, col).setBackground(highlight_color)
    
    def find_ledger_row(self, transaction_id):
        """Find the row index for a ledger transaction"""
        for row in range(self.ledger_table.rowCount()):
            item = self.ledger_table.item(row, 0)  # ID column
            if item and int(item.text()) == transaction_id:
                return row
        return None
    
    def find_bank_row(self, entry_id):
        """Find the row index for a bank entry"""
        for row in range(self.bank_table.rowCount()):
            item = self.bank_table.item(row, 0)  # ID column
            if item and int(item.text()) == entry_id:
                return row
        return None
    
    def reconcile_selected(self):
        """Mark selected ledger transactions and bank entries as matched"""
        selected_ledger_rows = []
        selected_bank_rows = []
        
        # Find selected ledger transactions
        for row in range(self.ledger_table.rowCount()):
            checkbox = self.ledger_table.cellWidget(row, 12)  # Checkbox column
            if checkbox and checkbox.isChecked():
                selected_ledger_rows.append(row)
        
        # Find selected bank entries
        for row in range(self.bank_table.rowCount()):
            checkbox = self.bank_table.cellWidget(row, 8)  # Checkbox column
            if checkbox and checkbox.isChecked():
                selected_bank_rows.append(row)
        
        if not selected_ledger_rows or not selected_bank_rows:
            QMessageBox.warning(self, "Reconciliation Error", 
                              "Please select at least one ledger transaction and one bank entry.")
            return
        
        if len(selected_ledger_rows) != len(selected_bank_rows):
            QMessageBox.warning(self, "Reconciliation Error", 
                              "Please select the same number of ledger transactions and bank entries.")
            return
        
        # Confirm reconciliation
        reply = QMessageBox.question(
            self, "Confirm Reconciliation",
            f"Are you sure you want to mark {len(selected_ledger_rows)} pairs as matched?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            matched_pairs = []
            for i in range(len(selected_ledger_rows)):
                ledger_row = selected_ledger_rows[i]
                bank_row = selected_bank_rows[i]
                
                # Get transaction IDs
                ledger_id = int(self.ledger_table.item(ledger_row, 0).text())
                bank_id = int(self.bank_table.item(bank_row, 0).text())
                
                # Store the matched pairs for later highlighting
                matched_pairs.append((ledger_id, bank_id))
                
                # Mark as matched
                if self.reconciliation_manager.mark_as_matched(ledger_id, bank_id, self.current_user):
                    success_count += 1
            
            QMessageBox.information(self, "Reconciliation Complete", 
                                  f"Successfully reconciled {success_count} pairs.")
            
            # Refresh tables while preserving the current date range
            start_date = self.start_date_input.date().toString("yyyy-MM-dd")
            end_date = self.end_date_input.date().toString("yyyy-MM-dd")
            self.load_ledger_transactions(start_date, end_date)
            self.load_bank_entries(start_date, end_date)
            
            # Update summary without re-running matching
            summary = self.reconciliation_manager.get_reconciliation_summary(start_date, end_date)
            ledger_unmatched = summary['ledger'].get('Unreconciled', 0)
            bank_unmatched = summary['bank'].get('Unreconciled', 0)
            
            # Count the matched items in current view
            matched_ledger_count = sum(1 for i in range(self.ledger_table.rowCount()) 
                                     if self.ledger_table.item(i, 11).text() == "Reconciled")
            matched_bank_count = sum(1 for i in range(self.bank_table.rowCount()) 
                                   if self.bank_table.item(i, 7).text() == "Reconciled")
            
            total_matches = matched_ledger_count + matched_bank_count
            
            self.summary_label.setText(
                f"Current view: {total_matches} matched items, "
                f"Unmatched ledger entries: {ledger_unmatched}, "
                f"Unmatched bank entries: {bank_unmatched}"
            )