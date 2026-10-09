"""SQLite database for LockByte vault."""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import Credential, SecureNote, VaultMetadata, CredentialCategory


class VaultDatabase:
    """SQLite database for encrypted vault storage."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: Path):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize_schema()

    def _initialize_schema(self):
        """Create database schema if it doesn't exist."""
        conn = self._get_connection()

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Vault metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vault_metadata (
                vault_id TEXT PRIMARY KEY,
                version INTEGER,
                kdf_params TEXT,
                salt TEXT NOT NULL,
                verification_key TEXT NOT NULL,
                created_at TEXT,
                last_unlocked_at TEXT,
                settings TEXT,
                schema_version INTEGER DEFAULT 1
            )
        """)

        # Credentials table (encrypted)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id TEXT PRIMARY KEY,
                website TEXT,
                username TEXT,
                email TEXT,
                password_encrypted BLOB NOT NULL,
                url TEXT,
                category TEXT,
                tags TEXT,
                notes_encrypted BLOB,
                is_favorite INTEGER DEFAULT 0,
                password_changed_date TEXT,
                has_2fa INTEGER DEFAULT 0,
                totp_secret_encrypted BLOB,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Index for search
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_credentials_website
            ON credentials(website)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_credentials_category
            ON credentials(category)
        """)

        # Secure notes table (encrypted)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS secure_notes (
                id TEXT PRIMARY KEY,
                title TEXT,
                content_encrypted BLOB NOT NULL,
                category TEXT,
                tags TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Audit events table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                timestamp TEXT,
                details TEXT
            )
        """)

        # Settings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def save_vault_metadata(self, metadata: VaultMetadata):
        """Save vault metadata."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Clear any existing vault metadata to prevent stale records
        cursor.execute("DELETE FROM vault_metadata")

        cursor.execute("""
            INSERT INTO vault_metadata
            (vault_id, version, kdf_params, salt, verification_key, created_at, settings)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.vault_id,
            metadata.version,
            json.dumps(metadata.kdf_params),
            metadata.salt,
            metadata.verification_key,
            metadata.created_at.isoformat(),
            json.dumps(metadata.settings)
        ))

        conn.commit()

    def load_vault_metadata(self, vault_id: Optional[str] = None) -> Optional[VaultMetadata]:
        """Load vault metadata. If vault_id is None, loads the most recent vault."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if vault_id:
            cursor.execute("SELECT * FROM vault_metadata WHERE vault_id = ?", (vault_id,))
        else:
            cursor.execute("SELECT * FROM vault_metadata ORDER BY created_at DESC LIMIT 1")

        row = cursor.fetchone()
        if not row:
            return None

        return VaultMetadata(
            vault_id=row['vault_id'],
            version=row['version'],
            kdf_params=json.loads(row['kdf_params']) if row['kdf_params'] else {},
            salt=row['salt'],
            verification_key=row['verification_key'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            last_unlocked_at=datetime.fromisoformat(row['last_unlocked_at']) if row['last_unlocked_at'] else None,
            settings=json.loads(row['settings']) if row['settings'] else {}
        )

    def save_credential(self, credential: Credential, encrypted_password: bytes, encrypted_notes: Optional[bytes] = None, encrypted_totp_secret: Optional[bytes] = None):
        """Save credential with encrypted password.

        Args:
            credential: Credential model
            encrypted_password: Encrypted password bytes
            encrypted_notes: Encrypted notes bytes (optional)
            encrypted_totp_secret: Encrypted TOTP secret bytes (optional)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO credentials
            (id, website, username, email, password_encrypted, url, category, tags,
             notes_encrypted, is_favorite, password_changed_date, has_2fa, totp_secret_encrypted,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            credential.id,
            credential.website,
            credential.username,
            credential.email,
            encrypted_password,
            credential.url,
            credential.category.value,
            json.dumps(credential.tags),
            encrypted_notes,
            int(credential.is_favorite),
            credential.password_changed_date.isoformat() if credential.password_changed_date else None,
            int(credential.has_2fa),
            encrypted_totp_secret,
            credential.created_at.isoformat(),
            credential.updated_at.isoformat()
        ))

        conn.commit()

    def load_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Load credential (encrypted fields still encrypted)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM credentials WHERE id = ?", (credential_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return {
            'id': row['id'],
            'website': row['website'],
            'username': row['username'],
            'email': row['email'],
            'password_encrypted': row['password_encrypted'],
            'url': row['url'],
            'category': row['category'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'notes_encrypted': row['notes_encrypted'],
            'is_favorite': bool(row['is_favorite']),
            'password_changed_date': row['password_changed_date'],
            'has_2fa': bool(row['has_2fa']),
            'totp_secret_encrypted': row['totp_secret_encrypted'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }

    def list_credentials(self, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all credentials (with encrypted fields)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if search_query:
            query = "%{}%".format(search_query)
            cursor.execute("""
                SELECT * FROM credentials
                WHERE website LIKE ? OR username LIKE ? OR email LIKE ?
                ORDER BY updated_at DESC
            """, (query, query, query))
        else:
            cursor.execute("SELECT * FROM credentials ORDER BY updated_at DESC")

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_credential(self, credential_id: str):
        """Delete a credential."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM credentials WHERE id = ?", (credential_id,))
        conn.commit()

    def save_secure_note(self, note: SecureNote, encrypted_content: bytes):
        """Save secure note with encrypted content."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO secure_notes
            (id, title, content_encrypted, category, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            note.id,
            note.title,
            encrypted_content,
            note.category,
            json.dumps(note.tags),
            note.created_at.isoformat(),
            note.updated_at.isoformat()
        ))

        conn.commit()

    def load_secure_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Load secure note (content still encrypted)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM secure_notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return {
            'id': row['id'],
            'title': row['title'],
            'content_encrypted': row['content_encrypted'],
            'category': row['category'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }

    def list_secure_notes(self) -> List[Dict[str, Any]]:
        """List all secure notes."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM secure_notes ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_secure_note(self, note_id: str):
        """Delete a secure note."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM secure_notes WHERE id = ?", (note_id,))
        conn.commit()

    def log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log an audit event."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_events (event_type, timestamp, details)
            VALUES (?, ?, ?)
        """, (
            event_type,
            datetime.utcnow().isoformat(),
            json.dumps(details)
        ))

        conn.commit()

    def get_credential_count(self) -> int:
        """Get total credential count."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM credentials")
        return cursor.fetchone()['count']

    def get_note_count(self) -> int:
        """Get total secure note count."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM secure_notes")
        return cursor.fetchone()['count']