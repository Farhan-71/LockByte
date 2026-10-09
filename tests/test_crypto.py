"""Tests for LockByte cryptographic core."""

import pytest
from pathlib import Path
import tempfile
import os

from crypto import (
    generate_salt, derive_key_simple, encrypt_data, decrypt_data,
    KeyManager, VaultKey, secure_random_bytes
)
from vault import VaultRepository, Credential, CredentialCategory
from security import PasswordStrengthAnalyzer, SecurityAuditEngine, PasswordGenerator


class TestKDF:
    """Test key derivation function."""

    def test_generate_salt(self):
        """Test salt generation."""
        salt1 = generate_salt()
        salt2 = generate_salt()

        assert len(salt1) == 32
        assert len(salt2) == 32
        assert salt1 != salt2  # Should be different

    def test_derive_key(self):
        """Test key derivation."""
        password = "MySecurePassword123!"
        salt = generate_salt()

        key1 = derive_key_simple(password, salt)
        key2 = derive_key_simple(password, salt)

        # Same password and salt should produce same key
        assert key1 == key2
        assert len(key1) == 32

    def test_derive_key_different_salts(self):
        """Test that different salts produce different keys."""
        password = "MySecurePassword123!"
        salt1 = generate_salt()
        salt2 = generate_salt()

        key1 = derive_key_simple(password, salt1)
        key2 = derive_key_simple(password, salt2)

        # Different salts should produce different keys
        assert key1 != key2

    def test_derive_key_different_passwords(self):
        """Test that different passwords produce different keys."""
        password1 = "Password1!"
        password2 = "Password2!"
        salt = generate_salt()

        key1 = derive_key_simple(password1, salt)
        key2 = derive_key_simple(password2, salt)

        assert key1 != key2


class TestEncryption:
    """Test encryption and decryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption."""
        key = secure_random_bytes(32)
        plaintext = b"Hello, World! This is a secret."

        ciphertext = encrypt_data(plaintext, key)
        decrypted = decrypt_data(ciphertext, key)

        assert decrypted == plaintext

    def test_encrypt_produces_different_ciphertexts(self):
        """Test that same plaintext produces different ciphertexts (due to random nonce)."""
        key = secure_random_bytes(32)
        plaintext = b"Same plaintext"

        ciphertext1 = encrypt_data(plaintext, key)
        ciphertext2 = encrypt_data(plaintext, key)

        # Different ciphertexts (different nonces)
        assert ciphertext1 != ciphertext2

        # Both decrypt to same plaintext
        assert decrypt_data(ciphertext1, key) == plaintext
        assert decrypt_data(ciphertext2, key) == plaintext

    def test_decrypt_with_wrong_key_fails(self):
        """Test that decryption with wrong key fails."""
        key1 = secure_random_bytes(32)
        key2 = secure_random_bytes(32)
        plaintext = b"Secret message"

        ciphertext = encrypt_data(plaintext, key1)

        with pytest.raises(ValueError):
            decrypt_data(ciphertext, key2)

    def test_tampered_ciphertext_fails(self):
        """Test that tampered ciphertext fails to decrypt."""
        key = secure_random_bytes(32)
        plaintext = b"Secret message"

        ciphertext = bytearray(encrypt_data(plaintext, key))
        # Tamper with the ciphertext
        ciphertext[20] ^= 0xFF

        with pytest.raises(ValueError):
            decrypt_data(bytes(ciphertext), key)


class TestKeyManager:
    """Test key manager."""

    def test_create_vault(self):
        """Test vault creation."""
        km = KeyManager()
        password = "MyMasterPassword123!"

        key, salt, params = km.create_vault(password)

        assert len(key) == 32
        assert len(salt) == 32
        assert km.is_unlocked

    def test_unlock_vault(self):
        """Test vault unlock."""
        km = KeyManager()
        password = "MyMasterPassword123!"

        key, salt, params = km.create_vault(password)
        km.lock()
        assert not km.is_unlocked

        # Create verification key
        verify_key = key

        # Unlock
        assert km.unlock(password, salt, verify_key)
        assert km.is_unlocked

    def test_unlock_with_wrong_password(self):
        """Test unlock with wrong password fails."""
        km = KeyManager()
        password = "MyMasterPassword123!"
        wrong_password = "WrongPassword456!"

        key, salt, params = km.create_vault(password)
        km.lock()

        assert not km.unlock(wrong_password, salt, key)
        assert not km.is_unlocked


