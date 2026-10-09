"""LockByte main application."""

import sys
import io
from pathlib import Path
from typing import Optional
import json
import stdiomask

# Set UTF-8 output for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vault import VaultRepository
from security import (
    PasswordGenerator, PasswordStrengthAnalyzer,
    SecurityAuditEngine, TOTPGenerator, PrivacyAwareBreachCheck
)


class LockByteApp:
    """Main LockByte application controller."""

    def __init__(self, vault_path: Path = None):
        """Initialize application."""
        if vault_path is None:
            vault_path = Path.home() / ".lockbyte" / "vault.db"

        vault_path.parent.mkdir(parents=True, exist_ok=True)
        self.vault_path = vault_path
        self.vault: Optional[VaultRepository] = None
        self.audit_engine = SecurityAuditEngine()
        self.breach_checker = PrivacyAwareBreachCheck()

    def initialize_vault(self, master_password: str):
        """Initialize a new vault."""
        self.vault = VaultRepository(self.vault_path)
        metadata, key = self.vault.create_new_vault(master_password)
        print(f"[*] Vault created with ID: {metadata.vault_id}")

    def open_vault(self, master_password: str) -> bool:
        """Open existing vault."""
        if not self.vault_path.exists():
            print("[X] Vault not found. Please initialize first.")
            return False

        self.vault = VaultRepository(self.vault_path)

        if self.vault.unlock(master_password):
            print("[*] Vault unlocked")
            return True
        else:
            print("[X] Invalid password")
            return False

    def add_credential(self, website: str, username: str, password: str,
                      email: str = "", url: str = "", category: str = "other"):
        """Add a credential to the vault."""
        if not self.vault or not self.vault.is_unlocked():
            print("[X] Vault not unlocked")
            return

        credential = self.vault.add_credential(
            website=website,
            username=username,
            password=password,
            email=email,
            url=url,
            category=category
        )

        analysis = PasswordStrengthAnalyzer.analyze(password)
        print(f"[*] Credential added: {website}")
        print(f"    Password strength: {analysis.strength_level.value}")
        if analysis.recommendations:
            print(f"    Tips: {', '.join(analysis.recommendations[:2])}")

    def list_credentials(self, search: str = None):
        """List credentials in vault."""
        if not self.vault or not self.vault.is_unlocked():
            print("[X] Vault not unlocked")
            return

        credentials = self.vault.list_credentials(search)

        if not credentials:
            print("No credentials found")
            return

        print(f"\n{'Website':<20} {'Username':<20} {'Strength':<12}")
        print("-" * 52)

        for cred in credentials:
            analysis = PasswordStrengthAnalyzer.analyze(cred.password)
            print(f"{cred.website:<20} {cred.username:<20} {analysis.strength_level.value:<12}")

    def generate_password(self, length: int = 16):
        """Generate a secure password."""
        password = PasswordGenerator.generate(
            length=length,
            min_uppercase=1,
            min_lowercase=1,
            min_digits=1,
            min_symbols=1
        )
        strength = PasswordGenerator.estimate_strength(password)

        print(f"Generated: {password}")
        print(f"Strength: {strength['strength']}")
        print(f"Entropy: {strength['entropy']:.1f} bits")

    def generate_passphrase(self, word_count: int = 4):
        """Generate a memorable passphrase."""
        passphrase = PasswordGenerator.generate_passphrase(
            word_count=word_count,
            capitalize=True,
            include_number=True
        )
        print(f"Generated: {passphrase}")

    def run_security_audit(self):
        """Run a security audit of the vault."""
        if not self.vault or not self.vault.is_unlocked():
            print("[X] Vault not unlocked")
            return

        credentials = self.vault.list_credentials()
        if not credentials:
            print("No credentials to audit")
            return

        print("\n[*] Running security audit...")

        result = self.audit_engine.audit_credentials(credentials)

        print(f"\n+======================================+")
        print(f"|  LOCKBYTE SECURITY CENTER          |")
        print(f"|  Overall Security Score: {result.overall_score}/100")
        print(f"+======================================+")
        print(f"\nCredentials: {result.total_credentials}")
        print(f"Weak passwords: {result.weak_passwords}")
        print(f"Reused passwords: {result.reused_passwords}")
        print(f"Exposed credentials: {result.exposed_credentials}")
        print(f"Missing 2FA: {result.missing_2fa}")
        print(f"Old passwords: {result.old_passwords}")

        actions = self.audit_engine.get_priority_actions(result)
        if actions:
            print(f"\n[!] Priority Actions:")
            for i, action in enumerate(actions[:5], 1):
                print(f"  {i}. [{action['priority'].upper()}] {action['action']}")
                print(f"     Reason: {action['reason']}")

    def check_password_breach(self, password: str):
        """Check if a password has been exposed."""
        print("Checking password against known breaches...")
        is_exposed, count = PrivacyAwareBreachCheck().checker.check_password(password)

        if is_exposed:
            print(f"[!] WARNING: This password appears in {count} known breaches!")
            print("   Consider using a different password.")
        else:
            print("[*] Password not found in known breaches")

    def setup_totp(self, website_search: str, secret: str):
        """Setup 2FA for an existing credential."""
        if not self.vault or not self.vault.is_unlocked():
            print("[X] Vault not unlocked")
            return

        credentials = self.vault.list_credentials(website_search)
        if not credentials:
            print(f"[X] No credentials found matching '{website_search}'")
            return

        # Automatically select the first match for simplicity
        target_cred = credentials[0]
        self.vault.add_totp_to_credential(target_cred.id, secret)
        print(f"[*] 2FA setup successfully for {target_cred.website} ({target_cred.username})")

    def get_totp_code(self, website_search: str):
        """Generate current 2FA code for a credential."""
        if not self.vault or not self.vault.is_unlocked():
            print("[X] Vault not unlocked")
            return

        credentials = self.vault.list_credentials(website_search)

        # Filter only those with 2FA
        totp_creds = [c for c in credentials if c.has_2fa and c.totp_secret]

        if not totp_creds:
            print(f"[X] No 2FA-enabled credentials found matching '{website_search}'")
            return

        target_cred = totp_creds[0]
        generator = TOTPGenerator()
        code = generator.generate(target_cred.totp_secret)

        print(f"[*] {target_cred.website} 2FA Code: {code}")
        print(f"    (Valid for next {generator.get_remaining_time()} seconds)")

    def add_secure_note(self, title: str, content: str, category: str = "note"):
        """Add a secure note to the vault."""
        if not self.vault or not self.vault.is_unlocked():
            print("[X] Vault not unlocked")
            return

        note = self.vault.add_secure_note(title=title, content=content, category=category)
        print(f"[*] Secure note added: '{note.title}'")

    def list_secure_notes(self):
        """List and optionally read secure notes."""
        if not self.vault or not self.vault.is_unlocked():
            print("[X] Vault not unlocked")
            return

        notes = self.vault.list_secure_notes()

        if not notes:
            print("No secure notes found")
            return

        print(f"\n{'ID':<5} {'Title':<25} {'Category':<15} {'Last Updated':<20}")
        print("-" * 68)

        for i, note in enumerate(notes, 1):
            date_str = note.updated_at.strftime("%Y-%m-%d %H:%M")
            print(f"{i:<5} {note.title:<25} {note.category:<15} {date_str:<20}")

        print("\nSelect a note ID to read its contents (or press Enter to return):")
        choice = input("> ").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(notes):
                target_note = notes[idx]
                print(f"\n======================================")
                print(f"TITLE: {target_note.title}")
                print(f"CATEGORY: {target_note.category}")
                print(f"DATE: {target_note.updated_at}")
                print(f"--------------------------------------")
                print(f"{target_note.content}")
                print(f"======================================\n")
            else:
                print("[X] Invalid note ID")


    def close_vault(self):
        """Close and lock the vault."""
        if self.vault:
            self.vault.close()
            print("[*] Vault locked")

    def display_menu(self):
        """Display main menu."""
        print("\n+======================================+")
        print("|        LOCKBYTE v1.0                |")
        print("|  Secure Password Manager            |")
        print("+======================================+")
        print("\n1. Add credential")
        print("2. List credentials")
        print("3. Generate password")
        print("4. Generate passphrase")
        print("5. Run security audit")
        print("6. Check password breach")
        print("7. Setup 2FA for credential")
        print("8. Get 2FA code")
        print("9. Add Secure Note")
        print("10. List/Read Secure Notes")
        print("11. Lock vault")
        print("12. Exit")
        print()


