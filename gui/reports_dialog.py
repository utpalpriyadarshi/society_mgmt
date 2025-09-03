# gui/reports_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QDateEdit, QMessageBox, 
                            QFileDialog, QGroupBox, QFormLayout)
from PyQt5.QtCore import QDate
import os
import sys
from datetime import date
from models.reports import ReportGenerator

class ReportsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reports")
        self.setGeometry(100, 100, 400, 350)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Report type selection
        report_group = QGroupBox("Generate Reports")
        report_layout = QFormLayout()
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Ledger Report", "Resident List", "Payment Summary", "Expense Summary", "Outstanding Dues Report", "Income vs Expense Report", "Payments Report", "Expenses Report"])
        self.report_type_combo.currentTextChanged.connect(self.on_report_type_changed)
        report_layout.addRow("Report Type:", self.report_type_combo)
        
        # Date range (always visible and enabled)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-12))
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        report_layout.addRow("Start Date:", self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        report_layout.addRow("End Date:", self.end_date)
        
        # Date info label
        self.date_info_label = QLabel("(Date range applies to Ledger, Outstanding Dues, Income vs Expense, Payments, and Expenses reports)")
        self.date_info_label.setWordWrap(True)
        report_layout.addRow("", self.date_info_label)
        
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        # Generate button
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_button)
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Initialize UI state
        self.on_report_type_changed(self.report_type_combo.currentText())
    
    def on_report_type_changed(self, report_type):
        # Date range is always enabled now, but we can update the info label
        date_applicable = report_type in ["Ledger Report", "Outstanding Dues Report", "Income vs Expense Report", "Payments Report", "Expenses Report"]
        if date_applicable:
            self.date_info_label.setText("(Date range will be applied to this report)")
        else:
            self.date_info_label.setText("(Date range applies to Ledger, Outstanding Dues, Income vs Expense, Payments, and Expenses reports)")
    
    def generate_report(self):
        report_type = self.report_type_combo.currentText()
        
        try:
            if report_type == "Ledger Report":
                self.generate_ledger_report()
            elif report_type == "Resident List":
                self.generate_resident_report()
            elif report_type == "Payment Summary":
                self.generate_payment_summary()
            elif report_type == "Expense Summary":
                self.generate_expense_summary()
            elif report_type == "Outstanding Dues Report":
                self.generate_outstanding_dues_report()
            elif report_type == "Income vs Expense Report":
                self.generate_income_expense_report()
            elif report_type == "Payments Report":
                self.generate_payments_report()
            elif report_type == "Expenses Report":
                self.generate_expenses_report()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def generate_ledger_report(self):
        self.status_label.setText("Generating ledger report...")
        self.repaint()  # Force UI update
        
        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username
            
            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            report_generator = ReportGenerator()
            file_path = report_generator.generate_ledger_report(
                generated_by,
                start_date=start_date,
                end_date=end_date
            )
            
            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Ledger report generated successfully!\n\nSaved to: {file_path}")
            
            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate ledger report: {str(e)}")
    
    def generate_resident_report(self):
        self.status_label.setText("Generating resident report...")
        self.repaint()  # Force UI update
        
        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username

            report_generator = ReportGenerator()
            file_path = report_generator.generate_resident_list_report(generated_by)

            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Resident list report generated successfully!\n\nSaved to: {file_path}")

            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate resident list report: {str(e)}")
    
    def generate_payment_summary(self):
        self.status_label.setText("Generating payment summary...")
        self.repaint()  # Force UI update
        
        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username

            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            report_generator = ReportGenerator()
            file_path = report_generator.generate_payment_summary_report(
                generated_by,
                start_date=start_date,
                end_date=end_date
            )

            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Payment summary report generated successfully!\n\nSaved to: {file_path}")

            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate payment summary report: {str(e)}")
    
    def generate_expense_summary(self):
        self.status_label.setText("Generating expense summary...")
        self.repaint()  # Force UI update
        
        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username

            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            report_generator = ReportGenerator()
            file_path = report_generator.generate_expense_summary_report(
                generated_by,
                start_date=start_date,
                end_date=end_date
            )

            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Expense summary report generated successfully!\n\nSaved to: {file_path}")

            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate expense summary report: {str(e)}")
    
    def generate_outstanding_dues_report(self):
        self.status_label.setText("Generating outstanding dues report...")
        self.repaint()  # Force UI update

        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username

            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            report_generator = ReportGenerator()
            file_path = report_generator.generate_outstanding_dues_report(
                generated_by,
                start_date=start_date,
                end_date=end_date
            )

            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Outstanding dues report generated successfully!\n\nSaved to: {file_path}")

            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate outstanding dues report: {str(e)}")

    def generate_income_expense_report(self):
        self.status_label.setText("Generating income vs expense report...")
        self.repaint()  # Force UI update

        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username

            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            report_generator = ReportGenerator()
            file_path = report_generator.generate_income_expense_report(
                generated_by,
                start_date=start_date,
                end_date=end_date
            )

            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Income vs Expense report generated successfully!\n\nSaved to: {file_path}")

            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate income vs expense report: {str(e)}")
    
    def generate_payments_report(self):
        self.status_label.setText("Generating payments report...")
        self.repaint()  # Force UI update

        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username

            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            report_generator = ReportGenerator()
            file_path = report_generator.generate_payments_report(
                generated_by,
                start_date=start_date,
                end_date=end_date
            )

            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Payments report generated successfully!\n\nSaved to: {file_path}")

            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate payments report: {str(e)}")
    
    def generate_expenses_report(self):
        self.status_label.setText("Generating expenses report...")
        self.repaint()  # Force UI update

        try:
            # Get the username from the main window
            generated_by = "System User"  # Default value
            if hasattr(self.parent(), 'parent') and self.parent().parent():
                main_window = self.parent().parent()
                if hasattr(main_window, 'username'):
                    generated_by = main_window.username

            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            report_generator = ReportGenerator()
            file_path = report_generator.generate_expenses_report(
                generated_by,
                start_date=start_date,
                end_date=end_date
            )

            self.status_label.setText(f"Report generated successfully: {file_path}")
            QMessageBox.information(self, "Success", f"Expenses report generated successfully!\n\nSaved to: {file_path}")

            # Optionally open the file location
            self.open_file_location(file_path)
        except Exception as e:
            self.status_label.setText("Error generating report")
            QMessageBox.critical(self, "Error", f"Failed to generate expenses report: {str(e)}")
    
    def open_file_location(self, file_path):
        """
        Open the file location in the system explorer
        """
        try:
            directory = os.path.dirname(file_path)
            if os.name == 'nt':  # Windows
                os.startfile(directory)
            elif os.name == 'posix':  # macOS or Linux
                os.system(f'open "{directory}"' if sys.platform == 'darwin' else f'xdg-open "{directory}"')
        except Exception as e:
            print(f"Could not open file location: {e}")

