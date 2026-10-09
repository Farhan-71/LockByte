# LockByte Project Rules & AI Governance

These rules strictly govern all code generated and modified in this repository.

## 1. Coding Standards
- **Language:** Python 3.8+
- **Type Hinting:** Strict type hinting is MANDATORY for all function arguments and return types (e.g., `def unlock(password: str) -> bool:`).
- **GUI Framework:** Use `PySide6`. Follow reactive Qt patterns (Signals and Slots) for UI updates. Separate UI logic from cryptographic business logic.
- **Formatting:** Follow PEP 8 guidelines. Use clear, descriptive variable names.

## 2. File Organization
- `/app`: Application entry points and CLI logic.
- `/gui`: (NEW) All PySide6 views, components, and window layouts.
- `/crypto`: Low-level cryptographic operations. Do NOT modify without re-running `pytest`.
- `/vault`: Database and repository abstractions.
- `/security`: Auditing, TOTP, and breach checks.

## 3. Security Mandates (CRITICAL)
- **Zero Plaintext Logs:** NEVER log or `print()` master passwords, derived keys, or decrypted credentials.
- **Memory Wiping:** When closing the vault or locking, call `KeyManager.lock()` to release keys. 
- **Clipboard Hygiene:** When implementing PySide6 clipboard copying, attach a `QTimer` to clear the clipboard after 30 seconds.
- **SQL Injection Prevention:** ALWAYS use parameterized SQLite queries (`?`). Never use f-strings or string concatenation for SQL queries.

## 4. Forbidden Actions
- Do NOT install unvetted dependencies or alter `requirements.txt` without justification.
- Do NOT rewrite or modify the core cryptography layer (`crypto/encryption.py`, `crypto/kdf.py`) without an explicit directive. The current AES-256-GCM / Argon2id setup is verified and passing tests.
- Do NOT delete existing tests.