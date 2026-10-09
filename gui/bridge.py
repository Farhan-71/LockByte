"""Python-to-JavaScript bridge for QWebChannel in LockByte."""

import json
import sys
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Slot

# Ensure backend imports work
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.repository import VaultRepository
from security.password_generator import PasswordGenerator
from security.audit import SecurityAuditEngine
from security.breach_check import PrivacyAwareBreachCheck
from security.biometrics import BiometricAuthManager


class VaultBridge(QObject):
    """Bridge object exposed to JavaScript via QWebChannel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault_path = Path.home() / ".lockbyte" / "vault.db"
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self.vault: Optional[VaultRepository] = None

    @Slot(result=bool)
    def check_vault_exists(self) -> bool:
        """Check if the SQLite vault file exists."""
        return self.vault_path.exists()

    @Slot(str, result=str)
    def create_vault(self, master_password: str) -> str:
        """Create a new vault."""
        try:
            self.vault = VaultRepository(self.vault_path)
            metadata, _ = self.vault.create_new_vault(master_password)
            return json.dumps({"success": True, "vault_id": metadata.vault_id})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(str, result=str)
    def unlock_vault(self, master_password: str) -> str:
        """Unlock an existing vault."""
        try:
            self.vault = VaultRepository(self.vault_path)
            if self.vault.unlock(master_password):
                return json.dumps({"success": True})
            else:
                return json.dumps({"success": False, "error": "Invalid master password"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(result=str)
    def lock_vault(self) -> str:
        """Lock the vault."""
        if self.vault:
            self.vault.close()
            self.vault = None
        return json.dumps({"success": True})

    @Slot(str, result=str)
    def get_credentials(self, search_query: str = "") -> str:
        """Get all decrypted credentials."""
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})

        try:
            creds = self.vault.list_credentials(search_query if search_query else None)
            res = []
            for c in creds:
                # Format to match React UI state structure
                initial = c.website[0].upper() if c.website else "?"
                domain = c.url if c.url else (c.website.lower() + ".com" if "." not in c.website else c.website.lower())

                # Assign a background color based on name hash
                colors = ["#E2E2D2", "#C51F5D", "#7F93A8", "#9A5770", "#A9B5C0"]
                color = colors[abs(hash(c.website)) % len(colors)]

                res.append({
                    "id": c.id,
                    "website": c.website,
                    "domain": domain,
                    "username": c.username,
                    "email": c.email,
                    "password": c.password,
                    "category": c.category.value.title(),
                    "initial": initial,
                    "color": color,
                    "twoFactor": c.has_2fa,
                    "totpSecret": c.totp_secret or "",
                    "notes": c.notes,
                    "updated": c.updated_at.strftime("%Y-%m-%d %H:%M")
                })
            return json.dumps({"success": True, "data": res})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(str, result=str)
    def add_credential(self, json_data: str) -> str:
        """Add a new credential to the vault."""
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})

        try:
            data = json.loads(json_data)
            cred = self.vault.add_credential(
                website=data.get("website", ""),
                username=data.get("username", ""),
                password=data.get("password", ""),
                email=data.get("email", ""),
                url=data.get("url", ""),
                category=data.get("category", "other").lower(),
                notes=data.get("notes", ""),
                totp_secret=data.get("totpSecret") or None
            )
            return json.dumps({"success": True, "id": cred.id})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(result=str)
    def get_notes(self) -> str:
        """Get all secure notes."""
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})

        try:
            notes = self.vault.list_secure_notes()
            res = []
            for n in notes:
                res.append({
                    "id": n.id,
                    "title": n.title,
                    "category": n.category.title(),
                    "content": n.content,
                    "updated": n.updated_at.strftime("%Y-%m-%d")
                })
            return json.dumps({"success": True, "data": res})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(str, result=str)
    def add_note(self, json_data: str) -> str:
        """Add a secure note."""
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})

        try:
            data = json.loads(json_data)
            note = self.vault.add_secure_note(
                title=data.get("title", ""),
                content=data.get("content", ""),
                category=data.get("category", "note")
            )
            return json.dumps({"success": True, "id": note.id})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(int, bool, bool, bool, bool, result=str)
    def generate_password(self, length: int, upper: bool, lower: bool, digits: bool, symbols: bool) -> str:
        """Generate a password using Python CSPRNG."""
        try:
            pwd = PasswordGenerator.generate(
                length=length,
                include_uppercase=upper,
                include_lowercase=lower,
                include_digits=digits,
                include_symbols=symbols
            )
            strength = PasswordGenerator.estimate_strength(pwd)
            return json.dumps({
                "success": True,
                "password": pwd,
                "strength": strength["strength"],
                "entropy": strength["entropy"]
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(result=str)
    def run_audit(self) -> str:
        """Run security audit on current vault."""
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})

        try:
            creds = self.vault.list_credentials()

            # Breach check
            exposed = set()
            breach_checker = PrivacyAwareBreachCheck()
            for c in creds:
                try:
                    is_exposed, _ = breach_checker.checker.check_password(c.password)
                    if is_exposed:
                        exposed.add(c.id)
                except Exception:
                    pass

            engine = SecurityAuditEngine()
            result = engine.audit_credentials(creds, exposed)
            actions = engine.get_priority_actions(result)

            return json.dumps({
                "success": True,
                "score": result.overall_score,
                "weakCount": result.weak_passwords,
                "reusedCount": result.reused_passwords,
                "missing2FA": result.missing_2fa,
                "exposedCount": result.exposed_credentials,
                "actions": actions
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(result=str)
    def get_settings(self) -> str:
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})
        try:
            return json.dumps({"success": True, "data": self.vault.get_settings()})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(str, result=str)
    def update_settings(self, json_data: str) -> str:
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})
        try:
            settings = json.loads(json_data)
            self.vault.update_settings(settings)
            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(str, str, result=str)
    def change_master_password(self, old_pw: str, new_pw: str) -> str:
        if not self.vault or not self.vault.is_unlocked():
            return json.dumps({"success": False, "error": "Vault is locked"})
        try:
            if self.vault.change_master_password(old_pw, new_pw):
                # Update DPAPI biometric key if biometric is enabled
                bio = BiometricAuthManager()
                if bio.key_file.exists():
                    bio.store_master_password(new_pw)
                return json.dumps({"success": True})
            else:
                return json.dumps({"success": False, "error": "Incorrect current master password"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(result=str)
    def check_biometrics_available(self) -> str:
        """Check if Windows Hello biometrics is available."""
        try:
            available = BiometricAuthManager.is_available()
            return json.dumps({"success": True, "available": available})
        except Exception as e:
            return json.dumps({"success": False, "available": False, "error": str(e)})

    @Slot(result=str)
    def has_stored_biometric_key(self) -> str:
        """Check if DPAPI protected biometric key file exists."""
        try:
            bio = BiometricAuthManager()
            return json.dumps({"success": True, "hasKey": bio.key_file.exists()})
        except Exception as e:
            return json.dumps({"success": False, "hasKey": False, "error": str(e)})

    @Slot(result=str)
    def authenticate_biometrics(self) -> str:
        """Trigger Windows Hello prompt and unlock vault if verified."""
        try:
            bio = BiometricAuthManager()
            if not bio.key_file.exists():
                return json.dumps({"success": False, "verified": False, "error": "Biometrics not configured"})

            verified = bio.verify_user("Unlock LockByte Vault")
            if not verified:
                return json.dumps({"success": True, "verified": False, "error": "Windows Hello verification failed or canceled"})

            # Retrieve master password from DPAPI
            master_pw = bio.retrieve_master_password()
            if not master_pw:
                return json.dumps({"success": False, "verified": False, "error": "Failed to retrieve biometric key"})

            # Unlock vault
            self.vault = VaultRepository(self.vault_path)
            if self.vault.unlock(master_pw):
                return json.dumps({"success": True, "verified": True})
            else:
                return json.dumps({"success": False, "verified": False, "error": "Failed to unlock vault with biometric key"})
        except Exception as e:
            return json.dumps({"success": False, "verified": False, "error": str(e)})

    @Slot(str, result=str)
    def enable_biometrics(self, master_password: str) -> str:
        """Verify user with Windows Hello and save DPAPI protected key."""
        try:
            if not self.vault or not self.vault.is_unlocked():
                return json.dumps({"success": False, "error": "Vault is locked"})

            # Validate password against current vault metadata
            metadata = self.vault._get_metadata()
            if metadata:
                old_salt = bytes.fromhex(metadata.salt)
                old_verify = bytes.fromhex(metadata.verification_key)
                if not self.vault.key_manager.unlock(master_password, old_salt, old_verify):
                    return json.dumps({"success": False, "error": "Incorrect master password"})

            bio = BiometricAuthManager()
            if not bio.is_available():
                return json.dumps({"success": False, "error": "Windows Hello is not available on this device"})

            verified = bio.verify_user("Verify identity to enable Biometric Unlock")
            if not verified:
                return json.dumps({"success": False, "error": "Windows Hello verification failed or canceled"})

            if bio.store_master_password(master_password):
                return json.dumps({"success": True})
            else:
                return json.dumps({"success": False, "error": "Failed to store biometric key"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @Slot(result=str)
    def disable_biometrics(self) -> str:
        """Remove DPAPI biometric key file."""
        try:
            bio = BiometricAuthManager()
            bio.clear_stored_key()
            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
