# Database Backup Feature Testing Guide

## Prerequisites
- The Society Management System should be set up and running
- Python should be installed and accessible from the command line

## Test Procedures

### 1. Manual Backup Test

#### Steps:
1. Open a command prompt or terminal
2. Navigate to the project directory:
   ```bash
   cd C:\Users\utpal\OneDrive\Desktop\Programming\SocietyMgmtV1.0
   ```
3. Run the backup script:
   ```bash
   python ai_agent_utils/backup_database.py --verify
   ```

#### Expected Results:
- A new backup file should be created in the `backups` directory with a timestamped name
- The backup should be verified successfully
- A message should indicate that the backup was created successfully
- No old backups should be removed (since this is likely the first run)

### 2. Backup Cleanup Test (Days)

#### Steps:
1. Create some test backup files with old timestamps:
   ```bash
   # On Windows (PowerShell)
   cd backups
   echo . > society_management_backup_20250101_120000.db
   echo . > society_management_backup_20250102_120000.db
   cd ..
   
   # On Linux/Mac
   cd backups
   touch society_management_backup_20250101_120000.db
   touch society_management_backup_20250102_120000.db
   cd ..
   ```
2. Modify the file timestamps to make them appear older:
   ```powershell
   # Using PowerShell to change the file timestamps
   $file1 = Get-ChildItem backups\society_management_backup_20250101_120000.db
   $file2 = Get-ChildItem backups\society_management_backup_20250102_120000.db
   $file1.LastWriteTime = (Get-Date).AddDays(-2)
   $file1.CreationTime = (Get-Date).AddDays(-2)
   $file2.LastWriteTime = (Get-Date).AddDays(-2)
   $file2.CreationTime = (Get-Date).AddDays(-2)
   ```
3. Run the backup script with a short retention period:
   ```bash
   python ai_agent_utils/backup_database.py --keep-days 1
   ```

#### Expected Results:
- The old backup files should be removed
- A message should indicate how many files were removed
- A new backup should still be created

### 3. Backup Cleanup Test (Minutes)

#### Steps:
1. Create some test backup files:
   ```bash
   # On Windows (PowerShell)
   cd backups
   echo . > society_management_backup_20250101_120000.db
   echo . > society_management_backup_20250102_120000.db
   cd ..
   
   # On Linux/Mac
   cd backups
   touch society_management_backup_20250101_120000.db
   touch society_management_backup_20250102_120000.db
   cd ..
   ```
2. Modify the file timestamps to make them appear older:
   ```powershell
   # Using PowerShell to change the file timestamps
   $file1 = Get-ChildItem backups\society_management_backup_20250101_120000.db
   $file2 = Get-ChildItem backups\society_management_backup_20250102_120000.db
   $file1.LastWriteTime = (Get-Date).AddMinutes(-45)
   $file1.CreationTime = (Get-Date).AddMinutes(-45)
   $file2.LastWriteTime = (Get-Date).AddMinutes(-45)
   $file2.CreationTime = (Get-Date).AddMinutes(-45)
   ```
3. Run the backup script with a short retention period in minutes:
   ```bash
   python ai_agent_utils/backup_database.py --keep-mins 30
   ```

#### Expected Results:
- The old backup files should be removed (as they are older than 30 minutes)
- A message should indicate how many files were removed
- A new backup should still be created

### 4. Backup Verification Test

#### Steps:
1. Run the backup script with verification enabled:
   ```bash
   python ai_agent_utils/backup_database.py --verify
   ```

#### Expected Results:
- A new backup should be created
- The backup should be verified with a message showing the SQLite version
- No errors should occur during verification

### 5. Scheduler Script Test

#### Steps:
1. Run the scheduler batch file:
   ```bash
   ai_agent_utils\backup_scheduler.bat
   ```

#### Expected Results:
- A new backup should be created in the `backups` directory
- The backup should be verified
- No errors should occur

## Verification

After running the tests, you should:
1. Check the `backups` directory to confirm that backup files were created
2. Verify that the backup files are valid SQLite databases by opening them with an SQLite browser or command-line tool
3. Confirm that old backups are properly cleaned up when the retention period expires

## Troubleshooting

If any tests fail:
1. Check that Python is properly installed and in your PATH
2. Verify that the database file exists and is accessible
3. Check the error messages for specific issues
4. Ensure that the backup directory is writable

## Test Data Cleanup

After testing, you may want to remove test backups:
```bash
# On Windows
del backups\society_management_backup_202501*.db

# On Linux/Mac
rm backups/society_management_backup_202501*.db
```