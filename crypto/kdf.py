"""Key Derivation Function using Argon2id."""

import secrets
from typing import Tuple
from argon2 import low_level

# Argon2id parameters - balanced for security and usability
DEFAULT_PARAMS = {
    'memory_cost': 65536,  # 64 MB
    'time_cost': 3,
    'parallelism': 4,
    'salt_length': 32,  # 256 bits
    'key_length': 32,   # 256 bits
}


def generate_salt(length: int = None) -> bytes:
    """Generate a cryptographically secure random salt."""
    if length is None:
        length = DEFAULT_PARAMS['salt_length']
    return secrets.token_bytes(length)


def derive_key(
    password: str,
    salt: bytes,
    memory_cost: int = None,
    time_cost: int = None,
    parallelism: int = None,
    key_length: int = None
) -> bytes:
    """Derive a cryptographic key from a password using Argon2id."""
    # Use defaults
    if memory_cost is None:
        memory_cost = DEFAULT_PARAMS['memory_cost']
    if time_cost is None:
        time_cost = DEFAULT_PARAMS['time_cost']
    if parallelism is None:
        parallelism = DEFAULT_PARAMS['parallelism']
    if key_length is None:
        key_length = DEFAULT_PARAMS['key_length']

    # Encode password
    password_bytes = password.encode('utf-8')

    # Use argon2-cffi low-level API for direct key derivation
    result = low_level.hash_secret_raw(
        secret=password_bytes,
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=key_length,
        type=low_level.Type.ID  # Argon2id
    )

    return result


def derive_key_simple(password: str, salt: bytes) -> bytes:
    """Simple key derivation using Argon2id with default parameters."""
    return derive_key(
        password=password,
        salt=salt,
        memory_cost=DEFAULT_PARAMS['memory_cost'],
        time_cost=DEFAULT_PARAMS['time_cost'],
        parallelism=DEFAULT_PARAMS['parallelism'],
        key_length=DEFAULT_PARAMS['key_length']
    )


def verify_key(password: str, salt: bytes, expected_key: bytes) -> bool:
    """Verify that a password produces the expected key."""
    try:
        derived = derive_key_simple(password, salt)
        return secrets.compare_digest(derived, expected_key)
    except Exception:
        return False


def create_key_pair(password: str) -> Tuple[bytes, bytes, dict]:
    """Create a new key pair from a password."""
    salt = generate_salt()
    params = DEFAULT_PARAMS.copy()
    key = derive_key_simple(password, salt)
    return key, salt, params


def hash_password_for_storage(password: str, salt: bytes = None) -> Tuple[str, bytes]:
    """Create a hash suitable for password verification storage."""
    from argon2 import PasswordHasher

    if salt is None:
        salt = generate_salt()

    ph = PasswordHasher(
        time_cost=DEFAULT_PARAMS['time_cost'],
        memory_cost=DEFAULT_PARAMS['memory_cost'],
        parallelism=DEFAULT_PARAMS['parallelism']
    )

    hash_str = ph.hash(password)
    return hash_str, salt


def verify_stored_password(password: str, hash_str: str) -> bool:
    """Verify a password against a stored hash."""
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError

    ph = PasswordHasher()

    try:
        ph.verify(hash_str, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        return False