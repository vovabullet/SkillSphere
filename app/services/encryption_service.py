import os
import base64
import hashlib
from cryptography.fernet import Fernet

_cached_key = None


def get_encryption_key():
    global _cached_key
    if _cached_key:
        return _cached_key
    
    key = os.environ.get('ENCRYPTION_KEY')
    
    if not key:
        secret_key = os.environ.get('SESSION_SECRET', 'default-encryption-key-change-me')
        key_hash = hashlib.sha256(secret_key.encode()).digest()
        key = base64.urlsafe_b64encode(key_hash)
    elif isinstance(key, str):
        if len(key) == 44:
            key = key.encode()
        else:
            key_hash = hashlib.sha256(key.encode()).digest()
            key = base64.urlsafe_b64encode(key_hash)
    
    _cached_key = key
    return key


def get_fernet():
    return Fernet(get_encryption_key())


def encrypt_token(token):
    if not token:
        return None
    try:
        f = get_fernet()
        return f.encrypt(token.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return None


def decrypt_token(encrypted_token):
    if not encrypted_token:
        return None
    try:
        f = get_fernet()
        return f.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
