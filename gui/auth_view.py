"""Authentication views for LockByte GUI."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
import qtawesome as qta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.components import SecurityBackdrop


class LandingView(QWidget):
    """Initial landing page before setup/unlock."""
    open_app = Signal()

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Backdrop
        self.backdrop = SecurityBackdrop(self)
        self.backdrop.resize(2000, 2000) # Oversize to ensure it fills

        # Top-left Logo
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(40, 28, 0, 0)

        logo_icon = QLabel()
        pixmap_mark = QPixmap(str(Path(__file__).parent / "assets" / "lockbyte-mark.png"))
        if not pixmap_mark.isNull():
            logo_icon.setPixmap(pixmap_mark.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_icon.setText(qta.charmap('ph.lock'))
            logo_icon.setFont(qta.font('ph', 16))
            logo_icon.setStyleSheet("color: #e2e2d2; border: 1px solid #32485e; border-radius: 9px; padding: 10px; background: #141d26;")

        logo_text = QLabel("LockByte")
        logo_text.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e2d2; margin-left: 5px;")

        top_layout.addWidget(logo_icon)
        top_layout.addWidget(logo_text)
        top_layout.addStretch()

        # Center Content
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(15)

        # Giant Hero Icon
        hero_icon = QLabel()
        pixmap_full = QPixmap(str(Path(__file__).parent / "assets" / "lockbyte-full.webp"))
        if not pixmap_full.isNull():
            hero_icon.setPixmap(pixmap_full.scaled(430, 225, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            hero_icon.setText(qta.charmap('ph.lock'))
            hero_icon.setFont(qta.font('ph', 100))
            hero_icon.setStyleSheet("color: #c51f5d;")
        hero_icon.setAlignment(Qt.AlignCenter)

        lbl_overline = QLabel("PRIVATE CREDENTIAL SECURITY")
        lbl_overline.setStyleSheet("color: #c51f5d; font-size: 9px; font-weight: 700; letter-spacing: 1.9px;")
        lbl_overline.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel("Your passwords. Your privacy. Your vault.")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: 500; color: #d7d7ca;")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_desc = QLabel("Secure your digital credentials with a private, encrypted password manager.")
        lbl_desc.setStyleSheet("color: #8295a7; font-size: 13px;")
        lbl_desc.setAlignment(Qt.AlignCenter)

        # Actions
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        btn_open = QPushButton(f"{qta.charmap('ph.lock-key-open')} Open LockByte")
        btn_open.setFont(qta.font('ph', 12))
        btn_open.setObjectName("PrimaryButton")
        btn_open.setMinimumHeight(44)
        btn_open.setMinimumWidth(180)
        btn_open.clicked.connect(self.open_app.emit)

        btn_learn = QPushButton(f"{qta.charmap('ph.shield')} Learn About Security")
        btn_learn.setFont(qta.font('ph', 12))
        btn_learn.setMinimumHeight(44)
        btn_learn.setMinimumWidth(200)

        btn_layout.addWidget(btn_open)
        btn_layout.addWidget(btn_learn)

        # Features Row
        feat_layout = QHBoxLayout()
        feat_layout.setAlignment(Qt.AlignCenter)
        feat_layout.setSpacing(30)

        for icon, text in [
            (qta.charmap('ph.lock-key'), "AES-256 Encryption"),
            (qta.charmap('ph.shield-check'), "Zero-Knowledge Architecture"),
            (qta.charmap('ph.database'), "Local Vault"),
            (qta.charmap('ph.key'), "TOTP 2FA")
        ]:
            lbl = QLabel(f"{icon} {text}")
            lbl.setFont(qta.font('ph', 10))
            lbl.setStyleSheet("color: #9cabb7;")
            feat_layout.addWidget(lbl)

        center_layout.addWidget(hero_icon)
        center_layout.addWidget(lbl_overline)
        center_layout.addWidget(lbl_title)
        center_layout.addWidget(lbl_desc)
        center_layout.addSpacing(15)
        center_layout.addLayout(btn_layout)
        center_layout.addSpacing(30)
        center_layout.addLayout(feat_layout)

        # Footer
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignCenter)
        lbl_footer = QLabel("🟢 Your credentials stay protected.")
        lbl_footer.setStyleSheet("color: #66798c; font-size: 9px; margin-bottom: 27px;")
        bottom_layout.addWidget(lbl_footer)

        layout.addLayout(top_layout)
        layout.addWidget(center_widget)
        layout.addStretch()
        layout.addLayout(bottom_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.backdrop.resize(self.size())


class SetupView(QWidget):
    """View for first-time vault setup."""

    # Signal emitted when user attempts to set a master password
    setup_attempted = Signal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Backdrop
        self.backdrop = SecurityBackdrop(self)
        self.backdrop.resize(2000, 2000)

        # Top-left Logo
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(40, 28, 0, 0)

        logo_icon = QLabel()
        pixmap_mark = QPixmap(str(Path(__file__).parent / "assets" / "lockbyte-mark.png"))
        if not pixmap_mark.isNull():
            logo_icon.setPixmap(pixmap_mark.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_icon.setText(qta.charmap('ph.lock'))
            logo_icon.setFont(qta.font('ph', 16))
            logo_icon.setStyleSheet("color: #e2e2d2; border: 1px solid #32485e; border-radius: 9px; padding: 10px; background: #141d26;")

        logo_text = QLabel("LockByte")
        logo_text.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e2d2; margin-left: 5px;")

        top_layout.addWidget(logo_icon)
        top_layout.addWidget(logo_text)
        top_layout.addStretch()

        # Container for centering
        container = QFrame()
        container.setObjectName("SetupCard")
        container.setFixedWidth(900)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)

        # Header
        lbl_step = QLabel("INITIAL SETUP • 1 OF 1")
        lbl_step.setStyleSheet("color: #8295a7; font-family: 'IBM Plex Mono'; font-size: 8px; font-weight: 600; letter-spacing: 1px; border: 1px solid #32485e; padding: 6px 10px; border-radius: 4px;")
        lbl_step.setAlignment(Qt.AlignCenter)

        header = QLabel("Welcome to LockByte")
        header.setStyleSheet("font-size: 34px; letter-spacing: -1.2px; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)

        sub_header = QLabel("Create a new secure vault by setting a Master Password.\nThis password will NEVER be stored and cannot be recovered.")
        sub_header.setAlignment(Qt.AlignCenter)
        sub_header.setWordWrap(True)
        sub_header.setStyleSheet("color: #8295a7; margin-bottom: 20px;")

        container_layout.addWidget(lbl_step, 0, Qt.AlignHCenter)
        container_layout.addWidget(header)
        container_layout.addWidget(sub_header)
        container_layout.addSpacing(20)

        # 3 Cards Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        for title, desc, icon in [
            ("Secure Vault", "Store passwords and credentials securely.", qta.charmap('ph.lock')),
            ("Password Generator", "Create strong, unique passwords.", qta.charmap('ph.magic-wand')),
            ("Security Audit", "Identify weak and reused credentials.", qta.charmap('ph.shield-check'))
        ]:
            card = QFrame()
            card.setObjectName("SetupCard")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(24, 27, 24, 25)

            i_lbl = QLabel(icon)
            i_lbl.setFont(qta.font('ph', 21))
            i_lbl.setStyleSheet("color: #c51f5d; border: 1px solid #3e5973; background: #223343; border-radius: 6px; padding: 8px;")
            i_lbl.setFixedSize(38, 38)
            i_lbl.setAlignment(Qt.AlignCenter)

            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("font-size: 13px; font-weight: bold; margin-top: 10px; border: none;")

            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet("color: #8295a7; font-size: 10px; border: none;")
            d_lbl.setWordWrap(True)

            c_layout.addWidget(i_lbl)
            c_layout.addWidget(t_lbl)
            c_layout.addWidget(d_lbl)

            cards_layout.addWidget(card)

        container_layout.addLayout(cards_layout)
        container_layout.addSpacing(20)

        # Inputs
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignHCenter)

        self.pwd_input1 = QLineEdit()
        self.pwd_input1.setPlaceholderText("Master Password (min 8 characters)")
        self.pwd_input1.setEchoMode(QLineEdit.Password)
        self.pwd_input1.setFixedWidth(300)

        self.pwd_input2 = QLineEdit()
        self.pwd_input2.setPlaceholderText("Confirm Master Password")
        self.pwd_input2.setEchoMode(QLineEdit.Password)
        self.pwd_input2.setFixedWidth(300)

        # Error Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #c95b6d; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignCenter)

        # Button
        self.btn_setup = QPushButton(f"{qta.charmap('ph.lock')} Create Secure Vault")
        self.btn_setup.setFont(qta.font('ph', 12))
        self.btn_setup.setObjectName("PrimaryButton")
        self.btn_setup.setMinimumHeight(44)
        self.btn_setup.setFixedWidth(250)
        self.btn_setup.clicked.connect(self._on_setup_clicked)

        # Allow hitting Enter to submit
        self.pwd_input1.returnPressed.connect(self.pwd_input2.setFocus)
        self.pwd_input2.returnPressed.connect(self._on_setup_clicked)

        form_layout.addWidget(self.pwd_input1)
        form_layout.addWidget(self.pwd_input2)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(self.btn_setup, 0, Qt.AlignHCenter)

        container_layout.addLayout(form_layout)

        layout.addLayout(top_layout)
        layout.addStretch()
        layout.addWidget(container, 0, Qt.AlignHCenter)
        layout.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'backdrop'):
            self.backdrop.resize(self.size())

    def _on_setup_clicked(self):
        pwd1 = self.pwd_input1.text()
        pwd2 = self.pwd_input2.text()

        if len(pwd1) < 8:
            self.show_error("Password must be at least 8 characters.")
            return

        if pwd1 != pwd2:
            self.show_error("Passwords do not match.")
            return

        self.error_label.setText("")
        self.setup_attempted.emit(pwd1)

    def show_error(self, message: str):
        """Display an error message."""
        self.error_label.setText(message)
        self.pwd_input1.clear()
        self.pwd_input2.clear()
        self.pwd_input1.setFocus()


class UnlockView(QWidget):
    """View for unlocking an existing vault."""

    # Signal emitted when user attempts to unlock
    unlock_attempted = Signal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Backdrop
        self.backdrop = SecurityBackdrop(self)
        self.backdrop.resize(2000, 2000)

        # Top-left Logo
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(40, 28, 0, 0)

        logo_icon = QLabel()
        pixmap_mark = QPixmap(str(Path(__file__).parent / "assets" / "lockbyte-mark.png"))
        if not pixmap_mark.isNull():
            logo_icon.setPixmap(pixmap_mark.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_icon.setText(qta.charmap('ph.lock'))
            logo_icon.setFont(qta.font('ph', 16))
            logo_icon.setStyleSheet("color: #e2e2d2; border: 1px solid #32485e; border-radius: 9px; padding: 10px; background: #141d26;")

        logo_text = QLabel("LockByte")
        logo_text.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e2d2; margin-left: 5px;")

        top_layout.addWidget(logo_icon)
        top_layout.addWidget(logo_text)
        top_layout.addStretch()

        # Container for centering
        container = QFrame()
        container.setObjectName("AuthCard")
        container.setFixedWidth(440)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(38, 37, 38, 32)
        container_layout.setSpacing(15)

        # Header
        icon_lbl = QLabel(qta.charmap('ph.lock-key'))
        icon_lbl.setFont(qta.font('ph', 30))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("color: #e2e2d2; border: 1px solid #3c5771; background: #223343; border-radius: 12px; padding: 15px;")

        icon_container = QHBoxLayout()
        icon_container.setAlignment(Qt.AlignCenter)
        icon_container.addWidget(icon_lbl)

        lbl_overline = QLabel("LOCAL VAULT")
        lbl_overline.setStyleSheet("color: #c51f5d; font-size: 9px; font-weight: 700; letter-spacing: 1.9px; margin-top: 10px;")
        lbl_overline.setAlignment(Qt.AlignCenter)

        header = QLabel("Unlock Your Vault")
        header.setStyleSheet("font-size: 25px; letter-spacing: -.8px; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)

        sub_header = QLabel("Enter your master password to continue.")
        sub_header.setAlignment(Qt.AlignCenter)
        sub_header.setStyleSheet("color: #8295a7; margin-bottom: 20px; font-size: 11px;")

        container_layout.addLayout(icon_container)
        container_layout.addWidget(lbl_overline)
        container_layout.addWidget(header)
        container_layout.addWidget(sub_header)

        # Input Form
        lbl_pwd = QLabel("Master password")
        lbl_pwd.setStyleSheet("color: #b8c2c8; font-size: 10px; font-weight: 600; border: none;")
        container_layout.addWidget(lbl_pwd)

        # Custom password input widget to match Figma
        pwd_box = QFrame()
        pwd_box.setStyleSheet("border: 1px solid #364e66; border-radius: 6px; background: #151f29;")
        pwd_box.setFixedHeight(46)
        pwd_layout = QHBoxLayout(pwd_box)
        pwd_layout.setContentsMargins(13, 0, 10, 0)
        pwd_layout.setSpacing(9)

        icon_lock = QLabel(qta.charmap('ph.lock'))
        icon_lock.setFont(qta.font('ph', 13))
        icon_lock.setStyleSheet("color: #8295a7; border: none; background: transparent;")

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Enter master password")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setStyleSheet("border: none; background: transparent; color: #ececdd; font-size: 11px;")

        lbl_enter = QLabel("↵")
        lbl_enter.setStyleSheet("border: 1px solid #32485e; border-radius: 3px; color: #66798c; padding: 2px 5px; font-family: 'IBM Plex Mono'; font-size: 9px; background: transparent;")

        self.btn_reveal = QPushButton(qta.charmap('ph.eye'))
        self.btn_reveal.setFont(qta.font('ph', 13))
        self.btn_reveal.setStyleSheet("border: none; background: transparent; color: #8295a7;")
        self.btn_reveal.setCursor(Qt.PointingHandCursor)
        self.btn_reveal.pressed.connect(lambda: self.pwd_input.setEchoMode(QLineEdit.Normal))
        self.btn_reveal.released.connect(lambda: self.pwd_input.setEchoMode(QLineEdit.Password))

        pwd_layout.addWidget(icon_lock)
        pwd_layout.addWidget(self.pwd_input)
        pwd_layout.addWidget(lbl_enter)
        pwd_layout.addWidget(self.btn_reveal)

        container_layout.addWidget(pwd_box)

        # Options row
        opts_layout = QHBoxLayout()
        opts_layout.setContentsMargins(0, 0, 0, 0)

        chk_remember = QLabel("☑ Remember this device")
        chk_remember.setStyleSheet("color: #92a3b2; font-size: 9px; border: none;")

        btn_forgot = QPushButton("Forgot master password?")
        btn_forgot.setObjectName("TextButton")
        btn_forgot.setStyleSheet("font-size: 10px; padding: 0;")

        opts_layout.addWidget(chk_remember)
        opts_layout.addStretch()
        opts_layout.addWidget(btn_forgot)
        container_layout.addLayout(opts_layout)

        # Error Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #c95b6d; font-weight: bold; border: none;")
        self.error_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.error_label)

        # Button
        self.btn_unlock = QPushButton(f"{qta.charmap('ph.lock-open')} Unlock Vault")
        self.btn_unlock.setFont(qta.font('ph', 12))
        self.btn_unlock.setObjectName("PrimaryButton")
        self.btn_unlock.setMinimumHeight(44)
        self.btn_unlock.clicked.connect(self._on_unlock_clicked)

        # Allow hitting Enter to submit
        self.pwd_input.returnPressed.connect(self._on_unlock_clicked)
        container_layout.addWidget(self.btn_unlock)

        # Security Footer
        sec_footer = QLabel(f"{qta.charmap('ph.shield-check')} Your vault is protected with AES-256 encryption.")
        sec_footer.setFont(qta.font('ph', 10))
        sec_footer.setStyleSheet("color: #72869a; margin-top: 20px; border-top: 1px solid #2b4054; padding-top: 20px; font-size: 8.5px;")
        sec_footer.setAlignment(Qt.AlignCenter)

        lbl_status = QLabel("🟢 Vault Offline & Protected")
        lbl_status.setStyleSheet("color: #80aa91; font-weight: bold; font-size: 8px; border: none;")
        lbl_status.setAlignment(Qt.AlignCenter)

        container_layout.addWidget(sec_footer)
        container_layout.addWidget(lbl_status)

        layout.addLayout(top_layout)
        layout.addStretch()
        layout.addWidget(container, 0, Qt.AlignHCenter)
        layout.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'backdrop'):
            self.backdrop.resize(self.size())

    def _on_unlock_clicked(self):
        pwd = self.pwd_input.text()
        if not pwd:
            return

        self.error_label.setText("")
        self.unlock_attempted.emit(pwd)

    def show_error(self, message: str):
        """Display an error message and clear input."""
        self.error_label.setText(message)
        self.pwd_input.clear()
        self.pwd_input.setFocus()

    def clear(self):
        """Clear the input field and error."""
        self.pwd_input.clear()
        self.error_label.setText("")