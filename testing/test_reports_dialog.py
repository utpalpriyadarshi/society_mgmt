"""
Script to test the GUI changes for the reports dialog
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.reports_dialog import ReportsDialog

def main():
    app = QApplication(sys.argv)
    dialog = ReportsDialog()
    dialog.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()