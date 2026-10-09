"""Visual Password Generator View."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QCheckBox, QFrame, QGridLayout, QApplication
)
from PySide6.QtCore import Qt, QTimer, Signal
import sys
from pathlib import Path
import qtawesome as qta

sys.path.insert(0, str(Path(__file__).parent.parent))
from security.password_generator import PasswordGenerator
from .components import PageHeader

class GeneratorView(QWidget):
    """View for generating secure passwords."""

    # Emits the generated password string
    save_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._generate_password()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = PageHeader("Password Generator", "Create strong, unique credentials")
        layout.addWidget(self.header)

        # Body Container
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(38, 28, 38, 40)

        # Card
        card = QFrame()
        card.setProperty("class", "ContentSurface")
        card.setObjectName("ContentSurface")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(31, 29, 31, 31)

        # --- Card Header ---
        header_layout = QHBoxLayout()
        icon_lbl = QLabel(qta.charmap('ph.magic-wand'))
        icon_lbl.setFont(qta.font('ph', 22))
        icon_lbl.setStyleSheet("color: #c51f5d; border: 1px solid #3e5973; border-radius: 7px; background: #223343; padding: 8px;")
        icon_lbl.setFixedSize(42, 42)
        icon_lbl.setAlignment(Qt.AlignCenter)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        lbl_title = QLabel("Generate a secure password")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 2px;")
        lbl_desc = QLabel("Passwords are generated locally and never leave your device.")
        lbl_desc.setStyleSheet("color: #8295a7; font-size: 9px;")
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_desc)

        header_layout.addWidget(icon_lbl)
        header_layout.addSpacing(10)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        card_layout.addSpacing(27)

        # --- Password Display Box ---
        pwd_box = QFrame()
        pwd_box.setStyleSheet("border: 1px solid #45617b; border-radius: 7px; background: #17232e;")
        pwd_box.setFixedHeight(78)
        pwd_layout = QHBoxLayout(pwd_box)
        pwd_layout.setContentsMargins(19, 0, 19, 0)

        self.lbl_password = QLabel()
        self.lbl_password.setStyleSheet("color: #e2e2d2; font-family: 'IBM Plex Mono', monospace; font-size: 22px; font-weight: 500; border: none; background: transparent;")

        self.btn_copy = QPushButton(qta.charmap('ph.copy'))
        self.btn_copy.setFont(qta.font('ph', 16))
        self.btn_copy.setFixedSize(34, 34)
        self.btn_copy.setStyleSheet("QPushButton { border: 1px solid #385169; border-radius: 5px; background: #213140; color: #a1b0bb; } QPushButton:hover { border-color: #e2e2d2; color: #e2e2d2; }")
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

        btn_regen = QPushButton(qta.charmap('ph.arrows-clockwise'))
        btn_regen.setFont(qta.font('ph', 16))
        btn_regen.setFixedSize(34, 34)
        btn_regen.setStyleSheet("QPushButton { border: 1px solid #385169; border-radius: 5px; background: #213140; color: #a1b0bb; } QPushButton:hover { border-color: #e2e2d2; color: #e2e2d2; }")
        btn_regen.clicked.connect(self._generate_password)

        pwd_layout.addWidget(self.lbl_password)
        pwd_layout.addStretch()
        pwd_layout.addWidget(self.btn_copy)
        pwd_layout.addSpacing(6)
        pwd_layout.addWidget(btn_regen)

        card_layout.addWidget(pwd_box)
        card_layout.addSpacing(10)

        # --- Strength Row ---
        strength_layout = QHBoxLayout()
        self.lbl_strength_text = QLabel("🟢 Very Strong")
        self.lbl_strength_text.setStyleSheet("color: #80aa91; font-size: 8px; font-weight: bold;")

        bars_layout = QHBoxLayout()
        bars_layout.setSpacing(3)
        self.strength_bars = []
        for i in range(4):
            bar = QFrame()
            bar.setFixedSize(38, 2)
            bar.setStyleSheet("background: #80aa91; border-radius: 1px;")
            bars_layout.addWidget(bar)
            self.strength_bars.append(bar)

        strength_layout.addWidget(self.lbl_strength_text)
        strength_layout.addStretch()
        strength_layout.addLayout(bars_layout)
        card_layout.addLayout(strength_layout)

        # --- Divider ---
        card_layout.addSpacing(20)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #32485e;")
        card_layout.addWidget(line)
        card_layout.addSpacing(25)

        # --- Controls Row ---
        controls_layout = QHBoxLayout()

        # Left: Length
        len_layout = QVBoxLayout()
        len_header = QHBoxLayout()
        lbl_len_title = QLabel("Password length")
        lbl_len_title.setStyleSheet("color: #b8c2c8; font-size: 9px; font-weight: bold;")

        self.lbl_len_val = QLabel("20")
        self.lbl_len_val.setFixedSize(33, 26)
        self.lbl_len_val.setAlignment(Qt.AlignCenter)
        self.lbl_len_val.setStyleSheet("border: 1px solid #3a546d; border-radius: 4px; background: #20303f; color: #e2e2d2; font-family: 'IBM Plex Mono'; font-size: 10px; font-weight: bold;")

        len_header.addWidget(lbl_len_title)
        len_header.addStretch()
        len_header.addWidget(self.lbl_len_val)

        self.slider_length = QSlider(Qt.Horizontal)
        self.slider_length.setMinimum(8)
        self.slider_length.setMaximum(32)
        self.slider_length.setValue(20)
        self.slider_length.valueChanged.connect(self._on_length_changed)

        len_footer = QHBoxLayout()
        lbl_min = QLabel("8")
        lbl_min.setStyleSheet("color: #66798c; font-family: 'IBM Plex Mono'; font-size: 8px;")
        lbl_max = QLabel("32")
        lbl_max.setStyleSheet("color: #66798c; font-family: 'IBM Plex Mono'; font-size: 8px;")
        len_footer.addWidget(lbl_min)
        len_footer.addStretch()
        len_footer.addWidget(lbl_max)

        len_layout.addLayout(len_header)
        len_layout.addSpacing(10)
        len_layout.addWidget(self.slider_length)
        len_layout.addSpacing(2)
        len_layout.addLayout(len_footer)

        # Right: Options
        opts_layout = QGridLayout()
        opts_layout.setSpacing(12)

        self.chk_upper = QCheckBox("Uppercase")
        self.chk_lower = QCheckBox("Lowercase")
        self.chk_digits = QCheckBox("Numbers")
        self.chk_symbols = QCheckBox("Symbols")

        for chk in [self.chk_upper, self.chk_lower, self.chk_digits, self.chk_symbols]:
            chk.setChecked(True)
            chk.stateChanged.connect(self._generate_password)

        opts_layout.addWidget(self.chk_upper, 0, 0)
        opts_layout.addWidget(self.chk_lower, 0, 1)
        opts_layout.addWidget(self.chk_digits, 1, 0)
        opts_layout.addWidget(self.chk_symbols, 1, 1)

        controls_layout.addLayout(len_layout, 1)
        controls_layout.addSpacing(43)
        controls_layout.addLayout(opts_layout, 1)

        card_layout.addLayout(controls_layout)
        card_layout.addSpacing(28)

        # --- Save to Vault Button ---
        btn_save = QPushButton(f"{qta.charmap('ph.plus')} Save to Vault")
        btn_save.setFont(qta.font('ph', 12))
        btn_save.setObjectName("PrimaryButton")
        btn_save.setFixedWidth(140)
        btn_save.clicked.connect(lambda: self.save_requested.emit(self.lbl_password.text()))
        card_layout.addWidget(btn_save)

        body_layout.addWidget(card)

        # --- Footer Note ---
        footer_layout = QHBoxLayout()
        icon_shield = QLabel(qta.charmap('ph.shield-check'))
        icon_shield.setFont(qta.font('ph', 17))
        icon_shield.setStyleSheet("color: #80aa91;")

        note_text_layout = QVBoxLayout()
        note_text_layout.setSpacing(3)
        lbl_n1 = QLabel("Local generation")
        lbl_n1.setStyleSheet("color: #aab8c1; font-size: 9px; font-weight: bold;")
        lbl_n2 = QLabel("Cryptographically secure randomness is used directly on this device.")
        lbl_n2.setStyleSheet("color: #66798c; font-size: 8px;")
        note_text_layout.addWidget(lbl_n1)
        note_text_layout.addWidget(lbl_n2)

        footer_layout.addWidget(icon_shield)
        footer_layout.addSpacing(9)
        footer_layout.addLayout(note_text_layout)
        footer_layout.addStretch()

        body_layout.addSpacing(13)
        body_layout.addLayout(footer_layout)
        body_layout.addStretch()

        layout.addWidget(body_widget)

    def _on_length_changed(self, value: int):
        self.lbl_len_val.setText(str(value))
        self._generate_password()

    def _generate_password(self):
        # Ensure at least one option is checked
        if not (self.chk_upper.isChecked() or self.chk_lower.isChecked() or
                self.chk_digits.isChecked() or self.chk_symbols.isChecked()):
            self.chk_lower.setChecked(True) # Force lowercase if user unchecks all

        try:
            password = PasswordGenerator.generate(
                length=self.slider_length.value(),
                include_uppercase=self.chk_upper.isChecked(),
                include_lowercase=self.chk_lower.isChecked(),
                include_digits=self.chk_digits.isChecked(),
                include_symbols=self.chk_symbols.isChecked(),
                min_uppercase=1 if self.chk_upper.isChecked() else 0,
                min_lowercase=1 if self.chk_lower.isChecked() else 0,
                min_digits=1 if self.chk_digits.isChecked() else 0,
                min_symbols=1 if self.chk_symbols.isChecked() else 0
            )
            self.lbl_password.setText(password)

            # Analyze strength
            strength_data = PasswordGenerator.estimate_strength(password)
            strength_str = strength_data['strength'].replace('_', ' ').title()

            # Update UI
            self._update_strength_ui(strength_str)

        except Exception as e:
            self.lbl_password.setText("Error")

    def _update_strength_ui(self, strength_str: str):
        color = "#FF5252" # Red
        bars = 1
        icon = "🔴"

        if "Very Strong" in strength_str:
            color = "#80aa91" # Green
            bars = 4
            icon = "🟢"
        elif "Strong" in strength_str:
            color = "#80aa91"
            bars = 3
            icon = "🟢"
        elif "Good" in strength_str or "Fair" in strength_str:
            color = "#FFC107" # Yellow
            bars = 2
            icon = "🟡"

        self.lbl_strength_text.setText(f"{icon} {strength_str}")
        self.lbl_strength_text.setStyleSheet(f"color: {color}; font-size: 8px; font-weight: bold;")

        for i, bar in enumerate(self.strength_bars):
            if i < bars:
                bar.setStyleSheet(f"background: {color}; border-radius: 1px;")
            else:
                bar.setStyleSheet("background: #364e66; border-radius: 1px;")

    def _copy_to_clipboard(self):
        password = self.lbl_password.text()
        if password and not password.startswith("Error"):
            clipboard = QApplication.clipboard()
            clipboard.setText(password)

            self.btn_copy.setText(qta.charmap('ph.check'))

            original_text = qta.charmap('ph.copy')
            QTimer.singleShot(2000, lambda: self.btn_copy.setText(original_text))