# Bank format configuration dialog for reconciliation tab
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QCheckBox, QDialogButtonBox, QGroupBox, QTextEdit,
                             QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt

class BankFormatConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bank Format Configuration")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()
        self.load_default_formats()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Bank format selection
        format_selection_layout = QHBoxLayout()
        format_selection_layout.addWidget(QLabel("Bank Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.currentIndexChanged.connect(self.on_format_selected)
        format_selection_layout.addWidget(self.format_combo)
        
        self.new_format_button = QPushButton("New Format")
        self.new_format_button.clicked.connect(self.new_format)
        format_selection_layout.addWidget(self.new_format_button)
        
        self.delete_format_button = QPushButton("Delete Format")
        self.delete_format_button.clicked.connect(self.delete_format)
        format_selection_layout.addWidget(self.delete_format_button)
        
        format_selection_layout.addStretch()
        layout.addLayout(format_selection_layout)
        
        # Format configuration group
        config_group = QGroupBox("Format Configuration")
        config_layout = QFormLayout()
        
        # Format name
        self.format_name_edit = QLineEdit()
        config_layout.addRow("Format Name:", self.format_name_edit)
        
        # Date format
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "DD/MM/YYYY", "DD-MM-YYYY", "DD.MM.YYYY",
            "MM/DD/YYYY", "MM-DD-YYYY", "MM.DD.YYYY",
            "YYYY/MM/DD", "YYYY-MM-DD", "YYYY.MM.DD"
        ])
        config_layout.addRow("Date Format:", self.date_format_combo)
        
        # Field order
        self.field_order_edit = QLineEdit()
        self.field_order_edit.setPlaceholderText("e.g., date,description,amount,balance")
        config_layout.addRow("Field Order:", self.field_order_edit)
        
        # Amount format
        amount_format_layout = QHBoxLayout()
        self.amount_decimal_separator = QComboBox()
        self.amount_decimal_separator.addItems([".", ","])
        amount_format_layout.addWidget(QLabel("Decimal Separator:"))
        amount_format_layout.addWidget(self.amount_decimal_separator)
        
        amount_format_layout.addSpacing(10)
        
        self.amount_thousands_separator = QComboBox()
        self.amount_thousands_separator.addItems(["None", ",", ".", " "])
        amount_format_layout.addWidget(QLabel("Thousands Separator:"))
        amount_format_layout.addWidget(self.amount_thousands_separator)
        
        amount_format_layout.addStretch()
        config_layout.addRow("Amount Format:", amount_format_layout)
        
        # Currency symbol
        self.currency_symbol_edit = QLineEdit()
        self.currency_symbol_edit.setPlaceholderText("e.g., ₹, $, €")
        config_layout.addRow("Currency Symbol:", self.currency_symbol_edit)
        
        # Reference number pattern
        self.ref_pattern_edit = QLineEdit()
        self.ref_pattern_edit.setPlaceholderText("Regex pattern for reference numbers")
        config_layout.addRow("Reference Pattern:", self.ref_pattern_edit)
        
        # Description pattern
        self.desc_pattern_edit = QLineEdit()
        self.desc_pattern_edit.setPlaceholderText("Regex pattern for descriptions")
        config_layout.addRow("Description Pattern:", self.desc_pattern_edit)
        
        # Negative amount format
        self.negative_amount_combo = QComboBox()
        self.negative_amount_combo.addItems(["Minus sign (-)", "Parentheses ()"])
        config_layout.addRow("Negative Amount Format:", self.negative_amount_combo)
        
        # Multi-line description
        self.multiline_desc_checkbox = QCheckBox("Support multi-line descriptions")
        config_layout.addRow("", self.multiline_desc_checkbox)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Sample text area
        sample_group = QGroupBox("Sample Text")
        sample_layout = QVBoxLayout()
        self.sample_text_edit = QTextEdit()
        self.sample_text_edit.setPlaceholderText("Paste a sample line from your bank statement here...")
        self.sample_text_edit.setMaximumHeight(80)
        sample_layout.addWidget(self.sample_text_edit)
        
        sample_buttons_layout = QHBoxLayout()
        self.test_parsing_button = QPushButton("Test Parsing")
        self.test_parsing_button.clicked.connect(self.test_parsing)
        sample_buttons_layout.addWidget(self.test_parsing_button)
        sample_buttons_layout.addStretch()
        sample_layout.addLayout(sample_buttons_layout)
        
        sample_group.setLayout(sample_layout)
        layout.addWidget(sample_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def load_default_formats(self):
        """Load default bank formats"""
        # Clear existing items
        self.format_combo.clear()
        
        # Add default formats
        default_formats = [
            "Standard Indian Bank",
            "US Bank Format", 
            "European Bank Format",
            "Custom Format"
        ]
        
        for format_name in default_formats:
            self.format_combo.addItem(format_name)
            
        # Select first format
        if default_formats:
            self.format_combo.setCurrentIndex(0)
            self.load_format_config(default_formats[0])
            
    def on_format_selected(self, index):
        """Handle format selection change"""
        format_name = self.format_combo.itemText(index)
        self.load_format_config(format_name)
        
    def load_format_config(self, format_name):
        """Load configuration for a specific format"""
        # Reset fields
        self.format_name_edit.setText(format_name)
        
        # Set default values based on format name
        if format_name == "Standard Indian Bank":
            self.date_format_combo.setCurrentText("DD/MM/YYYY")
            self.field_order_edit.setText("date,description,amount,balance")
            self.amount_decimal_separator.setCurrentText(".")
            self.amount_thousands_separator.setCurrentText(",")
            self.currency_symbol_edit.setText("₹")
            self.ref_pattern_edit.setText("")
            self.desc_pattern_edit.setText("")
            self.negative_amount_combo.setCurrentText("Minus sign (-)")
            self.multiline_desc_checkbox.setChecked(False)
        elif format_name == "US Bank Format":
            self.date_format_combo.setCurrentText("MM/DD/YYYY")
            self.field_order_edit.setText("date,description,amount,balance")
            self.amount_decimal_separator.setCurrentText(".")
            self.amount_thousands_separator.setCurrentText(",")
            self.currency_symbol_edit.setText("$")
            self.ref_pattern_edit.setText("")
            self.desc_pattern_edit.setText("")
            self.negative_amount_combo.setCurrentText("Minus sign (-)")
            self.multiline_desc_checkbox.setChecked(False)
        elif format_name == "European Bank Format":
            self.date_format_combo.setCurrentText("DD.MM.YYYY")
            self.field_order_edit.setText("date,description,amount,balance")
            self.amount_decimal_separator.setCurrentText(",")
            self.amount_thousands_separator.setCurrentText(".")
            self.currency_symbol_edit.setText("€")
            self.ref_pattern_edit.setText("")
            self.desc_pattern_edit.setText("")
            self.negative_amount_combo.setCurrentText("Minus sign (-)")
            self.multiline_desc_checkbox.setChecked(False)
        else:  # Custom Format
            self.date_format_combo.setCurrentText("DD/MM/YYYY")
            self.field_order_edit.setText("date,description,amount,balance")
            self.amount_decimal_separator.setCurrentText(".")
            self.amount_thousands_separator.setCurrentText(",")
            self.currency_symbol_edit.setText("")
            self.ref_pattern_edit.setText("")
            self.desc_pattern_edit.setText("")
            self.negative_amount_combo.setCurrentText("Minus sign (-)")
            self.multiline_desc_checkbox.setChecked(False)
            
    def new_format(self):
        """Create a new bank format"""
        format_name, ok = QInputDialog.getText(self, "New Format", "Enter format name:")
        if ok and format_name:
            if self.format_combo.findText(format_name) == -1:
                self.format_combo.addItem(format_name)
                self.format_combo.setCurrentText(format_name)
                self.format_name_edit.setText(format_name)
            else:
                QMessageBox.warning(self, "Duplicate Name", "A format with this name already exists.")
                
    def delete_format(self):
        """Delete the current bank format"""
        current_format = self.format_combo.currentText()
        if current_format in ["Standard Indian Bank", "US Bank Format", "European Bank Format"]:
            QMessageBox.warning(self, "Cannot Delete", "Default formats cannot be deleted.")
            return
            
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete the format '{current_format}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            index = self.format_combo.currentIndex()
            self.format_combo.removeItem(index)
            if self.format_combo.count() > 0:
                self.format_combo.setCurrentIndex(0)
                
    def test_parsing(self):
        """Test parsing with the current configuration"""
        sample_text = self.sample_text_edit.toPlainText().strip()
        if not sample_text:
            QMessageBox.warning(self, "No Sample Text", "Please enter some sample text to test parsing.")
            return
            
        # Get current configuration
        config = self.get_current_config()
        
        # Try to parse the sample text
        try:
            # This is a simplified test - in a real implementation, 
            # you would use the actual parsing logic from reconciliation_tab.py
            result = f"Configuration: {config}\n\nSample text:\n{sample_text}"
            QMessageBox.information(self, "Parsing Test", f"Parsing would be attempted with:\n\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "Parsing Error", f"Error testing parsing: {str(e)}")
            
    def get_current_config(self):
        """Get the current configuration as a dictionary"""
        return {
            'name': self.format_name_edit.text(),
            'date_format': self.date_format_combo.currentText(),
            'field_order': self.field_order_edit.text(),
            'decimal_separator': self.amount_decimal_separator.currentText(),
            'thousands_separator': self.amount_thousands_separator.currentText(),
            'currency_symbol': self.currency_symbol_edit.text(),
            'ref_pattern': self.ref_pattern_edit.text(),
            'desc_pattern': self.desc_pattern_edit.text(),
            'negative_amount_format': self.negative_amount_combo.currentText(),
            'multiline_description': self.multiline_desc_checkbox.isChecked()
        }
        
    def get_all_configs(self):
        """Get all format configurations"""
        configs = []
        for i in range(self.format_combo.count()):
            format_name = self.format_combo.itemText(i)
            # In a real implementation, you would load each format's config from storage
            # For now, we'll return a basic configuration for each format
            config = {
                'name': format_name,
                'date_format': "DD/MM/YYYY",
                'field_order': "date,description,amount,balance",
                'decimal_separator': ".",
                'thousands_separator': ",",
                'currency_symbol': "",
                'ref_pattern': "",
                'desc_pattern': "",
                'negative_amount_format': "Minus sign (-)",
                'multiline_description': False
            }
            
            # Set specific values for default formats
            if format_name == "Standard Indian Bank":
                config['date_format'] = "DD/MM/YYYY"
                config['decimal_separator'] = "."
                config['thousands_separator'] = ","
                config['currency_symbol'] = "₹"
            elif format_name == "US Bank Format":
                config['date_format'] = "MM/DD/YYYY"
                config['decimal_separator'] = "."
                config['thousands_separator'] = ","
                config['currency_symbol'] = "$"
            elif format_name == "European Bank Format":
                config['date_format'] = "DD.MM.YYYY"
                config['decimal_separator'] = ","
                config['thousands_separator'] = "."
                config['currency_symbol'] = "€"
                
            configs.append(config)
        return configs