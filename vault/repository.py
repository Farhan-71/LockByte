"""Vault repository - high-level interface for vault operations."""

import sys
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vault.models import Credential, SecureNote, VaultMetadata, CredentialCategory
from vault.database import VaultDatabase
from crypto.key_management import KeyManager, VaultKey


class VaultRepository:
    """High-level repository for vault operations."""

    def __init__(self, db_path: Path):
        """Initialize vault repository.

        Args:
            db_path: Path to SQLite database
        """
        self.db = VaultDatabase(db_path)
        self.key_manager = KeyManager(db_path)
        self._vault_metadata: Optional[VaultMetadata] = None

    def create_new_vault(self, master_password: str, vault_id: str = None) -> Tuple[VaultMetadata, VaultKey]:
        """Create a new vault with master password.

        Args:
            master_password: Master password for vault
            vault_id: Custom vault ID (generated if None)

        Returns:
            Tuple of (metadata, vault_key)
        """
        # Create key
        key, salt, params = self.key_manager.create_vault(master_password)

        # Create verification key
        verify_key, _, _ = self.key_manager.create_vault(master_password + "_verify")

        # Create metadata
        metadata = VaultMetadata(
            vault_id=vault_id or f"vault_{datetime.utcnow().timestamp()}",
            version=1,
            kdf_params=params,
            salt=salt.hex(),
            verification_key=key.hex()
        )

        # Save metadata
        self.db.save_vault_metadata(metadata)
        self._vault_metadata = metadata

        return metadata, self.key_manager.current_key

    def unlock(self, master_password: str) -> bool:
        """Unlock vault with master password.

        Args:
            master_password: Master password

        Returns:
            True if successful
        """
        # Load metadata
        metadata = self._get_metadata()
        if not metadata:
            return False

        # Unlock with key manager
        salt = bytes.fromhex(metadata.salt)
        verify_key = bytes.fromhex(metadata.verification_key)

        return self.key_manager.unlock(master_password, salt, verify_key)

    def lock(self):
        """Lock the vault."""
        self.key_manager.lock()

    def is_unlocked(self) -> bool:
        """Check if vault is unlocked."""
        return self.key_manager.is_unlocked

    def _get_metadata(self) -> Optional[VaultMetadata]:
        """Get or load vault metadata."""
        if self._vault_metadata:
            return self._vault_metadata

        # Try to load from database
        # Since we currently only support a single vault per DB, we pass None
        # to fetch the first available vault metadata regardless of ID.
        metadata = self.db.load_vault_metadata()
        if metadata:
            self._vault_metadata = metadata
        return metadata

    def _require_unlocked(self):
        """Check that vault is unlocked."""
        if not self.is_unlocked():
            raise ValueError("Vault is locked")

    def get_settings(self) -> dict:
        """Get user settings."""
        self._require_unlocked()
        metadata = self._get_metadata()
        if metadata and metadata.settings:
            return metadata.settings
        return {}

    def update_settings(self, settings: dict):
        """Update user settings."""
        self._require_unlocked()
        metadata = self._get_metadata()
        if metadata:
            metadata.settings = settings
            self.db.save_vault_metadata(metadata)

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """Change the master password and re-encrypt the entire vault."""
        self._require_unlocked()
        metadata = self._get_metadata()
        if not metadata:
            return False

        old_salt = bytes.fromhex(metadata.salt)
        old_verify_key = bytes.fromhex(metadata.verification_key)

        # Load all plaintext data into memory using current key
        credentials = self.list_credentials()
        notes = self.list_secure_notes()

        # Change key (validates old password)
        result = self.key_manager.change_password(old_password, new_password, old_salt, old_verify_key)
        if not result:
            return False

        new_verify_key, new_salt, new_params = result

        # Update metadata
        metadata.salt = new_salt.hex()
        metadata.verification_key = new_verify_key.hex()
        metadata.kdf_params = new_params

        # Save new metadata
        self.db.save_vault_metadata(metadata)

        # Re-encrypt and save all credentials
        for cred in credentials:
            key = self.key_manager.current_key
            encrypted_password = key.encrypt(cred.password.encode('utf-8'))
            encrypted_notes = key.encrypt(cred.notes.encode('utf-8')) if cred.notes else None
            encrypted_totp = key.encrypt(cred.totp_secret.encode('utf-8')) if cred.totp_secret else None
            self.db.save_credential(cred, encrypted_password, encrypted_notes, encrypted_totp)

        # Re-encrypt and save all secure notes
        for note in notes:
            key = self.key_manager.current_key
            encrypted_content = key.encrypt(note.content.encode('utf-8'))
            self.db.save_secure_note(note, encrypted_content)

        return True

    def add_credential(self, website: str, username: str, password: str,
                      email: str = "", url: str = "", category: str = "other",
                      notes: str = "", totp_secret: str = None) -> Credential:
        """Add a new credential to the vault.

        Args:
            website: Website/service name
            username: Username
            password: Password
            email: Email address
            url: URL
            category: Category
            notes: Notes
            totp_secret: Base32 TOTP Secret

        Returns:
            Created credential
        """
        self._require_unlocked()

        # Create credential
        credential = Credential(
            website=website,
            username=username,
            password=password,
            email=email,
            url=url,
            category=CredentialCategory(category),
            notes=notes,
            has_2fa=bool(totp_secret),
            totp_secret=totp_secret
        )

        # Encrypt data
        key = self.key_manager.current_key
        encrypted_password = key.encrypt(password.encode('utf-8'))
        encrypted_notes = key.encrypt(notes.encode('utf-8')) if notes else None
        encrypted_totp = key.encrypt(totp_secret.encode('utf-8')) if totp_secret else None

        # Save to database
        self.db.save_credential(credential, encrypted_password, encrypted_notes, encrypted_totp)

        # Log audit event
        self.db.log_audit_event('credential_created', {
            'credential_id': credential.id,
            'website': website,
            'has_2fa': bool(totp_secret)
        })

        return credential

    def get_credential(self, credential_id: str) -> Optional[Credential]:
        """Get and decrypt a credential.

        Args:
            credential_id: Credential ID

        Returns:
            Decrypted credential or None
        """
        self._require_unlocked()

        # Load from database
        data = self.db.load_credential(credential_id)
        if not data:
            return None

        # Decrypt
        key = self.key_manager.current_key
        password = key.decrypt(data['password_encrypted']).decode('utf-8')
        notes = ""
        if data['notes_encrypted']:
            notes = key.decrypt(data['notes_encrypted']).decode('utf-8')
        totp_secret = None
        if data.get('totp_secret_encrypted'):
            totp_secret = key.decrypt(data['totp_secret_encrypted']).decode('utf-8')

        # Build credential
        credential = Credential(
            id=data['id'],
            website=data['website'],
            username=data['username'],
            email=data['email'],
            password=password,
            url=data['url'],
            category=CredentialCategory(data['category']),
            tags=data['tags'],
            notes=notes,
            is_favorite=data['is_favorite'],
            password_changed_date=data['password_changed_date'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            has_2fa=data['has_2fa'],
            totp_secret=totp_secret
        )

        return credential

    def list_credentials(self, search_query: str = None) -> List[Credential]:
        """List credentials (decrypts passwords).

        Args:
            search_query: Optional search query

        Returns:
            List of decrypted credentials
        """
        self._require_unlocked()

        # Load from database
        data_list = self.db.list_credentials(search_query)
        credentials = []

        key = self.key_manager.current_key
        for data in data_list:
            try:
                password = key.decrypt(data['password_encrypted']).decode('utf-8')
                notes = ""
                if data['notes_encrypted']:
                    notes = key.decrypt(data['notes_encrypted']).decode('utf-8')
                totp_secret = None
                if data.get('totp_secret_encrypted'):
                    totp_secret = key.decrypt(data['totp_secret_encrypted']).decode('utf-8')

                credential = Credential(
                    id=data['id'],
                    website=data['website'],
                    username=data['username'],
                    email=data['email'],
                    password=password,
                    url=data['url'],
                    category=CredentialCategory(data['category']),
                    tags=data['tags'],
                    notes=notes,
                    is_favorite=data['is_favorite'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    has_2fa=data['has_2fa'],
                    totp_secret=totp_secret
                )
                credentials.append(credential)
            except Exception as e:
                print(f"Error decrypting credential {data['id']}: {e}")
                continue

        return credentials

    def add_totp_to_credential(self, credential_id: str, totp_secret: str) -> Optional[Credential]:
        """Attach a 2FA TOTP secret to an existing credential.

        Args:
            credential_id: The ID of the credential
            totp_secret: The base32 TOTP secret

        Returns:
            Updated Credential or None if not found
        """
        self._require_unlocked()

        credential = self.get_credential(credential_id)
        if not credential:
            return None

        # Update credential model
        credential.has_2fa = True
        credential.totp_secret = totp_secret

        # Re-encrypt data
        key = self.key_manager.current_key
        encrypted_password = key.encrypt(credential.password.encode('utf-8'))
        encrypted_notes = key.encrypt(credential.notes.encode('utf-8')) if credential.notes else None
        encrypted_totp = key.encrypt(totp_secret.encode('utf-8'))

        # Save to database
        self.db.save_credential(credential, encrypted_password, encrypted_notes, encrypted_totp)

        self.db.log_audit_event('totp_added', {
            'credential_id': credential.id,
            'website': credential.website
        })

        return credential

    def delete_credential(self, credential_id: str):
        """Delete a credential.

        Args:
            credential_id: Credential ID
        """
        self._require_unlocked()

        self.db.delete_credential(credential_id)

        # Log audit event
        self.db.log_audit_event('credential_deleted', {
            'credential_id': credential_id
        })

    def add_secure_note(self, title: str, content: str, category: str = "note") -> SecureNote:
        """Add a secure note.

        Args:
            title: Note title
            content: Note content
            category: Note category

        Returns:
            Created note
        """
        self._require_unlocked()

        note = SecureNote(
            title=title,
            content=content,
            category=category
        )

        # Encrypt content
        key = self.key_manager.current_key
        encrypted_content = key.encrypt(content.encode('utf-8'))

        # Save to database
        self.db.save_secure_note(note, encrypted_content)

        # Log audit event
        self.db.log_audit_event('note_created', {
            'note_id': note.id,
            'title': title
        })

        return note

    def get_secure_note(self, note_id: str) -> Optional[SecureNote]:
        """Get and decrypt a secure note.

        Args:
            note_id: Note ID

        Returns:
            Decrypted note or None
        """
        self._require_unlocked()

        data = self.db.load_secure_note(note_id)
        if not data:
            return None

        # Decrypt
        key = self.key_manager.current_key
        content = key.decrypt(data['content_encrypted']).decode('utf-8')

        note = SecureNote(
            id=data['id'],
            title=data['title'],
            content=content,
            category=data['category'],
            tags=data['tags'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

        return note

    def list_secure_notes(self) -> List[SecureNote]:
        """List all secure notes (decrypts content).

        Returns:
            List of decrypted notes
        """
        self._require_unlocked()

        data_list = self.db.list_secure_notes()
        notes = []

        key = self.key_manager.current_key
        for data in data_list:
            try:
                content = key.decrypt(data['content_encrypted']).decode('utf-8')
                note = SecureNote(
                    id=data['id'],
                    title=data['title'],
                    content=content,
                    category=data['category'],
                    tags=data['tags'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at'])
                )
                notes.append(note)
            except Exception as e:
                print(f"Error decrypting note {data['id']}: {e}")
                continue

        return notes

    def delete_secure_note(self, note_id: str):
        """Delete a secure note."""
        self._require_unlocked()
        self.db.delete_secure_note(note_id)

    def get_vault_stats(self) -> dict:
        """Get vault statistics."""
        return {
            'total_credentials': self.db.get_credential_count(),
            'total_notes': self.db.get_note_count()
        }

    def close(self):
        """Close vault and database."""
        self.lock()
        self.db.close()