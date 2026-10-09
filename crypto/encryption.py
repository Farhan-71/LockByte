"""Authenticated encryption for LockByte vault data."""

import os
import secrets
from typing import Tuple, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend


# AES-256-GCM provides both confidentiality and authenticity
KEY_LENGTH = 32  # 256 bits
NONCE_LENGTH = 12  # 96 bits (recommended for AES-GCM)
TAG_LENGTH = 16  # 128 bits (appended to ciphertext)


def generate_nonce(length: int = None) -> bytes:
    """Generate a cryptographically secure random nonce.

    Args:
        length: Nonce length in bytes. Defaults to NONCE_LENGTH (12)

    Returns:
        Random nonce bytes
    """
    if length is None:
        length = NONCE_LENGTH
    return secrets.token_bytes(length)


def derive_subkey(master_key: bytes, context: str) -> bytes:
    """Derive a subkey from the master key using HKDF.

    This ensures different keys for different purposes (encryption, HMAC, etc.)

    Args:
        master_key: Master key bytes
        context: Context string for key derivation

    Returns:
        Derived subkey
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=context.encode('utf-8'),
        info=b'lockbyte-subkey',
        backend=default_backend()
    )
    return hkdf.derive(master_key)


def encrypt_data(plaintext: bytes, key: bytes, nonce: bytes = None) -> bytes:
    """Encrypt data using AES-256-GCM (authenticated encryption).

    Args:
        plaintext: Data to encrypt
        key: 32-byte encryption key
        nonce: 12-byte nonce (generated if None)

    Returns:
        Nonce + ciphertext + auth tag (combined)

    Raises:
        ValueError: If key length is invalid
    """
    if len(key) != KEY_LENGTH:
        raise ValueError(f"Key must be {KEY_LENGTH} bytes, got {len(key)}")

    if nonce is None:
        nonce = generate_nonce()

    if len(nonce) != NONCE_LENGTH:
        raise ValueError(f"Nonce must be {NONCE_LENGTH} bytes, got {len(nonce)}")

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    # Return nonce || ciphertext (tag is appended by AESGCM)
    return nonce + ciphertext


def decrypt_data(ciphertext: bytes, key: bytes) -> bytes:
    """Decrypt data using AES-256-GCM.

    Args:
        ciphertext: Nonce + ciphertext + auth tag
        key: 32-byte decryption key

    Returns:
        Decrypted plaintext

    Raises:
        ValueError: If decryption fails (invalid key, tampered data, etc.)
    """
    if len(key) != KEY_LENGTH:
        raise ValueError(f"Key must be {KEY_LENGTH} bytes, got {len(key)}")

    if len(ciphertext) < NONCE_LENGTH + TAG_LENGTH:
        raise ValueError("Ciphertext too short")

    nonce = ciphertext[:NONCE_LENGTH]
    actual_ciphertext = ciphertext[NONCE_LENGTH:]

    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, actual_ciphertext, None)
        return plaintext
    except Exception as e:
        raise ValueError("Decryption failed - invalid key or tampered data") from e


def encrypt_string(plaintext: str, key: bytes, encoding: str = 'utf-8') -> bytes:
    """Encrypt a string.

    Args:
        plaintext: String to encrypt
        key: Encryption key
        encoding: Text encoding (default: utf-8)

    Returns:
        Encrypted bytes (nonce + ciphertext + tag)
    """
    plaintext_bytes = plaintext.encode(encoding)
    return encrypt_data(plaintext_bytes, key)


def decrypt_string(ciphertext: bytes, key: bytes, encoding: str = 'utf-8') -> str:
    """Decrypt to a string.

    Args:
        ciphertext: Encrypted bytes
        key: Decryption key
        encoding: Text encoding (default: utf-8)

    Returns:
        Decrypted string
    """
    plaintext_bytes = decrypt_data(ciphertext, key)
    return plaintext_bytes.decode(encoding)


def encrypt_dict(data: dict, key: bytes) -> bytes:
    """Encrypt a dictionary (JSON serialized).

    Args:
        data: Dictionary to encrypt
        key: Encryption key

    Returns:
        Encrypted bytes
    """
    import json
    json_str = json.dumps(data, separators=(',', ':'), sort_keys=True)
    return encrypt_string(json_str, key)


def decrypt_dict(ciphertext: bytes, key: bytes) -> dict:
    """Decrypt to a dictionary.

    Args:
        ciphertext: Encrypted bytes
        key: Decryption key

    Returns:
        Decrypted dictionary
    """
    import json
    json_str = decrypt_string(ciphertext, key)
    return json.loads(json_str)


class EncryptedVault:
    """Helper class for encrypting/decrypting vault data."""

    def __init__(self, key: bytes):
        """Initialize with a vault key.

        Args:
            key: 32-byte vault encryption key
        """
        if len(key) != KEY_LENGTH:
            raise ValueError(f"Key must be {KEY_LENGTH} bytes")
        self._key = key

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data."""
        return encrypt_data(plaintext, self._key)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data."""
        return decrypt_data(ciphertext, self._key)

    def encrypt_str(self, plaintext: str) -> bytes:
        """Encrypt a string."""
        return encrypt_string(plaintext, self._key)

    def decrypt_str(self, ciphertext: bytes) -> str:
        """Decrypt to a string."""
        return decrypt_string(ciphertext, self._key)

    def encrypt_dict(self, data: dict) -> bytes:
        """Encrypt a dictionary."""
        return encrypt_dict(data, self._key)

    def decrypt_dict(self, ciphertext: bytes) -> dict:
        """Decrypt to a dictionary."""
        return decrypt_dict(ciphertext, self._key)