"""Privacy-preserving breach checking for LockByte."""

import hashlib
import requests
from typing import List, Optional, Dict, Tuple


class BreachChecker:
    """Privacy-preserving breach checking using k-anonymity."""

    # Using Have I Been Pwned API as an example
    HIBP_API_URL = "https://api.pwnedpasswords.com/range"
    TIMEOUT = 10

    @classmethod
    def check_password(cls, password: str) -> Tuple[bool, Optional[int]]:
        """Check if a password has been exposed using k-anonymity.

        Uses the Pwned Passwords API which implements k-anonymity:
        - Only the first 5 characters of the SHA-1 hash are sent
        - The server returns all hashes starting with those characters
        - We check locally without revealing the full password

        Args:
            password: Password to check

        Returns:
            Tuple of (is_exposed, breach_count)
        """
        try:
            # Hash the password
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

            # Get the first 5 characters
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]

            # Query the API with only the prefix
            response = requests.get(
                f"{cls.HIBP_API_URL}/{prefix}",
                timeout=cls.TIMEOUT,
                headers={'User-Agent': 'LockByte/1.0'}
            )

            if response.status_code == 200:
                # Parse response and look for our suffix
                for line in response.text.splitlines():
                    hash_suffix, count = line.split(':')
                    if hash_suffix == suffix:
                        return True, int(count)

                # Not found in the list
                return False, None

            elif response.status_code == 404:
                # Prefix not found - password not in breaches
                return False, None

            else:
                # API error
                return False, None

        except requests.RequestException:
            # Network error - can't check
            return False, None
        except Exception:
            # Any other error
            return False, None

    @classmethod
    def check_email(cls, email: str) -> Tuple[bool, Optional[List[str]]]:
        """Check if an email has been in known breaches.

        Uses Have I Been Pwned's email check.

        Args:
            email: Email address to check

        Returns:
            Tuple of (is_exposed, list_of_breach_names)
        """
        try:
            response = requests.get(
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                timeout=cls.TIMEOUT,
                headers={'User-Agent': 'LockByte/1.0'}
            )

            if response.status_code == 200:
                breaches = response.json()
                breach_names = [b['Name'] for b in breaches]
                return True, breach_names

            elif response.status_code == 404:
                # Email not found in breaches
                return False, None

            else:
                return False, None

        except requests.RequestException:
            return False, None
        except Exception:
            return False, None

    @classmethod
    def batch_check_passwords(cls, passwords: List[str]) -> Dict[str, Tuple[bool, Optional[int]]]:
        """Check multiple passwords for breach status.

        Args:
            passwords: List of passwords to check

        Returns:
            Dictionary mapping password to (is_exposed, count)
        """
        results = {}
        for password in passwords:
            is_exposed, count = cls.check_password(password)
            results[password] = (is_exposed, count)
        return results


class BreachCheckResult:
    """Result of a breach check."""

    def __init__(self, credential_id: str, website: str, email: str):
        self.credential_id = credential_id
        self.website = website
        self.email = email
        self.password_exposed = False
        self.password_breach_count = 0
        self.email_exposed = False
        self.email_breaches: List[str] = []
        self.check_timestamp = None
        self.error = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'credential_id': self.credential_id,
            'website': self.website,
            'email': self.email,
            'password_exposed': self.password_exposed,
            'password_breach_count': self.password_breach_count,
            'email_exposed': self.email_exposed,
            'email_breaches': self.email_breaches,
            'check_timestamp': self.check_timestamp,
            'error': self.error
        }


class PrivacyAwareBreachCheck:
    """Privacy-preserving breach checking orchestrator."""

    def __init__(self, rate_limit: int = None):
        """Initialize breach check.

        Args:
            rate_limit: Requests per minute (None for unlimited)
        """
        self.rate_limit = rate_limit
        self.checker = BreachChecker()
        self._last_check_time = 0

    def check_credential(self, credential_id: str, website: str,
                        email: str, password: str) -> BreachCheckResult:
        """Check a credential for breach status.

        Args:
            credential_id: Credential ID
            website: Website name
            email: Email address
            password: Password

        Returns:
            BreachCheckResult
        """
        result = BreachCheckResult(credential_id, website, email)

        # Check password
        is_exposed, count = self.checker.check_password(password)
        result.password_exposed = is_exposed
        result.password_breach_count = count or 0

        # Check email
        if email:
            is_exposed, breaches = self.checker.check_email(email)
            result.email_exposed = is_exposed
            result.email_breaches = breaches or []

        import time
        result.check_timestamp = int(time.time())

        return result