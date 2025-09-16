# Project Overview

This is a Society Management System, a desktop application for managing residential society operations. It is built with Python, PyQt5 for the graphical user interface, and SQLite for the database.

The application features:
- **User Authentication**: Secure login with role-based access control (System Admin, Admin, Treasurer, Viewer).
- **Resident Management**: CRUD (Create, Read, Update, Delete) operations for resident information, including vehicle tracking.
- **Financial Tracking**: Recording and managing payments and expenses through a ledger system.
- **Bank Reconciliation**: Matching ledger transactions with bank statements from CSV and PDF files.
- **Transaction Reversal**: A safe way to reverse erroneous transactions while maintaining an audit trail.
- **Reporting**: Generation of detailed PDF reports for financial transactions.
- **User Management**: Management of user accounts and roles.
- **Society Configuration**: Setting up and managing society information.
- **Database Backup**: Creating backups of the database.
- **Dark Mode**: A toggle for a dark theme.

## Building and Running

To run the application, you need to have Python 3.6 or higher installed.

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    python main.py
    ```

On the first run, a default System Admin user is created with the username `sysadmin` and password `systemadmin`.

## Development Conventions

- **Code Style**: The project follows standard Python coding conventions (PEP 8).
- **Database**: The application uses an SQLite database (`society_management.db`). Database schema changes are managed through migrations located in the `ai_agent_utils/migrations` directory.
- **Error Handling**: The application uses custom exception classes for database-related errors, defined in `utils/database_exceptions.py`. A context manager in `utils/db_context.py` handles database connections and errors.
- **Modularity**: The application is structured into several packages:
    - `gui`: Contains all the PyQt5 UI components.
    - `models`: Defines the data models and data access logic for different modules.
    - `utils`: Provides utility functions for security, audit logging, and database management.
- **Testing**: The project has some tests, for example `test_login_security.py` and `test_database_error_handling.py`.
