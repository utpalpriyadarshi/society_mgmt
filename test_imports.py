"""
Test script to verify all imports work correctly
"""
import sys
import os

print("Testing imports for Society Management System...")

# Test PyQt5 imports
try:
    from PyQt5.QtWidgets import QApplication, QDialog
    from PyQt5.QtCore import Qt
    print("+ PyQt5 imports successful")
except Exception as e:
    print("- PyQt5 import failed:", str(e))

# Test main modules
try:
    from gui.login_dialog import LoginDialog
    print("+ Login dialog import successful")
except Exception as e:
    print("- Login dialog import failed:", str(e))

try:
    from gui.main_window import MainWindow
    print("+ Main window import successful")
except Exception as e:
    print("- Main window import failed:", str(e))

try:
    from utils.security import authenticate_user
    print("+ Security module import successful")
except Exception as e:
    print("- Security module import failed:", str(e))

# Test database
try:
    from database import Database
    print("+ Database module import successful")
except Exception as e:
    print("- Database module import failed:", str(e))

print("\nImport test completed.")