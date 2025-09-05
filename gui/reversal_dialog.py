# gui/reversal_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QComboBox, QTextEdit, QPushButton,
                            QMessageBox, QDialogButtonBox)
from models.transaction_reversal import TransactionReversalManager, ReversalReason

class ReversalDialog(QDialog):
    def __init__(self, transaction_id, transaction_details, current_user, parent=None):
        super().__init__(parent)
        self.transaction_id = transaction_id
        self.transaction_details = transaction_details
        self.current_user = current_user
        self.reversal_manager = TransactionReversalManager()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Reverse Transaction")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Transaction details
        details_group = QFormLayout()
        details_group.addRow(QLabel("Transaction ID:"), QLabel(self.transaction_id))
        details_group.addRow(QLabel("Date:"), QLabel(self.transaction_details.date))
        details_group.addRow(QLabel("Type:"), QLabel(self.transaction_details.transaction_type))
        details_group.addRow(QLabel("Category:"), QLabel(self.transaction_details.category))
        details_group.addRow(QLabel("Amount:"), QLabel(f"₹{self.transaction_details.debit or self.transaction_details.credit}"))
        details_group.addRow(QLabel("Description:"), QLabel(self.transaction_details.description))
        
        layout.addLayout(details_group)
        
        # Reversal form
        form_layout = QFormLayout()
        
        # Reason for reversal
        self.reason_combo = QComboBox()
        self.reason_combo.addItems(self.reversal_manager.get_valid_reversal_reasons())
        form_layout.addRow("Reason for Reversal*:", self.reason_combo)
        
        # Remarks
        self.remarks_edit = QTextEdit()
        self.remarks_edit.setMaximumHeight(100)
        form_layout.addRow("Remarks:", self.remarks_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def accept(self):
        reason = self.reason_combo.currentText()
        remarks = self.remarks_edit.toPlainText().strip()
        
        if not reason:
            QMessageBox.warning(self, "Validation Error", "Please select a reason for reversal.")
            return
        
        try:
            reversal_id = self.reversal_manager.reverse_transaction(
                self.transaction_id,
                reason,
                remarks,
                self.current_user
            )
            
            if reversal_id:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Transaction reversed successfully!\nReversal Transaction ID: {reversal_id}"
                )
                super().accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to reverse transaction.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")