# Fernet module is imported from the
# cryptography package
from cryptography.fernet import Fernet

# key is generated
key = Fernet.generate_key()
print(key.decode())
