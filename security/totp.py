"""TOTP/2FA support for LockByte."""

import sys
from pathlib import Path
import base64
import hashlib
import hmac
import time
import urllib.parse
from typing import Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto.secure_random import secure_random_bytes


class TOTPGenerator:
    """Generates and manages TOTP codes."""

    DEFAULT_PERIOD = 30  # Seconds
    DEFAULT_CODE_LENGTH = 6
    DEFAULT_DIGITS = 6

    def __init__(self, period: int = None, code_length: int = None):
        """Initialize TOTP generator.

        Args:
            period: Time step in seconds (default 30)
            code_length: Number of digits in code (default 6)
        """
        self.period = period or self.DEFAULT_PERIOD
        self.code_length = code_length or self.DEFAULT_CODE_LENGTH

    def generate(self, secret: str, timestamp: int = None) -> str:
        """Generate a TOTP code.

        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (current if None)

        Returns:
            TOTP code string
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Calculate time counter
        counter = timestamp // self.period

        # Decode secret
        secret_bytes = self._decode_secret(secret)

        # Generate code
        code = self._generate_code(secret_bytes, counter)

        return code

    def verify(self, secret: str, code: str, timestamp: int = None, window: int = 1) -> bool:
        """Verify a TOTP code with a time window.

        Args:
            secret: Base32-encoded secret
            code: Code to verify
            timestamp: Unix timestamp (current if None)
            window: Number of time steps before/after to check

        Returns:
            True if code is valid
        """
        if timestamp is None:
            timestamp = int(time.time())

        for offset in range(-window, window + 1):
            check_time = timestamp + (offset * self.period)
            expected = self.generate(secret, check_time)
            if hmac.compare_digest(expected, code):
                return True

        return False

    def get_remaining_time(self, timestamp: int = None) -> int:
        """Get remaining seconds in current time window.

        Args:
            timestamp: Unix timestamp (current if None)

        Returns:
            Seconds until next time step
        """
        if timestamp is None:
            timestamp = int(time.time())

        elapsed = timestamp % self.period
        return self.period - elapsed

    def generate_uri(self, secret: str, issuer: str, account: str) -> str:
        """Generate a TOTP URI for QR code generation.

        Args:
            secret: Base32-encoded secret
            issuer: Issuer name (e.g., company name)
            account: Account identifier (e.g., email)

        Returns:
            TOTP URI string
        """
        # URL encode parameters
        issuer_encoded = urllib.parse.quote(issuer)
        account_encoded = urllib.parse.quote(account)

        uri = f"otpauth://totp/{issuer_encoded}:{account_encoded}"
        uri += f"?secret={secret}"
        uri += f"&issuer={issuer_encoded}"
        uri += f"&period={self.period}"
        uri += f"&digits={self.code_length}"

        return uri

    def _decode_secret(self, secret: str) -> bytes:
        """Decode a base32 secret.

        Args:
            secret: Base32-encoded secret (may have padding removed)

        Returns:
            Decoded bytes
        """
        # Add padding if necessary
        padding_needed = 8 - (len(secret) % 8)
        if padding_needed != 8:
            secret += '=' * padding_needed

        return base64.b32decode(secret.upper())

    def _generate_code(self, secret: bytes, counter: int) -> str:
        """Generate a TOTP code from secret and counter.

        Args:
            secret: Secret bytes
            counter: Time counter

        Returns:
            TOTP code string
        """
        # Convert counter to bytes (8 bytes, big-endian)
        counter_bytes = counter.to_bytes(8, 'big')

        # HMAC-SHA1
        hmac_result = hmac.new(secret, counter_bytes, hashlib.sha1).digest()

        # Dynamic truncation
        offset = hmac_result[-1] & 0x0F
        binary = (
            ((hmac_result[offset] & 0x7F) << 24) |
            ((hmac_result[offset + 1] & 0xFF) << 16) |
            ((hmac_result[offset + 2] & 0xFF) << 8) |
            (hmac_result[offset + 3] & 0xFF)
        )

        # Generate code
        code = binary % (10 ** self.code_length)

        return str(code).zfill(self.code_length)


class TOTPManager:
    """Manages TOTP secrets in the vault."""

    def __init__(self, key_manager):
        """Initialize TOTP manager.

        Args:
            key_manager: Vault key manager for encryption
        """
        self.key_manager = key_manager
        self.generator = TOTPGenerator()

    def generate_secret(self, length: int = 20) -> str:
        """Generate a new TOTP secret.

        Args:
            length: Secret length in bytes (default 20)

        Returns:
            Base32-encoded secret
        """
        return secure_random_bytes(length)

    def create_totp_entry(self, website: str, secret: str, account: str) -> dict:
        """Create a TOTP entry for storage.

        Args:
            website: Website name
            secret: Base32 secret
            account: Account identifier

        Returns:
            TOTP entry dictionary
        """
        return {
            'website': website,
            'secret': secret,
            'account': account,
            'created_at': int(time.time())
        }

    def get_current_code(self, secret: str) -> str:
        """Get the current TOTP code for a secret.

        Args:
            secret: Base32 secret

        Returns:
            Current TOTP code
        """
        return self.generator.generate(secret)

    def get_uri(self, secret: str, issuer: str, account: str) -> str:
        """Get TOTP URI for QR code.

        Args:
            secret: Base32 secret
            issuer: Issuer name
            account: Account identifier

        Returns:
            TOTP URI string
        """
        return self.generator.generate_uri(secret, issuer, account)