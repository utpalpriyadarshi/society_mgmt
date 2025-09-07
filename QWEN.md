# Society Management System - Project Context

## Project Overview

This is a desktop application for managing residential society operations. It is built using Python with PyQt5 for the graphical user interface and SQLite for the database.

The application provides modules for:

- Resident Management
- Payment Tracking
- Expense Management
- Reporting

The system uses a role-based access control mechanism (System Admin, Admin, Treasurer, Viewer).

## Technology Stack

- **Language:** Python 3
- **GUI Framework:** PyQt5
- **Database:** SQLite
- **Other Libraries:**
  - matplotlib (for reports)
  - reportlab (for generating PDF reports)
  - openpyxl (for Excel exports)
  - pandas (for data manipulation)

## Project Structure

- `main.py`: Entry point of the application. Initializes the GUI application and shows the login dialog.
- `database.py`: Contains the `Database` class for initializing and managing the SQLite database schema.
- `gui/`: Directory containing all PyQt5 GUI components.
  - `login_dialog.py`: Implements the login dialog window.
  - `main_window.py`: Implements the main application window with tabbed modules.
  - `resident_form.py`: Implements the resident management tab.
  - `user_management_dialog.py`: Implements the user management dialog.
- `models/`: (Inferred) Likely contains data models and managers for interacting with the database (e.g., `resident.py`).
- `utils/`: Utility functions.
  - `security.py`: Handles password hashing and user authentication.
- `ai_agent_utils/`: Directory containing helper scripts for development and database operations.

## Key Components

1.  **Login System:** Users must log in before accessing the main application. Authentication is handled by `utils/security.py`.
2.  **Main Window:** The main application interface is a `QMainWindow` with a `QTabWidget`. Tabs are dynamically added based on the user's role (System Admin, Admin, Treasurer, Viewer).
3.  **Database:** An SQLite database (`society_management.db`) is used to store resident information, ledger transactions, expenses, and user accounts. The schema is defined in `database.py`.
4.  **User Management:** System Admin and Admin users can manage other users and their roles through the User Management dialog.
5.  **Modules:**
    - **Resident Management:** Allows adding, editing, and viewing resident details.
    - **Payments:** Tracks financial transactions related to residents.
    - **Expenses:** Manages society expenses.
    - **Reports:** Generates reports on financial status, resident lists, etc.

## Building and Running

1.  **Install Dependencies:** Ensure Python 3 is installed. Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Application:** Execute the main script:
    ```bash
    python main.py
    ```

## Development Conventions

- GUI components are implemented using PyQt5 classes (QDialog, QMainWindow, QWidget, etc.).
- Database interactions are encapsulated within manager classes (e.g., `ResidentManager`).
- Passwords are hashed using SHA-256 before being stored or compared.
- The application structure separates concerns into GUI, database, models, and utilities.
- Helper scripts for development and database operations are stored in the `ai_agent_utils/` directory.
- All helper scripts created during development should be placed in the `ai_agent_utils/` directory to keep the main project directory clean and organized.