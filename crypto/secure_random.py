"""Cryptographically secure random generation for passwords and tokens."""

import secrets
import string
import random
from typing import List, Optional


def secure_random_bytes(length: int) -> bytes:
    """Generate cryptographically secure random bytes.

    Args:
        length: Number of bytes to generate

    Returns:
        Random bytes
    """
    return secrets.token_bytes(length)


def secure_random_hex(length: int) -> str:
    """Generate cryptographically secure random hex string.

    Args:
        length: Length of hex string (number of characters)

    Returns:
        Random hex string
    """
    return secrets.token_hex(length // 2 + length % 2)[:length]


def secure_random_base64(length: int) -> str:
    """Generate cryptographically secure random base64 string.

    Args:
        length: Length of base64 string (number of characters)

    Returns:
        Random base64 string
    """
    import base64
    random_bytes = secure_random_bytes(length)
    return base64.b64encode(random_bytes).decode('utf-8')[:length]


def secure_random_string(length: int, alphabet: str = None) -> str:
    """Generate cryptographically secure random string.

    Args:
        length: Length of string
        alphabet: Custom alphabet (default: alphanumeric)

    Returns:
        Random string
    """
    if alphabet is None:
        alphabet = string.ascii_letters + string.digits

    if not alphabet:
        raise ValueError("Alphabet cannot be empty")

    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_password(
    length: int = 16,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    include_digits: bool = True,
    include_symbols: bool = True,
    exclude_ambiguous: bool = True
) -> str:
    """Generate a cryptographically secure password.

    Args:
        length: Password length
        include_uppercase: Include uppercase letters
        include_lowercase: Include lowercase letters
        include_digits: Include digits
        include_symbols: Include symbols
        exclude_ambiguous: Exclude ambiguous characters (Il1O0)

    Returns:
        Generated password

    Raises:
        ValueError: If constraints make generation impossible
    """
    character_sets = []

    if include_uppercase:
        uppercase = string.ascii_uppercase
        if exclude_ambiguous:
            uppercase = uppercase.replace('I', '').replace('O', '')
        character_sets.append(uppercase)

    if include_lowercase:
        lowercase = string.ascii_lowercase
        if exclude_ambiguous:
            lowercase = lowercase.replace('l', '')
        character_sets.append(lowercase)

    if include_digits:
        digits = string.digits
        if exclude_ambiguous:
            digits = digits.replace('0', '').replace('1', '')
        character_sets.append(digits)

    if include_symbols:
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        character_sets.append(symbols)

    if not character_sets:
        raise ValueError("At least one character set must be selected")

    # Ensure at least one character from each selected set
    password_chars = []
    for charset in character_sets:
        password_chars.append(secrets.choice(charset))

    # Fill remaining length with random characters from all sets combined
    all_chars = ''.join(character_sets)
    remaining_length = length - len(password_chars)
    if remaining_length < 0:
        raise ValueError(f"Minimum password length for selected character sets is {len(password_chars)}")

    password_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))

    # Shuffle to avoid predictable pattern
    random.shuffle(password_chars)

    return ''.join(password_chars)


def generate_passphrase(
    word_count: int = 4,
    separator: str = '-',
    capitalize: bool = False,
    add_number: bool = False,
    add_symbol: bool = False
) -> str:
    """Generate a passphrase using diceware method.

    Args:
        word_count: Number of words in passphrase
        separator: Word separator
        capitalize: Capitalize each word
        add_number: Add a random number at the end
        add_symbol: Add a random symbol at the end

    Returns:
        Generated passphrase
    """
    # Diceware word list - a small subset for demonstration
    # In production, use a full diceware list
    diceware_words = [
        "apple", "banana", "cherry", "date", "elderberry",
        "fig", "grape", "honeydew", "imbe", "jujube",
        "kiwi", "lemon", "mango", "nectarine", "orange",
        "papaya", "quince", "raspberry", "strawberry", "tangerine",
        "ugli", "vanilla", "watermelon", "xigua", "yuzu", "zucchini",
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
        "golf", "hotel", "india", "juliett", "kilo", "lima",
        "mike", "november", "oscar", "papa", "quebec", "romeo",
        "sierra", "tango", "uniform", "victor", "whiskey",
        "xray", "yankee", "zulu"
    ]

    # Select random words
    words = [secrets.choice(diceware_words) for _ in range(word_count)]

    # Apply options
    if capitalize:
        words = [word.capitalize() for word in words]

    passphrase = separator.join(words)

    # Add optional extras
    extras = []
    if add_number:
        extras.append(str(secrets.randbelow(100)))
    if add_symbol:
        extras.append(secrets.choice("!@#$%^&*"))

    if extras:
        passphrase += separator + ''.join(extras)

    return passphrase


def generate_totp_secret(length: int = 20) -> str:
    """Generate a TOTP secret key.

    Args:
        length: Secret length in bytes (default 20, recommended 20-32)

    Returns:
        Base32 encoded secret
    """
    import base64

    # Generate random bytes
    secret_bytes = secure_random_bytes(length)

    # Convert to base32 (standard for TOTP)
    secret_b32 = base64.b32encode(secret_bytes).decode('utf-8')

    # Remove padding
    return secret_b32.rstrip('=')


def estimate_password_entropy(password: str) -> float:
    """Estimate the entropy of a password.

    Args:
        password: The password to analyze

    Returns:
        Estimated entropy in bits
    """
    if not password:
        return 0.0

    # Determine character pool size
    char_pool = 0
    has_lower = any(c in string.ascii_lowercase for c in password)
    has_upper = any(c in string.ascii_uppercase for c in password)
    has_digit = any(c in string.digits for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    if has_lower:
        char_pool += 26
    if has_upper:
        char_pool += 26
    if has_digit:
        char_pool += 10
    if has_symbol:
        char_pool += 32  # Common symbols

    # If we couldn't determine pool, use a conservative estimate
    if char_pool == 0:
        char_pool = 94  # ASCII printable characters

    # Entropy = log2(pool_size^length)
    return len(password) * (char_pool.bit_length() - 1)


class PasswordStrength:
    """Helper for password strength analysis."""

    STRENGTH_LEVELS = [
        (0, "Very Weak"),
        (40, "Weak"),
        (60, "Fair"),
        (80, "Good"),
        (100, "Strong"),
        (120, "Very Strong"),
    ]

    @classmethod
    def get_strength_level(cls, password: str) -> str:
        """Get the strength level description for a password.

        Args:
            password: The password to evaluate

        Returns:
            Strength level description
        """
        entropy = estimate_password_entropy(password)

        for threshold, level in reversed(cls.STRENGTH_LEVELS):
            if entropy >= threshold:
                return level

        return "Very Weak"