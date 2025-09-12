# Society Management System

A desktop application for managing residential society operations built with Python, PyQt5, and SQLite.

## Features

- **User Authentication**: Secure login system with role-based access control (System Admin, Admin, Treasurer, Viewer).
- **Resident Management**: Add, edit, view, and search resident information with car and scooter tracking.
- **Financial Tracking**: Record and manage payments and expenses with a ledger system.
- **Bank Reconciliation**: Match ledger transactions with bank statements (CSV and PDF formats) to ensure financial accuracy.
- **Transaction Reversal**: Safely reverse erroneous transactions with proper audit trail and documentation.
- **Reporting**: Generate detailed PDF reports of financial transactions, including outstanding dues reports and income vs expense analysis with charts.
- **User Management**: System Admins and Admins can manage user accounts and roles.
- **Society Configuration**: Set up and manage basic society information.
- **Database Backup**: Create backups of the entire database for safekeeping.
- **Dark Mode**: Toggle between light and dark themes for comfortable viewing in different lighting conditions.

## Technology Stack

- **Language**: Python 3
- **GUI Framework**: PyQt5
- **Database**: SQLite
- **Reporting**: reportlab (PDF generation)
- **Data Handling**: pandas, openpyxl (Excel exports)
- **Data Visualization**: matplotlib (Charts in reports)
- **PDF Processing**: PyMuPDF (PDF bank statement import)

## Installation

