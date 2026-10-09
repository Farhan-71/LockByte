# LockByte Crypto Module
"""Cryptographic primitives for LockByte secure credential management."""

from .kdf import derive_key, derive_key_simple, generate_salt, DEFAULT_PARAMS
from .encryption import encrypt_data, decrypt_data, generate_nonce
from .key_management import KeyManager, VaultKey
from .secure_random import secure_random_bytes, secure_random_string

__all__ = [
    'derive_key',
    'derive_key_simple',
    'generate_salt',
    'generate_nonce',
    'encrypt_data',
    'decrypt_data',
    'KeyManager',
    'VaultKey',
    'secure_random_bytes',
    'secure_random_string',
    'DEFAULT_PARAMS',
]