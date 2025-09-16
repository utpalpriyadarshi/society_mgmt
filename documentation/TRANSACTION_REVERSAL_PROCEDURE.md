# TRANSACTION REVERSAL PROCEDURE

## Overview

This document outlines the procedure for deleting or reversing transactions in the Society Management System's accounting module. The system implements best practices to ensure accuracy, transparency, and compliance in financial records.

## Key Principles

1. **Prefer Reversal Over Deletion**: Once a transaction has been posted to the ledger, it should be reversed rather than deleted to maintain an audit trail.
2. **Authorization Required**: Only authorized users can reverse transactions.
3. **Complete Documentation**: All reversals must be properly documented with reasons and remarks.
4. **Audit Trail**: Every reversal is tracked with user information and timestamps.

## Transaction Reversal Procedure

### 1. Identify the Transaction

- Navigate to the Ledger tab in the application
- Locate the transaction to be reversed in the transaction table
- Select the transaction by clicking on its row

### 2. Verify Transaction Details

The system displays the following details for verification:
- Transaction ID
- Date
- Type (Payment/Expense)
- Category
- Amount
- Description

### 3. Check Period Status

Before allowing a reversal, the system automatically checks:
- If the accounting period for the transaction is still open
- If the transaction has already been reversed

### 4. Authorization

The system verifies that the current user has appropriate permissions to reverse transactions (Admin, Treasurer, or System Admin roles).

### 5. Record the Reversal

When the user clicks "Reverse Selected Transaction":
- A reversal dialog appears with transaction details
- User must select a reason for reversal from predefined options:
  - Entered in Error
  - Duplicate Entry
  - Wrong Amount
  - Wrong Account
  - Wrong Period
  - Other
- User can add remarks to explain the reversal
- Clicking "OK" creates a new transaction with opposite values

### 6. System Actions

Upon successful reversal:
1. A new transaction is created with:
   - Opposite debit/credit values
   - Same category and description (prefixed with "REVERSAL:")
   - Today's date
   - Reference to the original transaction
2. The reversal is recorded in the transaction_reversals table
3. The ledger display is automatically refreshed

## Audit Trail

The system maintains a comprehensive audit trail for all reversals:
- Original transaction ID
- Reversal transaction ID
- Reason for reversal
- Remarks
- User who performed the reversal
- Timestamp of reversal

## Compliance Features

1. **GAAP/IFRS Compliance**: The reversal method aligns with Generally Accepted Accounting Principles
2. **No Permanent Deletion**: Posted transactions are never permanently deleted
3. **Role-Based Access**: Only authorized users can perform reversals
4. **Period Management**: Transactions in closed periods require special handling

## Database Structure

### transaction_reversals Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique identifier |
| original_transaction_id | TEXT UNIQUE | Reference to original transaction |
| reversal_transaction_id | TEXT | Reference to reversal transaction |
| reason | TEXT | Reason for reversal |
| remarks | TEXT | Additional remarks |
| reversed_by | TEXT | User who performed reversal |
| reversed_at | TIMESTAMP | Timestamp of reversal |

### Integration with Ledger Table

The reversal system works in conjunction with the existing ledger table, which contains all transaction details.

## User Interface

The reversal functionality is accessible through:
- Ledger form with a "Reverse Selected Transaction" button
- Reversal dialog that captures required information
- Real-time feedback and error handling

## Error Handling

The system handles the following error conditions:
- Transaction not found
- Transaction already reversed
- Insufficient permissions
- Invalid reversal reason
- Database errors

## Testing

All reversal functionality has been tested with various scenarios:
- Valid reversals
- Duplicate reversal attempts
- Unauthorized access attempts
- Edge cases with different transaction types

## Best Practices for Users

1. Always verify transaction details before reversing
2. Provide meaningful reasons and remarks for reversals
3. Ensure proper authorization before performing reversals
4. Review financial reports after reversals to confirm accuracy