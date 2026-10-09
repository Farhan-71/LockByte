"""LockByte Backup and Import/Export module."""

import json
import os
import time
from pathlib import Path
from typing import Optional, List
from datetime import datetime

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto.encryption import encrypt_data, decrypt_data
from vault.models import Credential, SecureNote


class BackupManager:
    """Manages encrypted vault backups."""

    BACKUP_VERSION = 1
    MAGIC_HEADER = b"LOCKBYTE_BACKUP_V1"

    def __init__(self, vault_key: bytes):
        """Initialize backup manager.

        Args:
            vault_key: Current vault encryption key
        """
        self._key = vault_key

    def create_backup(self, credentials: List[Credential],
                     notes: List[SecureNote],
                     output_path: Path,
                     encrypted: bool = True) -> Path:
        """Create a vault backup.

        Args:
            credentials: List of credentials to back up
            notes: List of secure notes to back up
            output_path: Path for the backup file
            encrypted: Whether to encrypt the backup (default True)

        Returns:
            Path to created backup file
        """
        # Build backup data
        backup_data = {
            'version': self.BACKUP_VERSION,
            'created_at': datetime.utcnow().isoformat(),
            'credentials': [c.to_dict() for c in credentials],
            'secure_notes': [n.to_dict() for n in notes],
            'credential_count': len(credentials),
            'note_count': len(notes)
        }

        payload = json.dumps(backup_data, indent=2).encode('utf-8')

        if encrypted:
            # Encrypted backup
            encrypted_payload = encrypt_data(payload, self._key)
            with open(output_path, 'wb') as f:
                f.write(self.MAGIC_HEADER)
                f.write(len(encrypted_payload).to_bytes(4, 'big'))
                f.write(encrypted_payload)
        else:
            # Plaintext backup (with warning)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(backup_data, indent=2))

        return output_path

    def restore_backup(self, backup_path: Path, encrypted: bool = True) -> dict:
        """Restore from a backup file.

        Args:
            backup_path: Path to backup file
            encrypted: Whether backup is encrypted

        Returns:
            Dictionary with restored data
        """
        if encrypted:
            with open(backup_path, 'rb') as f:
                header = f.read(len(self.MAGIC_HEADER))
                if header != self.MAGIC_HEADER:
                    raise ValueError("Invalid backup file format")

                payload_len = int.from_bytes(f.read(4), 'big')
                encrypted_payload = f.read(payload_len)

            payload = decrypt_data(encrypted_payload, self._key)
            backup_data = json.loads(payload.decode('utf-8'))
        else:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.loads(f.read())

        # Validate version
        if backup_data.get('version') != self.BACKUP_VERSION:
            raise ValueError(f"Unsupported backup version: {backup_data.get('version')}")

        # Parse credentials
        credentials = [Credential.from_dict(c) for c in backup_data.get('credentials', [])]
        notes = [SecureNote.from_dict(n) for n in backup_data.get('secure_notes', [])]

        return {
            'credentials': credentials,
            'secure_notes': notes,
            'created_at': backup_data.get('created_at'),
            'credential_count': len(credentials),
            'note_count': len(notes)
        }

    @staticmethod
    def generate_backup_filename(vault_name: str = "lockbyte") -> str:
        """Generate a timestamped backup filename.

        Args:
            vault_name: Vault name prefix

        Returns:
            Backup filename string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{vault_name}_backup_{timestamp}.lbk"


class CSVExporter:
    """Export credentials to CSV format (with warnings)."""

    @staticmethod
    def export_csv(credentials: List[Credential], output_path: Path,
                   include_passwords: bool = False) -> Path:
        """Export credentials to CSV.

        WARNING: CSV exports are unencrypted.

        Args:
            credentials: List of credentials
            output_path: Output file path
            include_passwords: Whether to include passwords (DANGEROUS)

        Returns:
            Path to exported file
        """
        import csv

        fields = ['website', 'username', 'email', 'url', 'category', 'has_2fa', 'created_at']
        if include_passwords:
            fields.insert(3, 'password')

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for cred in credentials:
                row = {
                    'website': cred.website,
                    'username': cred.username,
                    'email': cred.email,
                    'url': cred.url,
                    'category': cred.category.value,
                    'has_2fa': cred.has_2fa,
                    'created_at': cred.created_at.isoformat()
                }
                if include_passwords:
                    row['password'] = cred.password
                writer.writerow(row)

        return output_path


class CSVImporter:
    """Import credentials from CSV format."""

    @staticmethod
    def import_csv(input_path: Path) -> List[dict]:
        """Import credentials from CSV.

        Args:
            input_path: Path to CSV file

        Returns:
            List of credential dictionaries
        """
        import csv

        credentials = []
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                credentials.append({
                    'website': row.get('website', row.get('name', '')),
                    'username': row.get('username', row.get('login', '')),
                    'email': row.get('email', ''),
                    'password': row.get('password', ''),
                    'url': row.get('url', row.get('login_uri', '')),
                    'category': row.get('category', 'other'),
                    'notes': row.get('notes', '')
                })

        return credentials