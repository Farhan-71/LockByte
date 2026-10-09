"""Credential Detail and Edit Modal."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QApplication, QComboBox
)
from PySide6.QtCore import Qt, QTimer
import sys
from pathlib import Path
import qtawesome as qta

# Ensure backend imports work
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.models import Credential, CredentialCategory
from security.totp import TOTPGenerator

class SecureClipboard:
    """Manages secure clipboard copying with auto-clear."""

    def __init__(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        # Clear after 30 seconds
        self.timer.setInterval(30000)
        self.timer.timeout.connect(self.clear)

    def copy(self, text: str):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.timer.start()

    def clear(self):
        clipboard = QApplication.clipboard()
        clipboard.clear()


class CredentialModal(QDialog):
    """Modal dialog for viewing, creating, or editing a credential."""

    def __init__(self, parent=None, credential: Credential = None):
        super().__init__(parent)
        self.credential = credential
        self.clipboard = SecureClipboard()
        self.is_edit_mode = credential is None

        self.setWindowTitle("Credential Details" if credential else "New Credential")
        self.setMinimumWidth(400)

        self._init_ui()
        if credential:
            self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Form Fields
        self.inp_website = QLineEdit()
        self.inp_username = QLineEdit()
        self.inp_email = QLineEdit()

        self.inp_password = QLineEdit()
        self.inp_password.setEchoMode(QLineEdit.Password)

        self.inp_url = QLineEdit()
        self.inp_notes = QLineEdit()

        self.combo_category = QComboBox()
        for cat in CredentialCategory:
            self.combo_category.addItem(cat.value.title(), cat)

        self.inp_totp_secret = QLineEdit()
        self.inp_totp_secret.setPlaceholderText("Base32 Secret for 2FA")

        # Layout Assembly
        form_layout.addRow("Website:", self.inp_website)
        form_layout.addRow("Username:", self.inp_username)
        form_layout.addRow("Email:", self.inp_email)

        # Password row with copy/reveal buttons
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(self.inp_password)

        self.btn_reveal_pwd = QPushButton(qta.charmap('ph.eye'))
        self.btn_reveal_pwd.setFont(qta.font('ph', 12))
        self.btn_reveal_pwd.setFixedWidth(30)
        self.btn_reveal_pwd.pressed.connect(lambda: self.inp_password.setEchoMode(QLineEdit.Normal))
        self.btn_reveal_pwd.released.connect(lambda: self.inp_password.setEchoMode(QLineEdit.Password))

        self.btn_copy_pwd = QPushButton("Copy")
        self.btn_copy_pwd.clicked.connect(self._copy_password)

        pwd_layout.addWidget(self.btn_reveal_pwd)
        pwd_layout.addWidget(self.btn_copy_pwd)
        form_layout.addRow("Password:", pwd_layout)

        form_layout.addRow("URL:", self.inp_url)
        form_layout.addRow("Category:", self.combo_category)
        form_layout.addRow("Notes:", self.inp_notes)
        form_layout.addRow("TOTP Secret:", self.inp_totp_secret)

        # TOTP Display Row (Only used if viewing an existing credential with 2FA)
        self.totp_display_label = QLabel("")
        self.totp_display_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4DA8DA;")
        self.totp_timer_label = QLabel("")

        totp_layout = QHBoxLayout()
        totp_layout.addWidget(self.totp_display_label)
        totp_layout.addWidget(self.totp_timer_label)

        self.btn_copy_totp = QPushButton("Copy 2FA")
        self.btn_copy_totp.clicked.connect(self._copy_totp)
        self.btn_copy_totp.hide()
        totp_layout.addWidget(self.btn_copy_totp)

        form_layout.addRow("Current 2FA:", totp_layout)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)

        # Set Read-Only if viewing
        if not self.is_edit_mode:
            self._set_read_only(True)

        # TOTP Timer
        self.totp_refresh_timer = QTimer(self)
        self.totp_refresh_timer.setInterval(1000)
        self.totp_refresh_timer.timeout.connect(self._update_totp_display)

    def _set_read_only(self, readonly: bool):
        self.inp_website.setReadOnly(readonly)
        self.inp_username.setReadOnly(readonly)
        self.inp_email.setReadOnly(readonly)
        self.inp_password.setReadOnly(readonly)
        self.inp_url.setReadOnly(readonly)
        self.inp_notes.setReadOnly(readonly)
        self.combo_category.setEnabled(not readonly)
        self.inp_totp_secret.setReadOnly(readonly)

        # If readonly, hide the save button and allow editing via a double click?
        # For simplicity, we just hide save unless editing.
        self.btn_save.setVisible(not readonly)
        if not readonly:
            self.btn_cancel.setText("Cancel")
        else:
            self.btn_cancel.setText("Close")

    def _load_data(self):
        """Load credential data into the form."""
        c = self.credential
        self.inp_website.setText(c.website)
        self.inp_username.setText(c.username)
        self.inp_email.setText(c.email)
        self.inp_password.setText(c.password)
        self.inp_url.setText(c.url)
        self.inp_notes.setText(c.notes)

        # Set category combo box
        idx = self.combo_category.findData(c.category)
        if idx >= 0:
            self.combo_category.setCurrentIndex(idx)

        if c.has_2fa and c.totp_secret:
            self.inp_totp_secret.setText(c.totp_secret)
            # We don't want to show the secret in plaintext normally, but we need it for generation
            self.inp_totp_secret.setEchoMode(QLineEdit.Password)
            self.btn_copy_totp.show()
            self._update_totp_display()
            self.totp_refresh_timer.start()

    def _update_totp_display(self):
        """Update the live TOTP code and countdown."""
        if not self.credential or not self.credential.totp_secret:
            return

        gen = TOTPGenerator()
        code = gen.generate(self.credential.totp_secret)
        remaining = gen.get_remaining_time()

        self.totp_display_label.setText(code)
        self.totp_timer_label.setText(f"({remaining}s)")

    def _copy_password(self):
        self.clipboard.copy(self.inp_password.text())
        self._temp_button_text(self.btn_copy_pwd, "Copied!")

    def _copy_totp(self):
        self.clipboard.copy(self.totp_display_label.text())
        self._temp_button_text(self.btn_copy_totp, "Copied!")

    def _temp_button_text(self, button: QPushButton, temp_text: str):
        """Temporarily change button text for visual feedback."""
        original_text = button.text()
        button.setText(temp_text)
        QTimer.singleShot(2000, lambda: button.setText(original_text))

    def get_data(self) -> dict:
        """Get the form data."""
        # Handle PySide6 potentially converting string enums to raw strings
        cat_data = self.combo_category.currentData()
        category_val = cat_data.value if hasattr(cat_data, 'value') else cat_data

        return {
            'website': self.inp_website.text().strip(),
            'username': self.inp_username.text().strip(),
            'email': self.inp_email.text().strip(),
            'password': self.inp_password.text().strip(),
            'url': self.inp_url.text().strip(),
            'notes': self.inp_notes.text().strip(),
            'category': category_val,
            'totp_secret': self.inp_totp_secret.text().strip() or None
        }