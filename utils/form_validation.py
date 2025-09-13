# utils/form_validation.py
"""
Form validation utilities for the Society Management System.
This module provides comprehensive validation functions for data entry forms.
"""

from PyQt5.QtWidgets import QMessageBox, QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPalette
from datetime import datetime, timedelta


def highlight_invalid_field(widget):
    """
    Highlight a field as invalid with a red background.
    
    Args:
        widget: The input widget to highlight
    """
    if hasattr(widget, 'setStyleSheet'):
        widget.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")
    elif hasattr(widget, 'setPalette'):
        palette = widget.palette()
        palette.setColor(QPalette.Base, "#ffcccc")
        widget.setPalette(palette)


def clear_field_highlight(widget):
    """
    Clear validation highlighting from a field.
    
    Args:
        widget: The input widget to clear highlighting
    """
    if hasattr(widget, 'setStyleSheet'):
        widget.setStyleSheet("")
    elif hasattr(widget, 'setPalette'):
        widget.setPalette(QPalette())


def validate_required_field(widget, field_name, parent=None):
    """
    Validate that a required field is not empty.
    
    Args:
        widget: The input widget (QLineEdit, QComboBox, QTextEdit, etc.)
        field_name: The name of the field for error messages
        parent: Parent widget for message boxes
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Clear any previous highlighting
    clear_field_highlight(widget)
    
    if isinstance(widget, QLineEdit):
        if not widget.text().strip():
            QMessageBox.warning(parent, "Validation Error", f"{field_name} is required.")
            highlight_invalid_field(widget)
            widget.setFocus()
            return False
    elif isinstance(widget, QComboBox):
        if not widget.currentText().strip():
            QMessageBox.warning(parent, "Validation Error", f"{field_name} is required.")
            highlight_invalid_field(widget)
            widget.setFocus()
            return False
    elif isinstance(widget, QTextEdit):
        if not widget.toPlainText().strip():
            QMessageBox.warning(parent, "Validation Error", f"{field_name} is required.")
            highlight_invalid_field(widget)
            widget.setFocus()
            return False
    elif hasattr(widget, 'value'):  # For QDoubleSpinBox and similar
        if widget.value() <= 0:
            QMessageBox.warning(parent, "Validation Error", f"{field_name} must be greater than zero.")
            highlight_invalid_field(widget)
            widget.setFocus()
            return False
            
    return True


def validate_date_field(date_widget, field_name, parent=None):
    """
    Validate that a date field contains a reasonable date.
    
    Args:
        date_widget: The QDateEdit widget
        field_name: The name of the field for error messages
        parent: Parent widget for message boxes
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Clear any previous highlighting
    clear_field_highlight(date_widget)
    
    current_date = QDate.currentDate()
    selected_date = date_widget.date()
    
    # Check if date is in the future
    if selected_date > current_date:
        reply = QMessageBox.question(
            parent, 
            "Date Validation", 
            f"{field_name} is in the future. Are you sure you want to proceed?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            highlight_invalid_field(date_widget)
            date_widget.setFocus()
            return False
    
    # Check if date is too far in the past (more than 10 years)
    ten_years_ago = current_date.addYears(-10)
    if selected_date < ten_years_ago:
        reply = QMessageBox.question(
            parent,
            "Date Validation",
            f"{field_name} is more than 10 years ago. Are you sure you want to proceed?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            highlight_invalid_field(date_widget)
            date_widget.setFocus()
            return False
            
    return True


def validate_amount_field(amount_widget, field_name, parent=None):
    """
    Validate that an amount field contains a valid amount.
    
    Args:
        amount_widget: The QDoubleSpinBox widget
        field_name: The name of the field for error messages
        parent: Parent widget for message boxes
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Clear any previous highlighting
    clear_field_highlight(amount_widget)
    
    if amount_widget.value() <= 0:
        QMessageBox.warning(parent, "Validation Error", f"{field_name} must be greater than zero.")
        highlight_invalid_field(amount_widget)
        amount_widget.setFocus()
        return False
        
    # Check for reasonable amount (less than 1 crore)
    if amount_widget.value() > 10000000:
        reply = QMessageBox.question(
            parent,
            "Amount Validation",
            f"{field_name} is very large (>{amount_widget.locale().toString(10000000)}). Are you sure you want to proceed?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            highlight_invalid_field(amount_widget)
            amount_widget.setFocus()
            return False
            
    return True


def validate_text_length(widget, field_name, max_length, parent=None):
    """
    Validate that a text field doesn't exceed maximum length.
    
    Args:
        widget: The input widget (QLineEdit, QTextEdit)
        field_name: The name of the field for error messages
        max_length: Maximum allowed length
        parent: Parent widget for message boxes
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Clear any previous highlighting
    clear_field_highlight(widget)
    
    if isinstance(widget, QLineEdit):
        text = widget.text()
    elif isinstance(widget, QTextEdit):
        text = widget.toPlainText()
    else:
        return True
        
    if len(text) > max_length:
        QMessageBox.warning(
            parent, 
            "Validation Error", 
            f"{field_name} must not exceed {max_length} characters. Current length: {len(text)}"
        )
        highlight_invalid_field(widget)
        widget.setFocus()
        return False
        
    return True


def validate_flat_no_field(flat_no_widget, field_name, parent=None):
    """
    Validate that a flat number field contains valid content.
    
    Args:
        flat_no_widget: The QComboBox widget
        field_name: The name of the field for error messages
        parent: Parent widget for message boxes
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Clear any previous highlighting
    clear_field_highlight(flat_no_widget)
    
    # If the field is empty, that's OK (optional field)
    if not flat_no_widget.currentText().strip():
        return True
        
    # Validate that flat number doesn't contain invalid characters
    flat_no = flat_no_widget.currentText().strip()
    invalid_chars = ['<', '>', ':', '"', '/', '\\\\', '|', '?', '*']
    
    for char in invalid_chars:
        if char in flat_no:
            QMessageBox.warning(
                parent,
                "Validation Error",
                f"{field_name} contains invalid characters. Please remove: {', '.join(invalid_chars)}"
            )
            highlight_invalid_field(flat_no_widget)
            flat_no_widget.setFocus()
            return False
            
    return True


def validate_form_data(form_data, parent=None):
    """
    Validate all form data at once.
    
    Args:
        form_data: Dictionary containing form field names and their widgets
        parent: Parent widget for message boxes
        
    Returns:
        bool: True if all validations pass, False otherwise
    """
    # Clear all highlights first
    for widget in form_data.values():
        clear_field_highlight(widget)
    
    # Required field validation
    required_fields = [
        ('date', 'Date'),
        ('category', 'Category'),
        ('amount', 'Amount'),
        ('payment_mode', 'Payment Mode')
    ]
    
    for field_key, field_name in required_fields:
        if field_key in form_data:
            widget = form_data[field_key]
            if not validate_required_field(widget, field_name, parent):
                return False
    
    # Date validation
    if 'date' in form_data:
        if not validate_date_field(form_data['date'], 'Date', parent):
            return False
    
    # Amount validation
    if 'amount' in form_data:
        if not validate_amount_field(form_data['amount'], 'Amount', parent):
            return False
    
    # Text length validation
    text_fields = [
        ('description', 'Description', 500),
        ('reference_no', 'Reference No', 50)
    ]
    
    for field_key, field_name, max_length in text_fields:
        if field_key in form_data:
            widget = form_data[field_key]
            if isinstance(widget, (QLineEdit, QTextEdit)):
                if not validate_text_length(widget, field_name, max_length, parent):
                    return False
    
    # Flat number validation
    if 'flat_no' in form_data:
        if not validate_flat_no_field(form_data['flat_no'], 'Flat No', parent):
            return False
            
    return True