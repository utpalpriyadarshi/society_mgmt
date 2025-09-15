#!/usr/bin/env python3
"""
Interactive Login Test Script
This script allows you to run the login dialog directly for testing purposes.
"""
import sys
import os

# Add the parent directory to the Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QDialog
from gui.login_dialog import LoginDialog

def main():
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    
    # Show the login dialog
    if login_dialog.exec_() == QDialog.Accepted:
        print("Login successful!")
        # You could continue with the main window here if needed
    else:
        print("Login cancelled")
    
    sys.exit(0)

if __name__ == "__main__":
    main()