# User Management System

## User Roles

The Society Management System supports four distinct user roles with different levels of access:

1. **System Admin** (Topmost role)
   - Full access to all system features
   - Can manage all users including other System Admins
   - Can perform system-level operations
   - Cannot be deleted through the UI

2. **Admin** (Application administrator)
   - Can manage residents, payments, and expenses
   - Can generate reports
   - Can manage users (except System Admins)
   - Can access all modules

3. **Treasurer**
   - Can manage payments and expenses
   - Can generate reports
   - Cannot manage users or residents

4. **Viewer**
   - Read-only access
   - Can only view reports
   - Cannot make any modifications

## Default Users

When the system is first initialized, a default System Admin user is created:
- Username: `sysadmin`
- Password: `systemadmin`

**Important:** Please change this default password immediately after first login for security reasons.

## User Management

Admin and System Admin users can access the User Management feature through the "Tools" menu. This interface allows them to:
- Add new users
- Edit existing users (except System Admins for System Admins)
- Delete users (except System Admins and the last Admin user)
- Assign roles to users

## Helper Scripts

Several helper scripts are available in the `ai_agent_utils` directory for development and database management:

- `create_system_admin.py` - Creates the default System Admin user
- `create_admin.py` - Creates a default Admin user
- `init_db.py` - Initializes the database schema
- `check_users.py` - Lists all users in the database

## Security Notes

- All passwords are hashed using SHA-256 before storage
- User roles determine access levels throughout the application
- The system prevents deletion of the last Admin user to ensure continued administrative access