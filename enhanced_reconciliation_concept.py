"""
Enhanced Reconciliation Tab Design Concept

This is a conceptual design for an improved reconciliation interface.
Key improvements:
1. Better visual organization
2. Enhanced filtering capabilities
3. Improved matching workflow
4. Better summary information
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QLabel, QPushButton, QComboBox, 
                             QDateEdit, QSpinBox, QDoubleSpinBox, QLineEdit,
                             QCheckBox, QTableWidget, QHeaderView, QSplitter,
                             QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon

class EnhancedReconciliationTab(QWidget):
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.setup_enhanced_ui()
        
    def setup_enhanced_ui(self):
        main_layout = QVBoxLayout()
        
        # Enhanced control panel with better organization
        control_group = QGroupBox("Reconciliation Controls")
        control_layout = QGridLayout()
        
        # Date range with presets
        control_layout.addWidget(QLabel("Date Range:"), 0, 0)
        
        date_preset_layout = QHBoxLayout()
        self.date_preset_combo = QComboBox()
        self.date_preset_combo.addItems([
            "Last 30 Days", "Last 3 Months", "Last 6 Months", 
            "Current Year", "Previous Year", "Custom Range"
        ])
        date_preset_layout.addWidget(self.date_preset_combo)
        
        self.start_date_input = QDateEdit()
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.end_date_input = QDateEdit()
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        
        date_preset_layout.addWidget(QLabel("From:"))
        date_preset_layout.addWidget(self.start_date_input)
        date_preset_layout.addWidget(QLabel("To:"))
        date_preset_layout.addWidget(self.end_date_input)
        
        control_layout.addLayout(date_preset_layout, 0, 1, 1, 3)
        
        # Matching controls
        control_layout.addWidget(QLabel("Matching Tolerance:"), 1, 0)
        
        tolerance_layout = QHBoxLayout()
        self.date_tolerance_spin = QSpinBox()
        self.date_tolerance_spin.setRange(0, 30)
        self.date_tolerance_spin.setValue(3)
        self.date_tolerance_spin.setSuffix(" days")
        tolerance_layout.addWidget(QLabel("Date:"))
        tolerance_layout.addWidget(self.date_tolerance_spin)
        
        self.amount_tolerance_spin = QDoubleSpinBox()
        self.amount_tolerance_spin.setRange(0, 1000)
        self.amount_tolerance_spin.setValue(0.01)
        self.amount_tolerance_spin.setPrefix("₹")
        tolerance_layout.addWidget(QLabel("Amount:"))
        tolerance_layout.addWidget(self.amount_tolerance_spin)
        
        control_layout.addLayout(tolerance_layout, 1, 1, 1, 3)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import Bank Statement")
        self.import_button.setIcon(QIcon("import_icon.png"))  # Placeholder
        self.find_matches_button = QPushButton("Find Matches")
        self.find_matches_button.setIcon(QIcon("search_icon.png"))  # Placeholder
        self.auto_match_button = QPushButton("Auto-Match")
        self.auto_match_button.setIcon(QIcon("magic_icon.png"))  # Placeholder
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(QIcon("refresh_icon.png"))  # Placeholder
        
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.find_matches_button)
        button_layout.addWidget(self.auto_match_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        control_layout.addLayout(button_layout, 2, 0, 1, 4)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Summary dashboard
        summary_group = QGroupBox("Reconciliation Summary")
        summary_layout = QHBoxLayout()
        
        self.matched_ledger_label = QLabel("Matched Ledger: 0")
        self.unmatched_ledger_label = QLabel("Unmatched Ledger: 0")
        self.matched_bank_label = QLabel("Matched Bank: 0")
        self.unmatched_bank_label = QLabel("Unmatched Bank: 0")
        self.confidence_label = QLabel("Avg Confidence: 0%")
        
        # Style the labels
        self.matched_ledger_label.setStyleSheet("color: green; font-weight: bold;")
        self.unmatched_ledger_label.setStyleSheet("color: red; font-weight: bold;")
        self.matched_bank_label.setStyleSheet("color: green; font-weight: bold;")
        self.unmatched_bank_label.setStyleSheet("color: red; font-weight: bold;")
        
        summary_layout.addWidget(self.matched_ledger_label)
        summary_layout.addWidget(self.unmatched_ledger_label)
        summary_layout.addWidget(self.matched_bank_label)
        summary_layout.addWidget(self.unmatched_bank_label)
        summary_layout.addWidget(self.confidence_label)
        summary_layout.addStretch()
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Splitter with enhanced tables
        splitter = QSplitter(Qt.Horizontal)
        
        # Enhanced ledger table
        ledger_group = QGroupBox("Ledger Transactions")
        ledger_layout = QVBoxLayout()
        
        # Search and filter for ledger
        ledger_filter_layout = QHBoxLayout()
        self.ledger_search = QLineEdit()
        self.ledger_search.setPlaceholderText("Search ledger transactions...")
        self.ledger_show_unmatched = QCheckBox("Show only unmatched")
        self.ledger_filter_button = QPushButton("Filter")
        
        ledger_filter_layout.addWidget(QLabel("Search:"))
        ledger_filter_layout.addWidget(self.ledger_search)
        ledger_filter_layout.addWidget(self.ledger_show_unmatched)
        ledger_filter_layout.addWidget(self.ledger_filter_button)
        
        self.ledger_table = QTableWidget()
        self.ledger_table.setColumnCount(14)
        headers = ["✓", "S.N", "Transaction ID", "Date", "Flat No", "Type", "Category", 
                  "Description", "Debit", "Credit", "Balance", "Payment Mode", 
                  "Entered By", "Status"]
        self.ledger_table.setHorizontalHeaderLabels(headers)
        self.ledger_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        ledger_layout.addLayout(ledger_filter_layout)
        ledger_layout.addWidget(self.ledger_table)
        
        ledger_group.setLayout(ledger_layout)
        splitter.addWidget(ledger_group)
        
        # Enhanced bank table
        bank_group = QGroupBox("Bank Statement Entries")
        bank_layout = QVBoxLayout()
        
        # Search and filter for bank
        bank_filter_layout = QHBoxLayout()
        self.bank_search = QLineEdit()
        self.bank_search.setPlaceholderText("Search bank entries...")
        self.bank_show_unmatched = QCheckBox("Show only unmatched")
        self.bank_filter_button = QPushButton("Filter")
        
        bank_filter_layout.addWidget(QLabel("Search:"))
        bank_filter_layout.addWidget(self.bank_search)
        bank_filter_layout.addWidget(self.bank_show_unmatched)
        bank_filter_layout.addWidget(self.bank_filter_button)
        
        self.bank_table = QTableWidget()
        self.bank_table.setColumnCount(10)
        headers = ["✓", "S.N", "Reference No", "Date", "Description", "Amount", 
                  "Balance", "Import Date", "Status", "Match Confidence"]
        self.bank_table.setHorizontalHeaderLabels(headers)
        self.bank_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        bank_layout.addLayout(bank_filter_layout)
        bank_layout.addWidget(self.bank_table)
        
        bank_group.setLayout(bank_layout)
        splitter.addWidget(bank_group)
        
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter)
        
        # Enhanced action buttons
        action_layout = QHBoxLayout()
        self.suggest_matches_button = QPushButton("Suggest Matches")
        self.suggest_matches_button.setIcon(QIcon("lightbulb_icon.png"))  # Placeholder
        self.match_selected_button = QPushButton("Match Selected")
        self.match_selected_button.setIcon(QIcon("link_icon.png"))  # Placeholder
        self.unmatch_selected_button = QPushButton("Unmatch Selected")
        self.unmatch_selected_button.setIcon(QIcon("unlink_icon.png"))  # Placeholder
        self.export_matches_button = QPushButton("Export Matches")
        self.export_matches_button.setIcon(QIcon("export_icon.png"))  # Placeholder
        
        action_layout.addWidget(self.suggest_matches_button)
        action_layout.addWidget(self.match_selected_button)
        action_layout.addWidget(self.unmatch_selected_button)
        action_layout.addWidget(self.export_matches_button)
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals
        self.setup_connections()
        
    def setup_connections(self):
        """Setup signal connections for enhanced functionality"""
        self.date_preset_combo.currentTextChanged.connect(self.on_date_preset_changed)
        self.find_matches_button.clicked.connect(self.enhanced_find_matches)
        self.auto_match_button.clicked.connect(self.auto_match_transactions)
        self.suggest_matches_button.clicked.connect(self.suggest_matches)
        self.match_selected_button.clicked.connect(self.match_selected)
        self.unmatch_selected_button.clicked.connect(self.unmatch_selected)
        self.ledger_filter_button.clicked.connect(self.filter_ledger_transactions)
        self.bank_filter_button.clicked.connect(self.filter_bank_entries)
        self.ledger_search.textChanged.connect(self.on_ledger_search_changed)
        self.bank_search.textChanged.connect(self.on_bank_search_changed)
        
    def on_date_preset_changed(self, preset):
        """Handle date preset changes"""
        current_date = QDate.currentDate()
        if preset == "Last 30 Days":
            self.start_date_input.setDate(current_date.addDays(-30))
            self.end_date_input.setDate(current_date)
        elif preset == "Last 3 Months":
            self.start_date_input.setDate(current_date.addMonths(-3))
            self.end_date_input.setDate(current_date)
        elif preset == "Last 6 Months":
            self.start_date_input.setDate(current_date.addMonths(-6))
            self.end_date_input.setDate(current_date)
        elif preset == "Current Year":
            self.start_date_input.setDate(QDate(current_date.year(), 1, 1))
            self.end_date_input.setDate(current_date)
        elif preset == "Previous Year":
            self.start_date_input.setDate(QDate(current_date.year() - 1, 1, 1))
            self.end_date_input.setDate(QDate(current_date.year() - 1, 12, 31))
            
    def enhanced_find_matches(self):
        """Enhanced find matches with progress feedback"""
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Get tolerance values
        date_tolerance = self.date_tolerance_spin.value()
        amount_tolerance = self.amount_tolerance_spin.value()
        
        # Find matches with enhanced parameters
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        
        # Load data with current filters
        self.load_ledger_transactions(start_date, end_date)
        self.load_bank_entries(start_date, end_date)
        
        # Find matches
        matches = self.reconciliation_manager.find_matches(
            start_date, end_date, 
            tolerance_days=date_tolerance,
            tolerance_amount=amount_tolerance
        )
        
        # Highlight matches
        self.highlight_matches(matches)
        
        # Update summary
        self.update_summary(start_date, end_date)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Show notification
        QMessageBox.information(
            self, 
            "Matching Complete", 
            f"Found {len(matches)} potential matches.\nReview and select matches to reconcile."
        )
        
    def auto_match_transactions(self):
        """Auto-match transactions with high confidence"""
        reply = QMessageBox.question(
            self,
            "Auto-Match Confirmation",
            "This will automatically match transactions with high confidence (80%+).\nDo you want to continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Implement auto-matching logic
            self.perform_auto_matching()
            
    def suggest_matches(self):
        """Suggest top potential matches"""
        # Get selected items or show suggestions for all unmatched
        # This would show a dialog with top 5-10 suggestions
        pass
        
    def match_selected(self):
        """Match selected ledger and bank entries"""
        # Enhanced matching with confirmation
        pass
        
    def unmatch_selected(self):
        """Unmatch selected entries"""
        # Allow reverting matches
        pass
        
    def filter_ledger_transactions(self):
        """Filter ledger transactions based on search criteria"""
        pass
        
    def filter_bank_entries(self):
        """Filter bank entries based on search criteria"""
        pass
        
    def on_ledger_search_changed(self, text):
        """Handle ledger search text changes"""
        pass
        
    def on_bank_search_changed(self, text):
        """Handle bank search text changes"""
        pass
        
    def update_summary(self, start_date, end_date):
        """Update the reconciliation summary"""
        summary = self.reconciliation_manager.get_reconciliation_summary(start_date, end_date)
        
        ledger_matched = summary['ledger'].get('Reconciled', 0)
        ledger_unmatched = summary['ledger'].get('Unreconciled', 0)
        bank_matched = summary['bank'].get('Reconciled', 0)
        bank_unmatched = summary['bank'].get('Unreconciled', 0)
        
        self.matched_ledger_label.setText(f"Matched Ledger: {ledger_matched}")
        self.unmatched_ledger_label.setText(f"Unmatched Ledger: {ledger_unmatched}")
        self.matched_bank_label.setText(f"Matched Bank: {bank_matched}")
        self.unmatched_bank_label.setText(f"Unmatched Bank: {bank_unmatched}")
        
        # Calculate average confidence if matches exist
        # This would require storing confidence scores