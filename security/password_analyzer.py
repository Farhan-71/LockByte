"""Password analysis and strength evaluation."""

import sys
from pathlib import Path
import re
import string
from typing import List, Tuple
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vault.models import PasswordStrengthLevel, PasswordAnalysis


class PasswordStrengthAnalyzer:
    """Analyzes password strength and generates recommendations."""

    # Common weak passwords
    COMMON_PASSWORDS = {
        'password', '123456', '12345678', 'qwerty', 'abc123',
        'monkey', '1234567', 'letmein', 'trustno1', 'dragon',
        'baseball', '111111', 'iloveyou', 'master', 'sunshine',
        'ashley', 'bailey', 'passw0rd', 'shadow', '123123'
    }

    # Keyboard patterns
    KEYBOARD_PATTERNS = [
        'qwerty', 'asdfgh', 'zxcvbn', 'qazwsx', '1234567', '123456',
        '1qaz', '2wsx', 'qweasd', 'qweasdzxc'
    ]

    MIN_STRONG_LENGTH = 12
    MIN_GOOD_LENGTH = 10
    MIN_FAIR_LENGTH = 8

    @classmethod
    def analyze(cls, password: str, password_id: str = "", check_reuse: bool = False,
                reuse_count: int = 0) -> PasswordAnalysis:
        """Analyze a password's strength.

        Args:
            password: Password to analyze
            password_id: ID for this password analysis
            check_reuse: Whether to check for reuse
            reuse_count: Number of times this password is reused

        Returns:
            PasswordAnalysis object
        """
        if not password:
            return PasswordAnalysis(
                password_id=password_id,
                strength_level=PasswordStrengthLevel.VERY_WEAK,
                entropy=0,
                length=0,
                has_uppercase=False,
                has_lowercase=False,
                has_digits=False,
                has_symbols=False,
                has_repeating_chars=False,
                has_sequences=False,
                is_common=True,
                is_reused=check_reuse and reuse_count > 0,
                reuse_count=reuse_count,
                recommendations=["Password cannot be empty"]
            )

        # Character set analysis
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_symbol = bool(re.search(r'[!@#$%^&*()_\-+=\[\]{}|;:,.<>?/\\~`"\']', password))

        # Pattern analysis
        has_repeating = cls._has_repeating_chars(password)
        has_sequences = cls._has_sequences(password)
        is_common = password.lower() in cls.COMMON_PASSWORDS
        is_keyboard = cls._is_keyboard_pattern(password)

        # Entropy calculation
        entropy = cls._calculate_entropy(password)

        # Determine strength
        strength = cls._determine_strength(
            len(password), has_upper, has_lower, has_digit, has_symbol,
            has_repeating, has_sequences, is_common, entropy
        )

        # Generate recommendations
        recommendations = cls._generate_recommendations(
            password, has_upper, has_lower, has_digit, has_symbol,
            has_repeating, has_sequences, is_common, is_keyboard, reuse_count
        )

        return PasswordAnalysis(
            password_id=password_id,
            strength_level=strength,
            entropy=entropy,
            length=len(password),
            has_uppercase=has_upper,
            has_lowercase=has_lower,
            has_digits=has_digit,
            has_symbols=has_symbol,
            has_repeating_chars=has_repeating,
            has_sequences=has_sequences,
            is_common=is_common,
            is_reused=check_reuse and reuse_count > 0,
            reuse_count=reuse_count,
            recommendations=recommendations
        )

    @classmethod
    def _has_repeating_chars(cls, password: str) -> bool:
        """Check for repeating characters."""
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True
        return False

    @classmethod
    def _has_sequences(cls, password: str) -> bool:
        """Check for sequential characters."""
        for i in range(len(password) - 2):
            c1, c2, c3 = ord(password[i]), ord(password[i + 1]), ord(password[i + 2])
            # Sequential or reverse sequential
            if (c2 == c1 + 1 and c3 == c2 + 1) or (c2 == c1 - 1 and c3 == c2 - 1):
                return True
        return False

    @classmethod
    def _is_keyboard_pattern(cls, password: str) -> bool:
        """Check for keyboard patterns."""
        password_lower = password.lower()
        for pattern in cls.KEYBOARD_PATTERNS:
            if pattern in password_lower or pattern[::-1] in password_lower:
                return True
        return False

    @classmethod
    def _calculate_entropy(cls, password: str) -> float:
        """Calculate password entropy in bits."""
        char_pool = set(password)
        pool_size = len(char_pool)

        # Estimate based on character types
        estimated_pool = 0
        if any(c in string.ascii_lowercase for c in password):
            estimated_pool += 26
        if any(c in string.ascii_uppercase for c in password):
            estimated_pool += 26
        if any(c in string.digits for c in password):
            estimated_pool += 10
        if any(c in string.punctuation for c in password):
            estimated_pool += 32

        if estimated_pool == 0:
            estimated_pool = pool_size

        # Entropy = log2(pool_size ^ length)
        import math
        return len(password) * math.log2(estimated_pool) if estimated_pool > 0 else 0

    @classmethod
    def _determine_strength(cls, length: int, has_upper: bool, has_lower: bool,
                           has_digit: bool, has_symbol: bool, has_repeating: bool,
                           has_sequences: bool, is_common: bool, entropy: float) -> PasswordStrengthLevel:
        """Determine password strength level."""
        if is_common or length < 6:
            return PasswordStrengthLevel.VERY_WEAK

        if has_repeating or has_sequences:
            return PasswordStrengthLevel.WEAK

        char_type_count = sum([has_upper, has_lower, has_digit, has_symbol])

        if length >= cls.MIN_STRONG_LENGTH and entropy >= 80 and char_type_count >= 3:
            return PasswordStrengthLevel.VERY_STRONG
        elif length >= cls.MIN_GOOD_LENGTH and entropy >= 60 and char_type_count >= 3:
            return PasswordStrengthLevel.STRONG
        elif length >= cls.MIN_GOOD_LENGTH and char_type_count >= 2:
            return PasswordStrengthLevel.GOOD
        elif length >= cls.MIN_FAIR_LENGTH and char_type_count >= 2:
            return PasswordStrengthLevel.FAIR
        elif length >= 6 and char_type_count >= 1:
            return PasswordStrengthLevel.WEAK
        else:
            return PasswordStrengthLevel.VERY_WEAK

    @classmethod
    def _generate_recommendations(cls, password: str, has_upper: bool, has_lower: bool,
                                 has_digit: bool, has_symbol: bool, has_repeating: bool,
                                 has_sequences: bool, is_common: bool, is_keyboard: bool,
                                 reuse_count: int) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if is_common:
            recommendations.append("Avoid common passwords")

        if len(password) < cls.MIN_GOOD_LENGTH:
            recommendations.append(f"Use at least {cls.MIN_GOOD_LENGTH} characters")

        if not has_upper:
            recommendations.append("Add uppercase letters")

        if not has_lower:
            recommendations.append("Add lowercase letters")

        if not has_digit:
            recommendations.append("Add numbers")

        if not has_symbol:
            recommendations.append("Add special characters (!@#$%^&* etc)")

        if has_repeating:
            recommendations.append("Avoid repeating characters (aaa, 111)")

        if has_sequences:
            recommendations.append("Avoid sequential characters (abc, 123)")

        if is_keyboard:
            recommendations.append("Avoid keyboard patterns (qwerty, asdfgh)")

        if reuse_count > 0:
            recommendations.append(f"This password is reused {reuse_count} times - consider changing it")

        if not recommendations:
            recommendations.append("This is a strong password")

        return recommendations


class PasswordReuse:
    """Detects password reuse across credentials."""

    @staticmethod
    def find_reused_passwords(credentials: List) -> dict:
        """Find reused passwords across credentials.

        Args:
            credentials: List of credential objects

        Returns:
            Dictionary mapping password hash to list of credential IDs
        """
        import hashlib

        reuse_map = {}

        for credential in credentials:
            password_hash = hashlib.sha256(credential.password.encode('utf-8')).hexdigest()

            if password_hash not in reuse_map:
                reuse_map[password_hash] = []

            reuse_map[password_hash].append({
                'credential_id': credential.id,
                'website': credential.website,
                'username': credential.username
            })

        # Filter to only show reused
        return {k: v for k, v in reuse_map.items() if len(v) > 1}

    @staticmethod
    def get_reuse_count(password: str, credentials: List) -> int:
        """Get count of how many times a password is used.

        Args:
            password: The password to check
            credentials: List of credentials

        Returns:
            Number of times this password appears
        """
        count = 0
        for credential in credentials:
            if credential.password == password:
                count += 1
        return count