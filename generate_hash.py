"""
Generate bcrypt hash for systemadmin password
"""
import bcrypt

# Generate hash for "systemadmin"
password = "systemadmin"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

print(f"Password: {password}")
print(f"Generated hash: {hashed.decode('utf-8')}")

# Test verification
result = bcrypt.checkpw(password.encode('utf-8'), hashed)
print(f"Verification result: {result}")