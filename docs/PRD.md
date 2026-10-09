# Product Requirements Document (PRD): LockByte

## 1. Product Overview
**Mission:** Provide a highly secure, local-first password manager and credential hygiene tool that empowers users to maintain complete ownership of their data while benefiting from modern cryptographic standards.
**Background:** LockByte currently operates as a fully functional CLI application utilizing AES-256-GCM encryption and Argon2id key derivation. The next phase introduces a graphical desktop interface to improve accessibility and usability without compromising security.

## 2. User Personas & Stories
### Target Audience
- **Security-Conscious Professionals / Developers:** Users who distrust cloud-sync password managers and prefer local, encrypted SQLite vaults. They understand the importance of 2FA, password entropy, and data breaches.

### User Stories
- *As a user, I want a graphical interface to view my vault so that I don't have to rely on command-line terminal interactions.*
- *As a user, I want to copy my passwords to the clipboard with one click and have them auto-clear after 30 seconds.*
- *As a user, I want to scan a QR code or paste a Base32 secret to manage my TOTP 2FA codes directly within the app.*
- *As a user, I want to export my vault to an encrypted JSON/CSV format for backup purposes.*

## 3. Core vs. MVP Scope
**Currently Completed (Phase 1 & 2):**
- Core cryptography (Argon2id, AES-256-GCM).
- CLI-based Vault CRUD operations.
- Security auditing & password generation.
- CLI-based TOTP/2FA and Secure Notes.

**Current MVP Scope (Phase 3 - GUI Expansion):**
- PySide6 Graphical Desktop Interface.
- Visual Dashboard for Security Audits.
- UI for TOTP / Secure Notes.
- JSON/CSV encrypted export/import.

**Out of Scope (Future Phases):**
- Mobile applications.
- Browser autofill extensions.
- Cloud synchronization.

## 4. Technical Stack & Constraints
- **Language:** Python 3.8+
- **GUI Framework:** PySide6 (Qt for Python)
- **Database:** SQLite3 (Local, Encrypted blobs)
- **Cryptography:** `cryptography` (AES-256-GCM), `argon2-cffi`
- **Security Constraints:** 
  - Master passwords must never be stored in memory longer than necessary.
  - Clipboard must be wiped after use.
  - Unlocked vaults must auto-lock after 15 minutes of inactivity.

## 5. UI/UX Design System
- **Theme:** Dark Mode by default (Cybersecurity aesthetic).
- **Layout:** 
  - Left Sidebar: Navigation (Vault, Generator, Audit, Settings).
  - Main Area: Data tables, detail views, and action buttons.
- **Interactions:** Use modal dialogues for sensitive actions (e.g., Master Password confirmation, deleting a credential).