# Database Backup Setup Instructions

## Automated Backup Solution

I've implemented a comprehensive automated backup solution for the Society Management System:

1. **Backup Script** (`ai_agent_utils/backup_database.py`):
   - Creates timestamped backups of the database
   - Stores backups in a dedicated `backups` directory
   - Verifies backup integrity
   - Automatically cleans up old backups (default: keeps backups for 7 days)
   - Supports flexible retention policies in both days and minutes

2. **Scheduler Script** (`ai_agent_utils/backup_scheduler.bat`):
   - Windows batch file to run the backup script
   - Can be scheduled with Windows Task Scheduler

## Setup Instructions

### Option 1: Manual Backup
Run the backup script manually at any time:
```bash
python ai_agent_utils/backup_database.py --verify
```

### Option 2: Scheduled Backups (Windows)
1. Open Windows Task Scheduler
2. Create a new task
3. Set the trigger to daily (or your preferred frequency)
4. Set the action to start a program:
   - Program: `C:\Users\utpal\OneDrive\Desktop\Programming\SocietyMgmtV1.0\ai_agent_utils\backup_scheduler.bat`
   - Start in: `C:\Users\utpal\OneDrive\Desktop\Programming\SocietyMgmtV1.0`

### Option 3: Scheduled Backups (Linux/Mac)
Create a cron job by running `crontab -e` and adding a line like:
```bash
0 2 * * * cd /path/to/SocietyMgmtV1.0 && python ai_agent_utils/backup_database.py
```
This would run the backup daily at 2 AM.

## Features
- **Timestamped backups**: Each backup has a unique timestamp
- **Verification**: Optional backup verification to ensure integrity
- **Automatic cleanup**: Removes backups older than specified retention period
- **Flexible retention**: Supports retention periods in both days and minutes
- **Configurable**: Easy to adjust backup location and retention period
- **Error handling**: Reports errors if backup fails

## Usage Examples
```bash
# Create a backup with default settings (7-day retention)
python ai_agent_utils/backup_database.py

# Create a backup with custom retention (30 days)
python ai_agent_utils/backup_database.py --keep-days 30

# Create a backup with minute-level retention (keep last 60 minutes)
python ai_agent_utils/backup_database.py --keep-mins 60

# Create a backup and verify its integrity
python ai_agent_utils/backup_database.py --verify

# Create a backup with custom retention and verification
python ai_agent_utils/backup_database.py --keep-days 14 --verify
```

## Testing
A test backup was successfully created and verified, confirming that the solution works correctly.