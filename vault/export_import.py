"""Export and Import functionality for the vault."""

import json
import csv
from typing import List, Dict, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.repository import VaultRepository
from vault.models import Credential, SecureNote

class VaultIO:
    """Handles importing and exporting vault data."""

    def __init__(self, vault: VaultRepository):
        self.vault = vault

    def export_json(self, file_path: str) -> bool:
        """Export all vault data to a JSON file."""
        try:
            credentials = self.vault.list_credentials()
            notes = self.vault.list_secure_notes()

            data = {
                "version": "1.0",
                "credentials": [c.to_dict() for c in credentials],
                "notes": [n.to_dict() for n in notes]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"JSON Export Error: {e}")
            return False

    def import_json(self, file_path: str) -> Tuple[int, int]:
        """Import data from a JSON file. Returns (creds_imported, notes_imported)."""
        creds_imported = 0
        notes_imported = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for cred_data in data.get('credentials', []):
                self.vault.add_credential(
                    website=cred_data.get('website', ''),
                    username=cred_data.get('username', ''),
                    password=cred_data.get('password', ''),
                    email=cred_data.get('email', ''),
                    url=cred_data.get('url', ''),
                    category=cred_data.get('category', 'other'),
                    notes=cred_data.get('notes', ''),
                    totp_secret=cred_data.get('totp_secret')
                )
                creds_imported += 1

            for note_data in data.get('notes', []):
                self.vault.add_secure_note(
                    title=note_data.get('title', 'Imported Note'),
                    content=note_data.get('content', ''),
                    category=note_data.get('category', 'note')
                )
                notes_imported += 1

            return creds_imported, notes_imported
        except Exception as e:
            print(f"JSON Import Error: {e}")
            return 0, 0

    def export_csv(self, file_path: str) -> bool:
        """Export credentials to a CSV format generally compatible with Chrome/Bitwarden.
        Format: name,url,username,password,totp,notes
        """
        try:
            credentials = self.vault.list_credentials()

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Standard generic headers
                writer.writerow(['name', 'url', 'username', 'password', 'totp', 'notes'])

                for c in credentials:
                    writer.writerow([
                        c.website,
                        c.url if c.url else c.website,
                        c.username if c.username else c.email,
                        c.password,
                        c.totp_secret if c.totp_secret else '',
                        c.notes
                    ])
            return True
        except Exception as e:
            print(f"CSV Export Error: {e}")
            return False

    def import_csv(self, file_path: str) -> int:
        """Import credentials from a generic CSV format.
        Attempts to map common headers (name/url, username/login, password)
        """
        imported = 0
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Normalize headers to lowercase for flexible matching
                if not reader.fieldnames:
                    return 0
                headers = [h.lower().strip() for h in reader.fieldnames]
                reader.fieldnames = headers

                for row in reader:
                    # Try to find website/name
                    website = row.get('name') or row.get('website') or row.get('url') or 'Unknown'
                    url = row.get('url') or ''

                    # Try to find username/login/email
                    username = row.get('username') or row.get('login') or row.get('email') or ''

                    # Try to find password
                    password = row.get('password') or ''
                    if not password:
                        continue # Skip empty passwords

                    # Extra fields
                    totp = row.get('totp') or None
                    notes = row.get('notes') or row.get('extra') or ''

                    self.vault.add_credential(
                        website=website,
                        username=username,
                        password=password,
                        url=url,
                        notes=notes,
                        totp_secret=totp
                    )
                    imported += 1

            return imported
        except Exception as e:
            print(f"CSV Import Error: {e}")
            return 0