1. **Prerequisites**: Ensure Python 3.6 or higher is installed on your system.
2. **Clone or Download**: Obtain the project files.
3. **Install Dependencies**: Run the following command in the project directory:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install PDF Processing Library**: For bank statement PDF import functionality:
   ```bash
   pip install PyMuPDF
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

1. **Resident Management**: Handles all resident data with enhanced vehicle tracking.
2. **Ledger**: Tracks all financial transactions.
3. **Bank Reconciliation**: Match ledger transactions with bank statements to ensure accuracy.
4. **Transaction Reversal**: Safely reverse erroneous transactions with proper documentation and audit trail.
5. **Reports**: Creates PDF reports of ledger data, including:
   - Ledger Report: Complete transaction history
   - Outstanding Dues Report: List of residents with unpaid maintenance fees
   - Income vs Expense Report: Financial analysis with visual charts comparing income and expenses by category
   - Payments Report: Detailed list of all payment transactions
   - Expenses Report: Detailed list of all expense transactions
   - Payment Summary Report: Summary of payments by category with detailed transaction list
   - Expense Summary Report: Summary of expenses by category with detailed transaction list
   - Resident List Report: Complete list of all residents
6. **User Management** (Admin/System Admin only): Manages user accounts.
7. **Society Setup** (Admin/System Admin only): Configures society details.

## Menu Options

### File Menu
- **Backup Database**: Create a complete backup of the database file with timestamp
- **Exit**: Close the application

### Tools Menu (Admin/System Admin only)
- **User Management**: Manage user accounts and roles
- **Society Setup**: Configure society information

## Bank Reconciliation

The application now includes a comprehensive bank reconciliation feature that allows users to match ledger transactions with bank statements to ensure financial accuracy and detect discrepancies.

### Key Features

- **Multiple Format Support**: Import bank statements in both CSV and PDF formats
- **Automatic Matching**: Smart algorithm matches transactions based on amount and date proximity
- **Visual Interface**: Side-by-side view of ledger and bank transactions with color-coded status indicators
- **Manual Reconciliation**: Select and match transactions manually with confirmation dialogs
- **Duplicate Prevention**: Prevents importing the same bank statement entries multiple times
- **Audit Trail**: Tracks all reconciliation activities with timestamps and user information

### How to Use Bank Reconciliation

1. Navigate to the Ledger tab
2. Click on the "Reconciliation" sub-tab
3. Set the date range for reconciliation
4. Click "Import Bank Statement" and select your CSV or PDF file
5. Click "Find Matches" to identify potential matches between ledger and bank entries
6. Review highlighted matches (yellow = high confidence)
7. Select ledger transactions and corresponding bank entries
8. Click "Mark Selected as Matched" to reconcile
9. View reconciliation status with color coding:
   - **Green**: Matched/reconciled entries
   - **Red**: Unmatched entries
   - **Yellow**: Potential matches

### Supported Bank Statement Formats

**CSV Format**: 
- Automatically detects common column names (Date, Description, Amount, Balance, Reference)
- Supports various date formats (DD/MM/YYYY, MM/DD/YYYY, etc.)
- Handles different number formats and currency symbols

**PDF Format**:
- Extracts text content using PyMuPDF library
- Parses transaction data using regular expressions
- Supports common transaction patterns:
  - `DD/MM/YYYY Description Amount`
  - `DD-MM-YYYY Description Amount`

### Technical Implementation

The reconciliation system includes:
- Database schema updates with reconciliation status tracking
- Dedicated models for bank statement management
- Intelligent matching algorithm with confidence scoring
- Duplicate prevention mechanisms
- Comprehensive error handling and user feedback

## Transaction Reversal

The application implements a comprehensive transaction reversal system that follows best accounting practices to ensure accuracy, transparency, and compliance in financial records.

### Key Features

- **Safe Reversal**: Instead of deleting transactions, the system creates reversal entries that maintain a complete audit trail
- **Authorization Control**: Only authorized users (Admin, Treasurer, System Admin) can reverse transactions
- **Reason Documentation**: Users must select from predefined reasons and add remarks for each reversal
- **Audit Trail**: All reversals are tracked with timestamps and user information
- **Period Management**: Transactions in closed periods are handled according to accounting standards
- **Error Prevention**: The system prevents duplicate reversals and validates all operations

### How to Reverse a Transaction

1. Navigate to the Ledger tab
2. Locate the transaction you want to reverse in the transaction table
3. Select the transaction by clicking on its row
4. Click the "Reverse Selected Transaction" button
5. In the reversal dialog:
   - Review the transaction details
   - Select a reason for reversal from the dropdown
   - Add any additional remarks
   - Click "OK" to complete the reversal
6. The system will create a new transaction with opposite values and refresh the ledger display

### Reversal Reasons

The system provides predefined reasons for transaction reversals:
- Entered in Error
- Duplicate Entry
- Wrong Amount
- Wrong Account
- Wrong Period
- Other

### Compliance

The transaction reversal system is designed to comply with Generally Accepted Accounting Principles (GAAP) and International Financial Reporting Standards (IFRS) by:
- Maintaining complete audit trails
- Preventing permanent deletion of posted transactions
- Ensuring proper documentation and authorization
- Following standard accounting period practices

For detailed technical information about the implementation, see [TRANSACTION_REVERSAL_PROCEDURE.md](TRANSACTION_REVERSAL_PROCEDURE.md).

## Reports

The application generates various PDF reports:

1. **Ledger Report**: Complete transaction history with running balances and date range filtering.
2. **Outstanding Dues Report**: Lists residents who have not paid maintenance fees, showing the number of months due and the total amount owed, with date range filtering.
3. **Income vs Expense Report**: Financial summary showing income and expenses by category with a visual chart comparison, with date range filtering.
4. **Payments Report**: Detailed list of all payment transactions with transaction IDs, dates, flat numbers, categories, descriptions, amounts, and payment modes, with date range filtering.
5. **Expenses Report**: Detailed list of all expense transactions with transaction IDs, dates, categories, descriptions, amounts, payment modes, and entered by information, with date range filtering.
6. **Payment Summary Report**: Summary of payments grouped by category with both summary view and detailed transaction list including transaction IDs and dates, with date range filtering.
7. **Expense Summary Report**: Summary of expenses grouped by category with both summary view and detailed transaction list including transaction IDs and dates, with date range filtering.
8. **Resident List Report**: Complete list of all residents.

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

## Login Security

The application implements login security measures to protect against unauthorized access:

- **Account Lockout**: After 5 failed login attempts, an account is locked for 30 minutes
- **Failed Attempt Tracking**: The system tracks failed login attempts for each user
- **Automatic Unlock**: Locked accounts are automatically unlocked after the lockout period expires

### Resetting Login Security

If accounts become locked and you need to reset the security measures, you can use the provided reset script:

```bash
python reset_login_security.py
```

This script will:
- Reset failed login attempts for all users to 0
- Unlock any accounts that were locked due to failed attempts
- Display the security status before and after the reset

## Recent Improvements

- Enhanced watermark visibility by placing it at three horizontal locations (top, middle, and bottom) instead of a single rotated watermark
- Added comprehensive payment and expense reports with detailed transaction information
- Improved summary reports to include both category summaries and detailed transaction lists with transaction IDs and dates
- Made date range fields always visible and functional for all report types in the GUI
- Implemented proper error handling and user feedback for all report generation operations
- Added database backup functionality accessible through the File menu
- Implemented login security with account lockout after multiple failed attempts
- Added login security reset functionality
- Added dark mode toggle for improved user experience in different lighting conditions
- **Modernized login page with two-section design (form on left, image on right)** - See [LOGIN_PAGE_IMPROVEMENTS.md](LOGIN_PAGE_IMPROVEMENTS.md) for details
- **Added bank reconciliation feature with CSV and PDF import support**
- **Enhanced resident management with car and scooter number tracking**
- **Implemented comprehensive transaction reversal system**
- **Enhanced database error handling with comprehensive testing procedures**

## Database

The application uses an SQLite database (`society_management.db`) to store all data. A backup of the initial database schema is provided as `society_management.db.backup`.

Helper scripts for development and database setup are available in the `ai_agent_utils` directory.

## Testing

Comprehensive testing procedures are available for verifying the application's functionality:

1. **Database Error Handling Testing**: See [DATABASE_ERROR_HANDLING_TESTING_PROCEDURE.md](DATABASE_ERROR_HANDLING_TESTING_PROCEDURE.md) and [DATABASE_ERROR_HANDLING_TESTING_USAGE.md](DATABASE_ERROR_HANDLING_TESTING_USAGE.md)
2. **Login Security Testing**: Run `python test_login_security.py`

## License

This project is proprietary and intended for use by NextGen Advisors.