"""Secure Notes View."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QFrame, QLabel, QGridLayout
)
from PySide6.QtCore import Qt
from typing import Optional
import sys
from pathlib import Path
import qtawesome as qta

sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.repository import VaultRepository
from .note_modal import NoteModal
from .components import PageHeader

class NotesView(QWidget):
    """View displaying a table of secure notes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault: Optional[VaultRepository] = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = PageHeader("Secure Notes", "Private notes protected inside your vault")
        layout.addWidget(self.header)

        # Body
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(38, 28, 38, 40)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search secure notes...")
        self.search_bar.setFixedWidth(360)
        self.search_bar.textChanged.connect(self.refresh_grid)

        self.btn_add = QPushButton(f"{qta.charmap('ph.plus')} New Note")
        self.btn_add.setFont(qta.font('ph', 12))
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self._on_add_clicked)

        toolbar_layout.addWidget(self.search_bar)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_add)

        # Grid Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 20, 0, 0)
        self.grid_layout.setSpacing(13)
        self.grid_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.grid_container)

        # Assurance footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 18, 0, 0)
        lbl_lock = QLabel(qta.charmap('ph.lock-key'))
        lbl_lock.setFont(qta.font('ph', 15))
        lbl_lock.setStyleSheet("color: #66798c;")
        lbl_text = QLabel("All secure notes use end-to-end AES-256 encryption.")
        lbl_text.setStyleSheet("color: #66798c; font-size: 8px;")

        footer_layout.addWidget(lbl_lock)
        footer_layout.addWidget(lbl_text)
        footer_layout.addStretch()

        body_layout.addLayout(toolbar_layout)
        body_layout.addWidget(self.scroll_area)
        body_layout.addLayout(footer_layout)

        layout.addWidget(body_widget)

    def set_vault(self, vault: VaultRepository):
        self.vault = vault
        self.refresh_grid()

    def refresh_grid(self):
        if not self.vault or not self.vault.is_unlocked():
            return

        # Clear existing grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        notes = self.vault.list_secure_notes()
        search_term = self.search_bar.text().lower()
        if search_term:
            notes = [n for n in notes if search_term in n.title.lower() or search_term in n.category.lower()]

        row, col = 0, 0
        for note in notes:
            card = self._create_note_card(note)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 1: # 2 columns
                col = 0
                row += 1

    def _create_note_card(self, note) -> QFrame:
        card = QFrame()
        card.setProperty("class", "ContentSurface")
        card.setObjectName("ContentSurface")
        # Ensure the hover effect from styles triggers
        card.setFrameShape(QFrame.StyledPanel)
        card.setMinimumHeight(150)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(19, 19, 19, 19)

        # Header (Icon and Options)
        h_layout = QHBoxLayout()
        icon_lbl = QLabel(qta.charmap('ph.file-text'))
        icon_lbl.setFont(qta.font('ph', 20))
        icon_lbl.setStyleSheet("color: #c51f5d; border: 1px solid #3b556f; border-radius: 6px; background: #213241; padding: 8px;")
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignCenter)

        btn_opts = QPushButton(qta.charmap('ph.dots-three-vertical'))
        btn_opts.setFont(qta.font('ph', 16))
        btn_opts.setFixedSize(29, 29)
        btn_opts.setStyleSheet("background: transparent; border: none; color: #8295a7;")
        # Store note ref in button to open it later
        btn_opts.clicked.connect(lambda: self._open_note(note))

        h_layout.addWidget(icon_lbl)
        h_layout.addStretch()
        h_layout.addWidget(btn_opts)

        # Text
        lbl_title = QLabel(note.title)
        lbl_title.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 15px; margin-bottom: 5px;")

        lbl_desc = QLabel("This note is encrypted and protected inside your local vault.")
        lbl_desc.setStyleSheet("color: #8295a7; font-size: 9px;")
        lbl_desc.setWordWrap(True)

        # Footer
        f_layout = QHBoxLayout()
        lbl_cat = QLabel(note.category)
        lbl_cat.setStyleSheet("color: #92a3b2; font-size: 10px;")

        lbl_date = QLabel(f"{qta.charmap('ph.clock')} {note.updated_at.strftime('%Y-%m-%d')}")
        lbl_date.setFont(qta.font('ph', 12))
        lbl_date.setStyleSheet("color: #66798c;")

        f_layout.addWidget(lbl_cat)
        f_layout.addStretch()
        f_layout.addWidget(lbl_date)

        layout.addLayout(h_layout)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addStretch()

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #2e4358; margin-top: 15px; margin-bottom: 10px;")
        layout.addWidget(line)

        layout.addLayout(f_layout)
        return card

    def _open_note(self, note):
        modal = NoteModal(self, note=note)
        modal.exec()

    def _on_add_clicked(self):
        if not self.vault or not self.vault.is_unlocked():
            return
        modal = NoteModal(self, note=None)
        if modal.exec():
            data = modal.get_data()
            if data['title'] and data['content']:
                self.vault.add_secure_note(
                    title=data['title'],
                    content=data['content'],
                    category=data['category']
                )
                self.refresh_grid()