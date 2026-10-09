"""Secure Note Detail and Edit Modal."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QApplication
)
from PySide6.QtCore import Qt, QTimer
import sys
from pathlib import Path

# Ensure backend imports work
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.models import SecureNote
from .credential_modal import SecureClipboard


class NoteModal(QDialog):
    """Modal dialog for viewing, creating, or editing a secure note."""

    def __init__(self, parent=None, note: SecureNote = None):
        super().__init__(parent)
        self.note = note
        self.clipboard = SecureClipboard()
        self.is_edit_mode = note is None

        self.setWindowTitle("Secure Note" if note else "New Secure Note")
        self.setMinimumSize(500, 400)

        self._init_ui()
        if note:
            self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        self.inp_title = QLineEdit()
        title_layout.addWidget(self.inp_title)

        # Category
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        self.inp_category = QLineEdit()
        self.inp_category.setPlaceholderText("e.g. note, recovery_code, license")
        cat_layout.addWidget(self.inp_category)

        # Content
        layout.addLayout(title_layout)
        layout.addLayout(cat_layout)
        layout.addWidget(QLabel("Content:"))

        self.inp_content = QTextEdit()
        self.inp_content.setAcceptRichText(False)
        layout.addWidget(self.inp_content)

        # Action Buttons
        btn_layout = QHBoxLayout()

        self.btn_copy = QPushButton("Copy Content")
        self.btn_copy.clicked.connect(self._copy_content)
        if self.is_edit_mode:
            self.btn_copy.hide()

        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_copy)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

        # Set Read-Only if viewing
        if not self.is_edit_mode:
            self._set_read_only(True)

    def _set_read_only(self, readonly: bool):
        self.inp_title.setReadOnly(readonly)
        self.inp_category.setReadOnly(readonly)
        self.inp_content.setReadOnly(readonly)

        self.btn_save.setVisible(not readonly)
        if not readonly:
            self.btn_cancel.setText("Cancel")
        else:
            self.btn_cancel.setText("Close")

    def _load_data(self):
        """Load note data into the form."""
        self.inp_title.setText(self.note.title)
        self.inp_category.setText(self.note.category)
        self.inp_content.setPlainText(self.note.content)

    def _copy_content(self):
        self.clipboard.copy(self.inp_content.toPlainText())
        original_text = self.btn_copy.text()
        self.btn_copy.setText("Copied!")
        QTimer.singleShot(2000, lambda: self.btn_copy.setText(original_text))

    def get_data(self) -> dict:
        """Get the form data."""
        return {
            'title': self.inp_title.text().strip(),
            'category': self.inp_category.text().strip() or "note",
            'content': self.inp_content.toPlainText()
        }