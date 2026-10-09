"""Secure password and passphrase generation."""

import secrets
import string
from typing import List, Optional


class PasswordGenerator:
    """Generates cryptographically secure passwords and passphrases."""

    # Default character sets
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Ambiguous characters to exclude
    AMBIGUOUS_UPPER = "IO"
    AMBIGUOUS_LOWER = "l"
    AMBIGUOUS_DIGITS = "01"

    # Diceware-style word list (subset for demonstration)
    WORD_LIST = [
        "apple", "banana", "cherry", "delta", "echo", "foxtrot", "golf", "hotel",
        "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
        "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey",
        "xray", "yankee", "zulu", "alpha", "bravo", "charlie", "dog", "easy",
        "fox", "green", "house", "item", "jig", "king", "love", "metal",
        "nice", "open", "page", "queen", "rock", "sugar", "tree", "unit",
        "vase", "water", "xenon", "year", "zebra", "able", "baker", "capture"
    ]

    @classmethod
    def generate(
        cls,
        length: int = 16,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_digits: bool = True,
        include_symbols: bool = True,
        exclude_ambiguous: bool = False,
        min_uppercase: int = 0,
        min_lowercase: int = 0,
        min_digits: int = 0,
        min_symbols: int = 0
    ) -> str:
        """Generate a cryptographically secure password.

        Args:
            length: Password length (default 16)
            include_uppercase: Include uppercase letters
            include_lowercase: Include lowercase letters
            include_digits: Include digits
            include_symbols: Include symbols
            exclude_ambiguous: Exclude ambiguous characters (I, O, l, 0, 1)
            min_uppercase: Minimum uppercase characters
            min_lowercase: Minimum lowercase characters
            min_digits: Minimum digits
            min_symbols: Minimum symbols

        Returns:
            Generated password

        Raises:
            ValueError: If constraints cannot be satisfied
        """
        # Build character pool
        char_pool = []
        required_chars = []

        if include_uppercase:
            chars = cls.UPPERCASE
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in cls.AMBIGUOUS_UPPER)
            char_pool.extend(chars)
            if min_uppercase > 0:
                required_chars.extend([secrets.choice(chars) for _ in range(min_uppercase)])

        if include_lowercase:
            chars = cls.LOWERCASE
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in cls.AMBIGUOUS_LOWER)
            char_pool.extend(chars)
            if min_lowercase > 0:
                required_chars.extend([secrets.choice(chars) for _ in range(min_lowercase)])

        if include_digits:
            chars = cls.DIGITS
            if exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in cls.AMBIGUOUS_DIGITS)
            char_pool.extend(chars)
            if min_digits > 0:
                required_chars.extend([secrets.choice(chars) for _ in range(min_digits)])

        if include_symbols:
            char_pool.extend(cls.SYMBOLS)
            if min_symbols > 0:
                required_chars.extend([secrets.choice(cls.SYMBOLS) for _ in range(min_symbols)])

        if not char_pool:
            raise ValueError("At least one character type must be included")

        # Calculate minimum required length
        min_required = len(required_chars)
        if length < min_required:
            raise ValueError(f"Length {length} is too short for minimum requirements ({min_required})")

        # Generate password
        password = list(required_chars)

        # Fill remaining length
        remaining = length - len(password)
        password.extend(secrets.choice(char_pool) for _ in range(remaining))

        # Shuffle to avoid predictable positions
        # Use Fisher-Yates with secrets for cryptographic shuffle
        for i in range(len(password) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password[i], password[j] = password[j], password[i]

        return ''.join(password)

    @classmethod
    def generate_passphrase(
        cls,
        word_count: int = 4,
        separator: str = "-",
        capitalize: bool = False,
        include_number: bool = False,
        include_symbol: bool = False,
        min_word_length: int = 3,
        max_word_length: int = 12
    ) -> str:
        """Generate a memorable passphrase.

        Args:
            word_count: Number of words (default 4)
            separator: Word separator (default "-")
            capitalize: Capitalize each word
            include_number: Add a random number
            include_symbol: Add a random symbol
            min_word_length: Minimum word length
            max_word_length: Maximum word length

        Returns:
            Generated passphrase
        """
        # Filter words by length
        valid_words = [
            w for w in cls.WORD_LIST
            if min_word_length <= len(w) <= max_word_length
        ]

        if not valid_words:
            valid_words = cls.WORD_LIST

        # Select random words
        words = [secrets.choice(valid_words) for _ in range(word_count)]

        # Apply options
        if capitalize:
            words = [w.capitalize() for w in words]

        # Build passphrase
        passphrase = separator.join(words)

        # Add number and/or symbol
        extras = []
        if include_number:
            extras.append(str(secrets.randbelow(100)))
        if include_symbol:
            extras.append(secrets.choice(cls.SYMBOLS))

        if extras:
            passphrase += separator + separator.join(extras)

        return passphrase

    @classmethod
    def generate_pin(cls, length: int = 6) -> str:
        """Generate a random PIN.

        Args:
            length: PIN length (default 6)

        Returns:
            Numeric PIN string
        """
        return ''.join(secrets.choice(cls.DIGITS) for _ in range(length))

    @classmethod
    def generate_hex(cls, length: int = 32) -> str:
        """Generate a random hex string.

        Args:
            length: Length of hex string

        Returns:
            Random hex string
        """
        bytes_needed = (length + 1) // 2
        return secrets.token_hex(bytes_needed)[:length]

    @classmethod
    def estimate_strength(cls, password: str) -> dict:
        """Estimate password strength.

        Args:
            password: Password to analyze

        Returns:
            Dictionary with strength info
        """
        from .password_analyzer import PasswordStrengthAnalyzer

        analysis = PasswordStrengthAnalyzer.analyze(password)
        return {
            'strength': analysis.strength_level.value,
            'entropy': analysis.entropy,
            'length': analysis.length,
            'recommendations': analysis.recommendations
        }