# How to Run the Login Dialog Directly

The original error occurred because when you tried to run `login_dialog.py` directly, Python couldn't find the `utils` module due to path issues. I've implemented two solutions:

## Solution 1: Added Path Configuration
At the top of `gui/login_dialog.py`, I added these lines:
```python
import sys
import os

# Add the parent directory to the Python path so imports work correctly when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

This ensures that when the file is run directly, Python can find the `utils` module and other project modules.

## Solution 2: Added Main Block
I also added this code at the end of the file:
```python
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = LoginDialog()
    dialog.show()
    sys.exit(app.exec_())
```

## How to Run the Login Dialog Directly

You can now run the login dialog directly in two ways:

1. As a module (recommended):
   ```bash
   cd C:\Users\utpal\OneDrive\Desktop\Programming\SocietyMgmtV1.0
   python -m gui.login_dialog
   ```

2. Using the interactive_login_test.py script:
   ```bash
   cd C:\Users\utpal\OneDrive\Desktop\Programming\SocietyMgmtV1.0
   python interactive_login_test.py
   ```

Both approaches will properly set up the Python path and allow the imports to work correctly.