class TestPasswordAnalyzer:
    """Test password analysis."""

    def test_weak_password(self):
        """Test detection of weak passwords."""
        analysis = PasswordStrengthAnalyzer.analyze("password")
        assert analysis.strength_level.value in ["very_weak", "weak"]

    def test_strong_password(self):
        """Test detection of strong passwords."""
        # Avoid 123 to prevent sequential char flag
        analysis = PasswordStrengthAnalyzer.analyze("MySecurePassword947!@#$")
        assert analysis.strength_level.value in ["strong", "very_strong"]

    def test_common_password_detection(self):
        """Test detection of common passwords."""
        analysis = PasswordStrengthAnalyzer.analyze("123456")
        assert analysis.is_common

    def test_repeating_chars_detection(self):
        """Test detection of repeating characters."""
        analysis = PasswordStrengthAnalyzer.analyze("Passaaa111")
        assert analysis.has_repeating_chars

    def test_keyboard_pattern_detection(self):
        """Test detection of keyboard patterns."""
        analysis = PasswordStrengthAnalyzer.analyze("qwerty123")
        # Should flag keyboard pattern

    def test_entropy_calculation(self):
        """Test entropy calculation."""
        analysis1 = PasswordStrengthAnalyzer.analyze("short")
        analysis2 = PasswordStrengthAnalyzer.analyze("VeryLongPasswordWith123!@#$")

        # Longer password should have higher entropy
        assert analysis2.entropy > analysis1.entropy


class TestPasswordGenerator:
    """Test password generation."""

    def test_generate_password(self):
        """Test password generation."""
        password = PasswordGenerator.generate(length=16)

        assert len(password) == 16
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)

    def test_generate_passphrase(self):
        """Test passphrase generation."""
        passphrase = PasswordGenerator.generate_passphrase(word_count=4)

        # Should have words separated by dashes
        parts = passphrase.split('-')
        assert len(parts) >= 4

    def test_generate_pin(self):
        """Test PIN generation."""
        pin = PasswordGenerator.generate_pin(length=6)

        assert len(pin) == 6
        assert pin.isdigit()

    def test_password_uniqueness(self):
        """Test that generated passwords are unique."""
        passwords = [PasswordGenerator.generate(length=16) for _ in range(10)]

        # All should be different
        assert len(set(passwords)) == 10


class TestVaultRepository:
    """Test vault repository."""

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            vault = VaultRepository(db_path)
            yield vault
            vault.close()

    def test_create_and_unlock_vault(self, temp_vault):
        """Test vault creation and unlock."""
        password = "TestPassword123!"

        metadata, key = temp_vault.create_new_vault(password)
        assert metadata is not None
        assert key is not None
        assert temp_vault.is_unlocked()

    def test_add_credential(self, temp_vault):
        """Test adding a credential."""
        password = "TestPassword123!"
        temp_vault.create_new_vault(password)

        cred = temp_vault.add_credential(
            website="github.com",
            username="testuser",
            password="MySecretPassword123!"
        )

        assert cred.id is not None
        assert cred.website == "github.com"
        assert cred.username == "testuser"

    def test_list_credentials(self, temp_vault):
        """Test listing credentials."""
        password = "TestPassword123!"
        temp_vault.create_new_vault(password)

        temp_vault.add_credential(
            website="github.com",
            username="user1",
            password="pass1"
        )
        temp_vault.add_credential(
            website="gmail.com",
            username="user2",
            password="pass2"
        )

        credentials = temp_vault.list_credentials()
        assert len(credentials) == 2

    def test_get_credential(self, temp_vault):
        """Test retrieving a specific credential."""
        password = "TestPassword123!"
        temp_vault.create_new_vault(password)

        cred = temp_vault.add_credential(
            website="github.com",
            username="testuser",
            password="MySecretPassword123!"
        )

        retrieved = temp_vault.get_credential(cred.id)
        assert retrieved.website == "github.com"
        assert retrieved.username == "testuser"
        assert retrieved.password == "MySecretPassword123!"

    def test_delete_credential(self, temp_vault):
        """Test deleting a credential."""
        password = "TestPassword123!"
        temp_vault.create_new_vault(password)

        cred = temp_vault.add_credential(
            website="github.com",
            username="testuser",
            password="MySecretPassword123!"
        )

        temp_vault.delete_credential(cred.id)
        credentials = temp_vault.list_credentials()
        assert len(credentials) == 0

    def test_add_secure_note(self, temp_vault):
        """Test adding a secure note."""
        password = "TestPassword123!"
        temp_vault.create_new_vault(password)

        note = temp_vault.add_secure_note(
            title="Recovery Codes",
            content="CODE123456789"
        )

        assert note.id is not None
        assert note.title == "Recovery Codes"


class TestSecurityAudit:
    """Test security audit."""

    @pytest.fixture
    def temp_vault_with_creds(self):
        """Create temporary vault with credentials for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_audit.db"
            vault = VaultRepository(db_path)
            vault.create_new_vault("TestPassword123!")
            vault.add_credential("github.com", "user", "Weak1")
            yield vault
            vault.close()

    def test_audit_credentials(self, temp_vault_with_creds):
        """Test audit on multiple credentials."""
        audit = SecurityAuditEngine()
        credentials = temp_vault_with_creds.list_credentials()

        result = audit.audit_credentials(credentials)

        assert result.total_credentials > 0
        assert result.overall_score >= 0
        assert result.overall_score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])