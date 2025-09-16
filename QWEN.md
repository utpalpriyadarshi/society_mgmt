# Society Management System - Project Context

## Project Overview

This is a desktop application for managing residential society operations. It is built using Python with PyQt5 for the graphical user interface and SQLite for the database.

The application provides modules for:

- Resident Management
- Payment Tracking
- Expense Management
- Bank Reconciliation
- Transaction Reversal
- Reporting
- User Management
- Audit Logging

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
  - bcrypt (for password hashing)
  - PyMuPDF (for PDF bank statement import)

## Project Structure

- `main.py`: Entry point of the application. Initializes the GUI application and shows the login dialog.
- `database.py`: Contains the `Database` class for initializing and managing the SQLite database schema.
- `gui/`: Directory containing all PyQt5 GUI components.
  - `login_dialog.py`: Implements the login dialog window.
  - `main_window.py`: Implements the main application window with tabbed modules.
  - `resident_form.py`: Implements the resident management tab.
  - `user_management_dialog.py`: Implements the user management dialog.
- `models/`: Contains data models and managers for interacting with the database.
  - `resident.py`: Resident data model and manager.
  - `ledger.py`: Ledger transaction data model and manager.
  - `reports.py`: Report generation functionality.
- `utils/`: Utility functions.
  - `security.py`: Handles password hashing and user authentication.
  - `session_manager.py`: Manages user sessions.
  - `audit_logger.py`: Handles audit logging of user actions.
  - `config.py`: Handles application configuration.
- `ai_agent_utils/`: Directory containing helper scripts for development and database operations.
  - `migrations/`: Database migration scripts.

## Key Components

1.  **Login System:** Users must log in before accessing the main application. Authentication is handled by `utils/security.py`. The login system includes:
    - Account lockout after 5 failed attempts for 30 minutes
    - "Remember me" functionality
    - Dark mode toggle
    - Forgot password functionality (placeholder)

2.  **Main Window:** The main application interface is a `QMainWindow` with a `QTabWidget`. Tabs are dynamically added based on the user's role (System Admin, Admin, Treasurer, Viewer).

3.  **Database:** An SQLite database (`society_management.db`) is used to store resident information, ledger transactions, expenses, and user accounts. The schema is managed through migrations.

4.  **User Management:** System Admin and Admin users can manage other users and their roles through the User Management dialog.

5.  **Modules:**
    - **Resident Management:** Allows adding, editing, and viewing resident details with car and scooter tracking.
    - **Ledger:** Tracks financial transactions.
    - **Bank Reconciliation:** Match ledger transactions with bank statements (CSV and PDF formats).
    - **Transaction Reversal:** Safely reverse erroneous transactions with proper audit trail.
    - **Reports:** Generates PDF reports on financial status, resident lists, etc.
    - **Audit Log Viewer:** View audit logs of user actions in the system.

6.  **Database Migrations:** The application uses a migration system to manage database schema changes over time. Migrations are stored in `ai_agent_utils/migrations/`.

7.  **Audit Logging:** All important actions in the system are logged to an audit trail for security and compliance purposes.

## Building and Running

1.  **Install Dependencies:** Ensure Python 3 is installed. Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
    Additionally, for bank statement PDF import functionality:
    ```bash
    pip install PyMuPDF
    ```

2.  **Run the Application:** Execute the main script:
    ```bash
    python main.py
    ```

On first run, a default System Admin user is created:
- **Username**: `sysadmin`
- **Password**: `systemadmin`

It's highly recommended to change this password after the first login.

## Development Conventions

- GUI components are implemented using PyQt5 classes (QDialog, QMainWindow, QWidget, etc.).
- Database interactions are encapsulated within manager classes (e.g., `ResidentManager`).
- Passwords are hashed using bcrypt for new accounts, with fallback to SHA-256 for legacy accounts.
- The application structure separates concerns into GUI, database, models, and utilities.
- Database schema changes are managed through migration scripts.
- All important user actions are logged to an audit trail.
- Helper scripts for development and database operations are stored in the `ai_agent_utils/` directory.
- All helper scripts created during development should be placed in the `ai_agent_utils/` directory to keep the main project directory clean and organized.

**NOTE** Never run git commit or git push commands

**NOTE** Always create ypur own helper files that you need to access db etc inside ai_agent_utils directory. Always search this directory whenever you want to check and query db as it already has a few python scripts for that