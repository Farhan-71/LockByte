"""Vault data models."""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class CredentialCategory(str, Enum):
    """Categories for credentials."""
    PERSONAL = "personal"
    WORK = "work"
    FINANCE = "finance"
    SOCIAL = "social"
    DEVELOPMENT = "development"
    OTHER = "other"


class PasswordStrengthLevel(str, Enum):
    """Password strength levels."""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    FAIR = "fair"
    GOOD = "good"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class Credential:
    """A stored credential/password entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    website: str = ""
    username: str = ""
    email: str = ""
    password: str = ""
    url: str = ""
    category: CredentialCategory = CredentialCategory.OTHER
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    is_favorite: bool = False
    password_changed_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    has_2fa: bool = False
    totp_secret: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert enums to strings
        data['category'] = self.category.value
        # Convert datetime objects to ISO format strings
        if self.password_changed_date:
            data['password_changed_date'] = self.password_changed_date.isoformat()
        else:
            data['password_changed_date'] = None
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Credential':
        """Create from dictionary."""
        # Convert string category back to enum
        if isinstance(data.get('category'), str):
            data['category'] = CredentialCategory(data['category'])

        # Convert ISO format strings back to datetime
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at') and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('password_changed_date') and isinstance(data['password_changed_date'], str):
            data['password_changed_date'] = datetime.fromisoformat(data['password_changed_date'])

        return cls(**data)

    def update(self, **kwargs):
        """Update credential fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()


@dataclass
class SecureNote:
    """A secure note stored in the vault."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    category: str = "note"  # recovery_code, security_note, license, account_recovery, etc.
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'SecureNote':
        """Create from dictionary."""
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at') and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class VaultMetadata:
    """Metadata about the vault."""
    vault_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1
    kdf_params: Dict[str, Any] = field(default_factory=dict)
    salt: str = ""  # Hex encoded
    verification_key: str = ""  # Hex encoded
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_unlocked_at: Optional[datetime] = None
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = {
            'vault_id': self.vault_id,
            'version': self.version,
            'kdf_params': self.kdf_params,
            'salt': self.salt,
            'verification_key': self.verification_key,
            'created_at': self.created_at.isoformat(),
            'last_unlocked_at': self.last_unlocked_at.isoformat() if self.last_unlocked_at else None,
            'settings': self.settings,
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'VaultMetadata':
        """Create from dictionary."""
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_unlocked_at') and isinstance(data['last_unlocked_at'], str):
            data['last_unlocked_at'] = datetime.fromisoformat(data['last_unlocked_at'])
        return cls(**data)


@dataclass
class PasswordAnalysis:
    """Analysis results for a password."""
    password_id: str
    strength_level: PasswordStrengthLevel
    entropy: float
    length: int
    has_uppercase: bool
    has_lowercase: bool
    has_digits: bool
    has_symbols: bool
    has_repeating_chars: bool
    has_sequences: bool
    is_common: bool
    is_reused: bool
    reuse_count: int = 0
    recommendations: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'password_id': self.password_id,
            'strength_level': self.strength_level.value,
            'entropy': self.entropy,
            'length': self.length,
            'has_uppercase': self.has_uppercase,
            'has_lowercase': self.has_lowercase,
            'has_digits': self.has_digits,
            'has_symbols': self.has_symbols,
            'has_repeating_chars': self.has_repeating_chars,
            'has_sequences': self.has_sequences,
            'is_common': self.is_common,
            'is_reused': self.is_reused,
            'reuse_count': self.reuse_count,
            'recommendations': self.recommendations,
            'analyzed_at': self.analyzed_at.isoformat(),
        }


@dataclass
class SecurityAuditResult:
    """Security audit findings."""
    vault_id: str
    total_credentials: int
    weak_passwords: int
    reused_passwords: int
    exposed_credentials: int
    missing_2fa: int
    old_passwords: int
    overall_score: int  # 0-100
    audit_timestamp: datetime = field(default_factory=datetime.utcnow)
    issues: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'vault_id': self.vault_id,
            'total_credentials': self.total_credentials,
            'weak_passwords': self.weak_passwords,
            'reused_passwords': self.reused_passwords,
            'exposed_credentials': self.exposed_credentials,
            'missing_2fa': self.missing_2fa,
            'old_passwords': self.old_passwords,
            'overall_score': self.overall_score,
            'audit_timestamp': self.audit_timestamp.isoformat(),
            'issues': self.issues,
        }