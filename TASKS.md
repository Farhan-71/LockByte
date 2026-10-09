# LockByte GUI Execution Breakdown

This document breaks down the development of the PySide6 Desktop Interface and Export/Import tools into sequential, manageable tasks.

## Stage 1: GUI Scaffolding & Setup
- [ ] Initialize `/gui` directory structure.
- [ ] Create the main PySide6 `QApplication` entry point (`gui/app.py`).
- [ ] Build the base `MainWindow` layout (Left Sidebar + Main Content Area).
- [ ] Implement a Dark Mode stylesheet / theme setup.

## Stage 2: Authentication & Vault Unlock
- [ ] Build the "Welcome/Setup" View for new users (Master Password creation).
- [ ] Build the "Unlock Vault" View for returning users.
- [ ] Connect the `KeyManager` and `VaultRepository` to the Unlock UI.
- [ ] Implement the 15-minute inactivity Auto-Lock timer (`QTimer`).

## Stage 3: Core Vault Management (CRUD)
- [ ] Build the Credential List View (Table with columns: Website, Username, Category).
- [ ] Implement search/filtering for the Credential List.
- [ ] Build the "Credential Detail" Modal (View/Edit password, View TOTP codes).
- [ ] Implement secure "Copy to Clipboard" with a 30-second auto-clear.

## Stage 4: Enhanced Security Features
- [ ] Build the "Password Generator" View (Sliders for length, toggles for rules).
- [ ] Build the "Security Audit Dashboard" View (Display overall score, weak passwords, and breach results).
- [ ] Build the "Secure Notes" tab.

## Stage 5: Import / Export & Polish
- [ ] Implement Export logic: Decrypt vault and write to an encrypted JSON/CSV file.
- [ ] Implement Import logic: Read CSV/JSON, encrypt records, and insert into SQLite.
- [ ] Build Import/Export UI Modals.
- [ ] Final UI Polish (Icons, tooltips, responsive resizing).