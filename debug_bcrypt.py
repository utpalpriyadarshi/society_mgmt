"""
Detailed debug script to test bcrypt authentication
"""
import bcrypt
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

def debug_bcrypt():
    print("Debugging bcrypt authentication...")
    
    # Test password and hash
    password = "systemadmin"
    stored_hash = "$2b$12$8K1p/a0dhrxiowP.dnkgNORTWgdEDHn5L2/xjpEWuC.QQv4rKO9jO"
    
    print(f"Password: {password}")
    print(f"Stored hash: {stored_hash}")
    
    # Test bcrypt verification
    print("\nTesting bcrypt verification...")
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = stored_hash.encode('utf-8')
        
        print(f"Password bytes: {password_bytes}")
        print(f"Hash bytes: {hash_bytes}")
        
        result = bcrypt.checkpw(password_bytes, hash_bytes)
        print(f"bcrypt.checkpw result: {result}")
        
        if result:
            print("✓ Bcrypt verification SUCCESSFUL")
        else:
            print("✗ Bcrypt verification FAILED")
    except Exception as e:
        print(f"Error during bcrypt verification: {e}")
    
    # Let's also test generating a new hash to compare
    print("\nTesting bcrypt hash generation...")
    try:
        # Generate a new hash for the same password
        new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        print(f"Newly generated hash: {new_hash.decode('utf-8')}")
        
        # Check if they match
        new_result = bcrypt.checkpw(password.encode('utf-8'), new_hash)
        print(f"New hash verification: {new_result}")
    except Exception as e:
        print(f"Error during bcrypt hash generation: {e}")

if __name__ == "__main__":
    debug_bcrypt()
