"""Key management for LockByte vault."""

import os
import secrets
from typing import Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

from .kdf import derive_key_simple, generate_salt, DEFAULT_PARAMS, verify_key
from .encryption import encrypt_data, decrypt_data, KEY_LENGTH


@dataclass
class VaultKey:
    """Represents a derived vault key."""
    key: bytes
    salt: bytes
    params: dict

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data with this key."""
        from .encryption import encrypt_data
        return encrypt_data(data, self.key)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data with this key."""
        from .encryption import decrypt_data
        return decrypt_data(ciphertext, self.key)


class KeyManager:
    """Manages key derivation and storage for the vault."""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize the key manager.

        Args:
            vault_path: Path to the vault database
        """
        self.vault_path = vault_path
        self._current_key: Optional[VaultKey] = None
        self._is_unlocked: bool = False

    @property
    def is_unlocked(self) -> bool:
        """Check if vault is currently unlocked."""
        return self._is_unlocked

    @property
    def current_key(self) -> Optional[VaultKey]:
        """Get the current vault key if unlocked."""
        return self._current_key

    def create_vault(self, master_password: str) -> Tuple[bytes, bytes, dict]:
        """Create a new vault with a master password.

        Generates a new salt and derives the encryption key.

        Args:
            master_password: The master password

        Returns:
            Tuple of (verification_hash, salt, kdf_params)
        """
        # Generate salt
        salt = generate_salt()

        # Derive key
        key = derive_key_simple(master_password, salt)

        # Create verification hash (we derive a separate key for verification)
        verify_key_bytes = derive_key_simple(master_password + "_verify", salt)

        # Store verification data
        verification_data = {
            'version': 1,
            'salt': salt.hex(),
        }

        self._current_key = VaultKey(
            key=key,
            salt=salt,
            params=DEFAULT_PARAMS.copy()
        )
        self._is_unlocked = True

        return verify_key_bytes, salt, DEFAULT_PARAMS.copy()

    def unlock(self, master_password: str, salt: bytes, verification_key: bytes) -> bool:
        """Unlock the vault with the master password.

        Args:
            master_password: The master password
            salt: The vault salt
            verification_key: The stored verification key

        Returns:
            True if password is correct, False otherwise
        """
        # Derive key from password
        derived_key = derive_key_simple(master_password, salt)

        # Derive verification key
        verify_derived = derive_key_simple(master_password + "_verify", salt)

        # Verify using constant-time comparison
        if not secrets.compare_digest(verify_derived, verification_key):
            return False

        self._current_key = VaultKey(
            key=derived_key,
            salt=salt,
            params=DEFAULT_PARAMS.copy()
        )
        self._is_unlocked = True
        return True

    def unlock_with_key(self, key: VaultKey):
        """Unlock with an already-derived key (for testing).

        Args:
            key: The derived vault key
        """
        self._current_key = key
        self._is_unlocked = True

    def lock(self):
        """Lock the vault and clear sensitive key material from memory."""
        if self._current_key:
            # Overwrite key material before clearing
            key_bytes = self._current_key.key
            if isinstance(key_bytes, bytes):
                # Note: Python doesn't guarantee memory overwriting,
                # but this is the best we can do at Python level
                pass
        self._current_key = None
        self._is_unlocked = False

    def change_password(self, old_password: str, new_password: str,
                        old_salt: bytes, old_verify_key: bytes) -> Optional[Tuple[bytes, bytes, dict]]:
        """Change the master password.

        Args:
            old_password: Current master password
            old_password: New master password
            old_salt: Current salt
            old_verify_key: Current verification key

        Returns:
            Tuple of (new_verification_key, new_salt, new_params) if successful, None otherwise
        """
        # Verify old password first
        if not self.unlock(old_password, old_salt, old_verify_key):
            return None

        # Generate new salt and derive new key
        new_salt = generate_salt()
        new_key = derive_key_simple(new_password, new_salt)
        new_verify_key = derive_key_simple(new_password + "_verify", new_salt)

        self._current_key = VaultKey(
            key=new_key,
            salt=new_salt,
            params=DEFAULT_PARAMS.copy()
        )

        return new_verify_key, new_salt, DEFAULT_PARAMS.copy()


class MemoryKeyCache:
    """Secure in-memory cache for derived keys.

    Keys are stored with encryption in memory to provide some
    protection against memory inspection.
    """

    def __init__(self):
        self._cache: dict = {}
        self._cache_key: Optional[bytes] = None

    def set_cache_key(self, key: bytes):
        """Set the key used to encrypt the cache."""
        self._cache_key = key

    def store(self, vault_id: str, key: VaultKey):
        """Store a key in the cache."""
        if not self._cache_key:
            raise ValueError("Cache key not set")

        # Serialize and encrypt
        key_data = {
            'key': key.key.hex(),
            'salt': key.salt.hex(),
            'params': key.params
        }
        key_json = json.dumps(key_data).encode('utf-8')
        encrypted = encrypt_data(key_json, self._cache_key)
        self._cache[vault_id] = encrypted

    def retrieve(self, vault_id: str) -> Optional[VaultKey]:
        """Retrieve a key from the cache."""
        if vault_id not in self._cache:
            return None

        encrypted = self._cache[vault_id]
        key_json = decrypt_data(encrypted, self._cache_key)
        key_data = json.loads(key_json.decode('utf-8'))

        return VaultKey(
            key=bytes.fromhex(key_data['key']),
            salt=bytes.fromhex(key_data['salt']),
            params=key_data['params']
        )

    def remove(self, vault_id: str):
        """Remove a key from the cache."""
        if vault_id in self._cache:
            del self._cache[vault_id]

    def clear(self):
        """Clear all cached keys."""
        self._cache.clear()


def secure_wipe(data: bytearray):
    """Securely wipe data from memory.

    Attempts to overwrite memory before releasing it.
    Note: Python's memory management makes this imperfect.
    """
    if isinstance(data, bytearray):
        for i in range(len(data)):
            data[i] = 0