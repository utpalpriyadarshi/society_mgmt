# PowerShell script to create automated database backup task at 1:00 PM
# Save this as create_backup_task_1pm.ps1 in your project directory

$Action = New-ScheduledTaskAction -Execute "C:\Users\utpal\OneDrive\Desktop\Programming\SocietyMgmtV1.0\ai_agent_utils\backup_scheduler.bat" -WorkingDirectory "C:\Users\utpal\OneDrive\Desktop\Programming\SocietyMgmtV1.0"
$Trigger = New-ScheduledTaskTrigger -Daily -At 1PM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest

Register-ScheduledTask -TaskName "Society Management Database Backup" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Daily automated backup of the Society Management System database at 1:00 PM"