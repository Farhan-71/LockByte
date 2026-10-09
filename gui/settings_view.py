"""Settings View for Import/Export and preferences."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QMessageBox, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt
from typing import Optional
import sys
from pathlib import Path
import qtawesome as qta

sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.repository import VaultRepository
from vault.export_import import VaultIO
from .components import PageHeader, ToggleSwitch

class SettingsView(QWidget):
    """View for managing settings and data export/import."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault: Optional[VaultRepository] = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = PageHeader("Settings", "Manage your vault preferences and security")
        layout.addWidget(self.header)

        # Scrollable Body Container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        body_widget = QWidget()
        body_layout = QGridLayout(body_widget)
        body_layout.setContentsMargins(38, 28, 38, 40)
        body_layout.setSpacing(13)
        body_layout.setAlignment(Qt.AlignTop)

        # --- SECTIONS ---

        # 1. Account Section
        sec_account = self._build_section("Account", "ph.user-circle")
        self._add_row(sec_account, "Profile", "Farhan Khan • user@example.com", "Manage")

        # 2. Security Section
        sec_security = self._build_section("Security", "ph.shield-check", icon_color="#c51f5d")
        self._add_row(sec_security, "Master Password", "Last changed 34 days ago", "Change")
        self._add_row(sec_security, "Auto-Lock", "Lock vault after 15 minutes", "15 min")
        self._add_row(sec_security, "Biometric Unlock", "Use device biometrics to unlock", toggle=True, checked=True)
        self._add_row(sec_security, "Two-Factor Authentication", "Require verification when signing in", toggle=True, checked=True)
        self._add_row(sec_security, "Session Timeout", "End inactive sessions automatically", "30 min", last=True)

        # 3. Vault Section (Includes Import/Export functionality)
        sec_vault = self._build_section("Vault", "ph.database", icon_color="#c51f5d")
        self._add_row(sec_vault, "Vault Location", "Stored locally on this device", "View")
        self._add_row(sec_vault, "Clipboard Protection", "Clear copied passwords after 30 seconds", toggle=True, checked=True)

        # Export Row
        export_btn = QPushButton("Export JSON")
        export_btn.setObjectName("SettingsComboButton")
        export_btn.clicked.connect(lambda: self._handle_export(True))
        self._add_custom_row(sec_vault, "Export Data", "Export vault to JSON format (Plaintext)", export_btn)

        # Import Row
        import_btn = QPushButton("Import JSON")
        import_btn.setObjectName("SettingsComboButton")
        import_btn.clicked.connect(lambda: self._handle_import(True))
        self._add_custom_row(sec_vault, "Import Data", "Import and encrypt data from JSON", import_btn, last=True)

        # 4. Notifications Section
        sec_notif = self._build_section("Notifications", "ph.warning", icon_color="#c51f5d")
        self._add_row(sec_notif, "Security Alerts", "Receive important vault security updates", toggle=True, checked=False, last=True)

        # 5. Privacy Section
        sec_privacy = self._build_section("Privacy", "ph.fingerprint", icon_color="#c51f5d")
        self._add_row(sec_privacy, "Analytics", "Usage analytics are disabled", "Private", last=True)

        # 6. Appearance Section
        sec_appearance = self._build_section("Appearance", "ph.gear", icon_color="#c51f5d")
        self._add_row(sec_appearance, "Theme", "Graphite dark", "Dark", last=True)

        # Add to Grid (Left Col, Right Col)
        body_layout.addWidget(sec_account, 0, 0)
        body_layout.addWidget(sec_vault, 1, 0)
        body_layout.addWidget(sec_privacy, 2, 0)

        body_layout.addWidget(sec_security, 0, 1, 2, 1) # Span 2 rows
        body_layout.addWidget(sec_notif, 2, 1)
        body_layout.addWidget(sec_appearance, 3, 1)

        scroll_area.setWidget(body_widget)
        layout.addWidget(scroll_area)

    def _build_section(self, title: str, icon_name: str, icon_color: str = "#c51f5d") -> QFrame:
        """Create a section card."""
        frame = QFrame()
        frame.setProperty("class", "ContentSurface")
        frame.setObjectName("ContentSurface")

        # Store internal layout for rows
        frame.rows_layout = QVBoxLayout(frame)
        frame.rows_layout.setContentsMargins(0, 0, 0, 0)
        frame.rows_layout.setSpacing(0)

        # Section Header
        header_widget = QWidget()
        header_widget.setFixedHeight(51)
        header_widget.setStyleSheet("border-bottom: 1px solid #32485e;")
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(17, 0, 17, 0)
        h_layout.setSpacing(9)

        icon = QLabel(qta.charmap(icon_name))
        icon.setFont(qta.font('ph', 18))
        icon.setStyleSheet(f"color: {icon_color}; border: none;")

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #dbdbce; font-size: 11px; font-weight: bold; border: none;")

        h_layout.addWidget(icon)
        h_layout.addWidget(lbl_title)
        h_layout.addStretch()

        frame.rows_layout.addWidget(header_widget)
        return frame

    def _add_row(self, section: QFrame, title: str, subtitle: str, action_text: str = "", toggle: bool = False, checked: bool = False, last: bool = False):
        """Add a standard settings row to a section."""
        row_widget = QWidget()
        row_widget.setMinimumHeight(58)

        border_style = "border-bottom: 1px solid #293c4f;" if not last else "border-bottom: none;"
        row_widget.setStyleSheet(f"{border_style}")

        r_layout = QHBoxLayout(row_widget)
        r_layout.setContentsMargins(17, 0, 17, 0)

        # Text Column
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setAlignment(Qt.AlignVCenter)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 9.5px; font-weight: 500; border: none;")

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("color: #8295a7; font-size: 8px; border: none;")

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_sub)

        r_layout.addLayout(text_layout)
        r_layout.addStretch()

        # Action Column
        if toggle:
            switch = ToggleSwitch()
            switch.setChecked(checked)
            switch.setStyleSheet("border: none;")
            r_layout.addWidget(switch)
        elif action_text:
            btn = QPushButton(f"{action_text} {qta.charmap('ph.caret-down')}")
            btn.setFont(qta.font('ph', 12))
            btn.setObjectName("SettingsComboButton")
            r_layout.addWidget(btn)

        section.rows_layout.addWidget(row_widget)

    def _add_custom_row(self, section: QFrame, title: str, subtitle: str, custom_action_widget: QWidget, last: bool = False):
        """Add a row with a custom action widget."""
        row_widget = QWidget()
        row_widget.setMinimumHeight(58)
        border_style = "border-bottom: 1px solid #293c4f;" if not last else "border-bottom: none;"
        row_widget.setStyleSheet(f"{border_style}")

        r_layout = QHBoxLayout(row_widget)
        r_layout.setContentsMargins(17, 0, 17, 0)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        text_layout.setAlignment(Qt.AlignVCenter)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 9.5px; font-weight: 500; border: none;")

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("color: #8295a7; font-size: 8px; border: none;")

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_sub)

        r_layout.addLayout(text_layout)
        r_layout.addStretch()

        r_layout.addWidget(custom_action_widget)
        section.rows_layout.addWidget(row_widget)

    def set_vault(self, vault: VaultRepository):
        self.vault = vault

    def _handle_export(self, is_json: bool):
        if not self.vault or not self.vault.is_unlocked():
            QMessageBox.critical(self, "Error", "Vault is locked.")
            return

        filter_str = "JSON Files (*.json)"
        default_ext = ".json"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Vault", f"lockbyte_export{default_ext}", filter_str
        )

        if not file_path:
            return # User cancelled

        io_handler = VaultIO(self.vault)
        success = io_handler.export_json(file_path)

        if success:
            QMessageBox.information(self, "Export Successful",
                                    f"Data exported securely to:\n{file_path}\n\n"
                                    "Please remember to delete this file when you are done with it!")
        else:
            QMessageBox.critical(self, "Export Failed", "An error occurred during export.")

    def _handle_import(self, is_json: bool):
        if not self.vault or not self.vault.is_unlocked():
            QMessageBox.critical(self, "Error", "Vault is locked.")
            return

        filter_str = "JSON Files (*.json)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Vault", "", filter_str
        )

        if not file_path:
            return

        io_handler = VaultIO(self.vault)

        creds, notes = io_handler.import_json(file_path)
        if creds > 0 or notes > 0:
            QMessageBox.information(self, "Import Successful", f"Successfully imported {creds} credentials and {notes} secure notes.")
            self.parent().parent().parent().view_vault.refresh_table() # Hack to refresh view
        else:
            QMessageBox.warning(self, "Import Warning", "No valid data found to import.")