def main():
    """Main entry point."""
    app = LockByteApp()

    print("+======================================+")
    print("|        LOCKBYTE SETUP               |")
    print("|  Secure Password Manager            |")
    print("+======================================+\n")

    if app.vault_path.exists():
        print(f"Vault found at: {app.vault_path}")
        master_password = stdiomask.getpass("Enter master password: ", mask="*")
        if not app.open_vault(master_password):
            return
    else:
        print("No vault found. Creating new vault...\n")
        while True:
            password1 = stdiomask.getpass("Set master password: ", mask="*")
            password2 = stdiomask.getpass("Confirm password: ", mask="*")
            if password1 == password2:
                if len(password1) >= 8:
                    app.initialize_vault(password1)
                    break
                else:
                    print("[X] Password must be at least 8 characters")
            else:
                print("[X] Passwords don't match")

    while True:
        app.display_menu()
        choice = input("Select option (1-12): ").strip()

        if choice == "1":
            website = input("Website: ").strip()
            username = input("Username: ").strip()
            password = stdiomask.getpass("Password: ", mask="*")
            email = input("Email (optional): ").strip()
            app.add_credential(website, username, password, email)

        elif choice == "2":
            search = input("Search (optional): ").strip()
            app.list_credentials(search if search else None)

        elif choice == "3":
            length = input("Password length (default 16): ").strip()
            length = int(length) if length else 16
            app.generate_password(length)

        elif choice == "4":
            app.generate_passphrase()

        elif choice == "5":
            app.run_security_audit()

        elif choice == "6":
            password = stdiomask.getpass("Enter password to check: ", mask="*")
            app.check_password_breach(password)

        elif choice == "7":
            website = input("Enter website name to setup 2FA: ").strip()
            secret = input("Enter Base32 TOTP Secret: ").strip()
            # Basic validation to strip spaces/hyphens users might copy-paste
            secret = secret.replace(" ", "").replace("-", "")
            if website and secret:
                app.setup_totp(website, secret)

        elif choice == "8":
            website = input("Enter website name for 2FA code: ").strip()
            if website:
                app.get_totp_code(website)

        elif choice == "9":
            title = input("Note Title: ").strip()
            category = input("Category (default 'note'): ").strip()
            if not category:
                category = "note"
            print("Note Content (type 'END' on a new line to finish):")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            content = "\n".join(lines)
            if title and content:
                app.add_secure_note(title, content, category)

        elif choice == "10":
            app.list_secure_notes()

        elif choice == "11":
            app.close_vault()
            print("Vault locked. Exiting...")
            break

        elif choice == "12":
            app.close_vault()
            print("Goodbye!")
            break

        else:
            print("[X] Invalid option")


if __name__ == "__main__":
    main()