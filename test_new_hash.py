"""
Test the new bcrypt hash
"""
import bcrypt

# Test password and new hash
password = "systemadmin"
stored_hash = "$2b$12$ks61E9uJb/7v42mQw3thnu7xxVyv6iKBRU2jUPRWZzeD/oQRVOHqK"

print(f"Password: {password}")
print(f"Stored hash: {stored_hash}")

# Test bcrypt verification
password_bytes = password.encode('utf-8')
hash_bytes = stored_hash.encode('utf-8')

result = bcrypt.checkpw(password_bytes, hash_bytes)
print(f"bcrypt.checkpw result: {result}")

if result:
    print("✓ Bcrypt verification SUCCESSFUL")
else:
    print("✗ Bcrypt verification FAILED")