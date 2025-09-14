import sqlite3
import pyotp
from utils.db_context import get_db_connection

def test_totp_functionality():
    # Test the TOTP functionality
    print("Testing TOTP functionality...")
    
    # Check if TOTP fields exist in the users table
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        totp_columns = [col for col in columns if 'totp' in col[1]]
        print(f"TOTP columns in users table: {[(col[1], col[2]) for col in totp_columns]}")
        
        # Check if any users have TOTP enabled
        cursor.execute("SELECT username, totp_enabled FROM users WHERE totp_enabled = 1")
        totp_users = cursor.fetchall()
        print(f"Users with TOTP enabled: {totp_users}")
        
        # Test enabling TOTP for a user
        print("\nTesting TOTP enablement for sysadmin user...")
        
        # Generate a TOTP secret
        totp_secret = pyotp.random_base32()
        print(f"Generated TOTP secret: {totp_secret}")
        
        # Update user with TOTP secret
        cursor.execute(
            "UPDATE users SET totp_secret = ?, totp_enabled = 1 WHERE username = ?",
            (totp_secret, "sysadmin")
        )
        conn.commit()
        
        print("TOTP enabled for sysadmin user")
        
        # Verify the update
        cursor.execute("SELECT totp_secret, totp_enabled FROM users WHERE username = ?", ("sysadmin",))
        result = cursor.fetchone()
        if result:
            secret, enabled = result
            print(f"Verified - Secret: {secret}, Enabled: {bool(enabled)}")
            
            # Test TOTP generation
            if secret:
                totp = pyotp.TOTP(secret)
                current_code = totp.now()
                print(f"Current TOTP code: {current_code}")
                
                # Verify the code
                is_valid = totp.verify(current_code)
                print(f"TOTP code verification: {'Passed' if is_valid else 'Failed'}")
        
        # Reset the user's TOTP settings
        cursor.execute(
            "UPDATE users SET totp_secret = NULL, totp_enabled = 0 WHERE username = ?",
            ("sysadmin",)
        )
        conn.commit()
        print("TOTP settings reset for sysadmin user")

if __name__ == "__main__":
    test_totp_functionality()