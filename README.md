# Society Management System

A desktop application for managing residential society operations built with Python, PyQt5, and SQLite.

## Features

- **User Authentication**: Secure login system with role-based access control (System Admin, Admin, Treasurer, Viewer).
- **Resident Management**: Add, edit, view, and search resident information.
- **Financial Tracking**: Record and manage payments and expenses with a ledger system.
- **Reporting**: Generate detailed PDF reports of financial transactions, including outstanding dues reports and income vs expense analysis with charts.
- **User Management**: System Admins and Admins can manage user accounts and roles.
- **Society Configuration**: Set up and manage basic society information.
- **Database Backup**: Create backups of the entire database for safekeeping.

## Technology Stack

- **Language**: Python 3
- **GUI Framework**: PyQt5
- **Database**: SQLite
- **Reporting**: reportlab (PDF generation)
- **Data Handling**: pandas, openpyxl (Excel exports)
- **Data Visualization**: matplotlib (Charts in reports)

## Installation

1. **Prerequisites**: Ensure Python 3.6 or higher is installed on your system.
2. **Clone or Download**: Obtain the project files.
3. **Install Dependencies**: Run the following command in the project directory:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Execute the main script:
```bash
python main.py
```

On first run, a default System Admin user is created:
- **Username**: `sysadmin`
- **Password**: `systemadmin`

It's highly recommended to change this password after the first login.

## User Roles and Permissions

- **System Admin**:
  - Full access to all features.
  - Manage all users, including other System Admins.
- **Admin**:
  - Manage residents.
  - Record payments and expenses.
  - Generate reports.
  - Manage other users (except System Admins).
  - Configure society details.
- **Treasurer**:
  - Manage residents.
  - Record payments and expenses.
  - Generate reports.
- **Viewer**:
  - View residents and financial reports.

## Modules

1. **Resident Management**: Handles all resident data.
2. **Ledger**: Tracks all financial transactions.
3. **Reports**: Creates PDF reports of ledger data, including:
   - Ledger Report: Complete transaction history
   - Outstanding Dues Report: List of residents with unpaid maintenance fees
   - Income vs Expense Report: Financial analysis with visual charts comparing income and expenses by category
   - Payments Report: Detailed list of all payment transactions
   - Expenses Report: Detailed list of all expense transactions
   - Payment Summary Report: Summary of payments by category with detailed transaction list
   - Expense Summary Report: Summary of expenses by category with detailed transaction list
   - Resident List Report: Complete list of all residents
4. **User Management** (Admin/System Admin only): Manages user accounts.
5. **Society Setup** (Admin/System Admin only): Configures society details.

## Menu Options

### File Menu
- **Backup Database**: Create a complete backup of the database file with timestamp
- **Exit**: Close the application

### Tools Menu (Admin/System Admin only)
- **User Management**: Manage user accounts and roles
- **Society Setup**: Configure society information

## Reports

The application generates various PDF reports:

1. **Ledger Report**: Complete transaction history with running balances and date range filtering.
2. **Outstanding Dues Report**: Lists residents who have not paid maintenance fees, showing the number of months due and the total amount owed, with date range filtering.
3. **Income vs Expense Report**: Financial summary showing income and expenses by category with a visual chart comparison, with date range filtering.
4. **Payments Report**: Detailed list of all payment transactions with transaction IDs, dates, flat numbers, categories, descriptions, amounts, and payment modes, with date range filtering.
5. **Expenses Report**: Detailed list of all expense transactions with transaction IDs, dates, categories, descriptions, amounts, payment modes, and entered by information, with date range filtering.
6. **Payment Summary Report**: Summary of payments grouped by category with both summary view and detailed transaction list including transaction IDs and dates, with date range filtering.
7. **Expense Summary Report**: Summary of expenses grouped by category with both summary view and detailed transaction list including transaction IDs and dates, with date range filtering.
8. **Resident List Report**: Complete list of all residents with their details.

All reports include:
- Society header with name, address, and contact information
- Watermark for authenticity (visible at three locations: top, middle, and bottom of each page)
- Page numbers and generation timestamps
- Consistent formatting and styling
- Date range filtering for applicable reports

## Database Backup

The application provides a built-in database backup feature accessible through the File menu. This feature allows users to create complete copies of the database file for safekeeping. Key features include:

- **Complete Database Copy**: Creates an exact copy of the entire database file
- **Timestamped Filenames**: Automatically generates filenames with timestamps for easy identification
- **User-Selected Location**: Allows users to choose where to save the backup file
- **Error Handling**: Provides clear feedback for successful backups or any issues that occur
- **Metadata Preservation**: Preserves all file metadata using proper copying techniques

To create a backup:
1. Open the File menu
2. Select "Backup Database"
3. Choose a location and filename (or use the auto-generated timestamped name)
4. Click "Save" to create the backup

It's recommended to create regular backups of the database, especially before making significant changes or updates to the system.

## Recent Improvements

- Enhanced watermark visibility by placing it at three horizontal locations (top, middle, and bottom) instead of a single rotated watermark
- Added comprehensive payment and expense reports with detailed transaction information
- Improved summary reports to include both category summaries and detailed transaction lists with transaction IDs and dates
- Made date range fields always visible and functional for all report types in the GUI
- Implemented proper error handling and user feedback for all report generation operations
- Added database backup functionality accessible through the File menu

## Database

The application uses an SQLite database (`society_management.db`) to store all data. A backup of the initial database schema is provided as `society_management.db.backup`.

Helper scripts for development and database setup are available in the `ai_agent_utils` directory.

## License

This project is proprietary and intended for use by NextGen Advisors.