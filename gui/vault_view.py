"""Vault view showing the list of credentials."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QPushButton, QFrame, QLabel
)
from PySide6.QtCore import Qt
from typing import Optional
import sys
from pathlib import Path
import qtawesome as qta

sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.repository import VaultRepository
from .credential_modal import CredentialModal
from .components import PageHeader

class VaultView(QWidget):
    """View displaying a searchable table of credentials."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault: Optional[VaultRepository] = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = PageHeader("Vault", "Your encrypted credentials")
        layout.addWidget(self.header)

        # Body Container
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(38, 28, 38, 40)

        # Toolbar (Search & Actions)
        toolbar_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search credentials...")
        self.search_bar.setFixedWidth(460)
        self.search_bar.textChanged.connect(self.refresh_table)

        self.btn_filter = QPushButton(f" {qta.charmap('ph.sliders-horizontal')} Filter")
        self.btn_filter.setFont(qta.font('ph', 12))
        self.btn_sort = QPushButton(f" Sort {qta.charmap('ph.caret-down')}")
        self.btn_sort.setFont(qta.font('ph', 12))
        self.btn_add = QPushButton(f" {qta.charmap('ph.plus')} Add Credential")
        self.btn_add.setFont(qta.font('ph', 12))
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self._on_add_clicked)

        toolbar_layout.addWidget(self.search_bar)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_filter)
        toolbar_layout.addWidget(self.btn_sort)
        toolbar_layout.addWidget(self.btn_add)

        body_layout.addLayout(toolbar_layout)
        body_layout.addSpacing(18)

        # Content Surface (The Table Card)
        surface = QFrame()
        surface.setObjectName("ContentSurface")
        surface.setProperty("class", "ContentSurface")
        surface_layout = QVBoxLayout(surface)
        surface_layout.setContentsMargins(0, 0, 0, 0)
        surface_layout.setSpacing(0)

        # Surface Header
        surface_header = QWidget()
        surface_header.setFixedHeight(61)
        surface_header.setStyleSheet("border-bottom: 1px solid #32485e;")
        sh_layout = QHBoxLayout(surface_header)
        sh_layout.setContentsMargins(20, 0, 20, 0)

        lbl_all = QLabel("All credentials")
        lbl_all.setStyleSheet("font-size: 12px; font-weight: 600; border: none;")
        self.lbl_count = QLabel("0 items")
        self.lbl_count.setStyleSheet("background: #243447; color: #8295a7; font-size: 8px; padding: 3px 7px; border-radius: 8px;")

        lbl_aes = QLabel(f"{qta.charmap('ph.lock-key')} AES-256 ENCRYPTED")
        lbl_aes.setFont(qta.font('ph', 10))
        lbl_aes.setStyleSheet("color: #607386; letter-spacing: 0.5px; font-weight: 600; border: none;")

        sh_layout.addWidget(lbl_all)
        sh_layout.addWidget(self.lbl_count)
        sh_layout.addStretch()
        sh_layout.addWidget(lbl_aes)

        surface_layout.addWidget(surface_header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Website", "Username", "Email", "Category", "2FA"])

        # Make table take up remaining space
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)

        surface_layout.addWidget(self.table)

        # Table Footer
        footer = QWidget()
        footer.setFixedHeight(49)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        lbl_sync = QLabel("Last synced just now")
        lbl_sync.setStyleSheet("color: #607386; font-size: 8px;")

        btn_prev = QPushButton("Previous")
        btn_prev.setFixedSize(60, 25)
        btn_prev.setStyleSheet("font-size: 8px; border-radius: 4px; padding: 0;")
        btn_next = QPushButton("Next")
        btn_next.setFixedSize(40, 25)
        btn_next.setStyleSheet("font-size: 8px; border-radius: 4px; padding: 0;")

        footer_layout.addWidget(lbl_sync)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_prev)
        footer_layout.addWidget(btn_next)

        surface_layout.addWidget(footer)
        body_layout.addWidget(surface)
        layout.addWidget(body_widget)

    def set_vault(self, vault: VaultRepository):
        """Set the active vault repository and load data."""
        self.vault = vault
        self.refresh_table()

    def refresh_table(self):
        """Fetch credentials from vault and populate the table."""
        if not self.vault or not self.vault.is_unlocked():
            self.table.setRowCount(0)
            return

        search_term = self.search_bar.text()
        credentials = self.vault.list_credentials(search_term if search_term else None)

        self.table.setRowCount(len(credentials))

        for row, cred in enumerate(credentials):
            # Custom Website Cell Widget
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.setContentsMargins(15, 5, 15, 5)

            # Initial box
            lbl_initial = QLabel(cred.website[0].upper() if cred.website else "?")
            lbl_initial.setFixedSize(33, 33)
            # Pick a dynamic color based on first letter for variety, fallback to grey
            color = "#80aa91" if row % 3 == 0 else ("#c51f5d" if row % 3 == 1 else "#7F93A8")
            lbl_initial.setStyleSheet(f"color: {color}; border: 1px solid #364e66; border-radius: 6px; background: #20303f; font-size: 14px; font-weight: bold;")
            lbl_initial.setAlignment(Qt.AlignCenter)

            # Text stack
            text_layout = QVBoxLayout()
            text_layout.setSpacing(3)
            lbl_web = QLabel(cred.website)
            lbl_web.setStyleSheet("color: #deded1; font-size: 10px; font-weight: bold; border: none;")
            lbl_dom = QLabel(cred.url if cred.url else cred.website.lower() + ".com")
            lbl_dom.setStyleSheet("color: #66798c; font-size: 8px; border: none;")
            text_layout.addWidget(lbl_web)
            text_layout.addWidget(lbl_dom)

            cell_layout.addWidget(lbl_initial)
            cell_layout.addLayout(text_layout)
            cell_layout.addStretch()

            self.table.setCellWidget(row, 0, cell_widget)

            # Store item invisibly for data retrieval on click
            hidden_item = QTableWidgetItem(cred.website)
            hidden_item.setData(Qt.UserRole, cred)
            self.table.setItem(row, 0, hidden_item)

            self.table.setItem(row, 1, QTableWidgetItem(cred.username))

            email_item = QTableWidgetItem(cred.email)
            email_item.setForeground(Qt.gray)
            self.table.setItem(row, 2, email_item)

            self.table.setItem(row, 3, QTableWidgetItem(cred.category.value.title()))

            # Custom 2FA Column
            has_2fa_str = f"🟢 Enabled" if cred.has_2fa else f"⚫ Not enabled"
            color = "#809e91" if cred.has_2fa else "#8295a7"
            item_2fa = QTableWidgetItem(has_2fa_str)
            item_2fa.setForeground(Qt.white if cred.has_2fa else Qt.gray)
            self.table.setItem(row, 4, item_2fa)

        # Update Count Label
        self.lbl_count.setText(f"{len(credentials)} items")

    def _on_row_double_clicked(self, row: int, col: int):
        """Handle opening a credential for viewing/editing."""
        item = self.table.item(row, 0)
        cred = item.data(Qt.UserRole)

        modal = CredentialModal(self, credential=cred)
        modal.exec() # Open dialog modally

    def _on_add_clicked(self):
        """Handle creating a new credential."""
        if not self.vault or not self.vault.is_unlocked():
            return

        modal = CredentialModal(self, credential=None)
        if modal.exec():
            # User clicked Save
            data = modal.get_data()
            if data['website'] and data['password']:
                self.vault.add_credential(
                    website=data['website'],
                    username=data['username'],
                    password=data['password'],
                    email=data['email'],
                    url=data['url'],
                    category=data['category'],
                    notes=data['notes'],
                    totp_secret=data['totp_secret']
                )
                self.refresh_table()