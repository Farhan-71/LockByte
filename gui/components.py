"""Reusable UI components that match the React design system."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen
import qtawesome as qta


class PageHeader(QFrame):
    """The standard page header used across the app."""
    def __init__(self, title: str, subtitle: str):
        super().__init__()
        self.setFixedHeight(92)
        self.setObjectName("PageHeader")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(38, 0, 38, 0)

        # Left side: Title & Subtitle
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("PageTitle")

        lbl_subtitle = QLabel(subtitle)
        lbl_subtitle.setObjectName("PageSubtitle")

        left_layout.addStretch()
        left_layout.addWidget(lbl_title)
        left_layout.addWidget(lbl_subtitle)
        left_layout.addStretch()

        # Right side: Account / Vault Status
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(17)

        lbl_secure = QLabel("🟢 Vault Secure")
        lbl_secure.setObjectName("VaultSecureBadge")

        btn_profile = QPushButton(qta.charmap('ph.user'))
        btn_profile.setFont(qta.font('ph', 16))
        btn_profile.setObjectName("ProfileButton")
        btn_profile.setFixedSize(34, 34)

        right_layout.addWidget(lbl_secure)
        right_layout.addWidget(btn_profile)

        layout.addWidget(left_widget)
        layout.addStretch()
        layout.addWidget(right_widget)


class ScoreRing(QWidget):
    """Custom painted widget for the circular score progress."""
    def __init__(self, score: int, parent=None):
        super().__init__(parent)
        self.score = score
        self.setFixedSize(120, 120)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)

        # Draw background ring
        bg_pen = QPen(QColor("#32485e"))
        bg_pen.setWidth(7)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)

        # Draw score progress
        # 360 degrees * 16 (Qt coordinate system)
        span_angle = int((self.score / 100) * 360 * 16)

        score_color = "#FF5252" if self.score < 50 else ("#FFC107" if self.score < 80 else "#80aa91")
        fg_pen = QPen(QColor(score_color))
        fg_pen.setWidth(7)
        fg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(fg_pen)

        # Start at 90 degrees (12 o'clock in Qt)
        painter.drawArc(rect, 90 * 16, -span_angle)

        # Draw text in center
        painter.setPen(QColor("#e2e2d2"))
        font = painter.font()
        font.setPixelSize(32)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, str(self.score))


class ToggleSwitch(QCheckBox):
    """Custom painted toggle switch matching the React design."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(31, 17)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        checked = self.isChecked()

        # Colors based on CSS design
        bg_color = QColor(197, 31, 93, 56) if checked else QColor("#2a3e51") # rgba(197,31,93,.22)
        border_color = QColor("#8c9eaa") if checked else QColor("#496580")
        thumb_color = QColor("#c51f5d") if checked else QColor("#92a3b2")

        # Draw background pill
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(0, 0, rect.width() - 1, rect.height() - 1, 8, 8)

        # Draw thumb (sliding circle)
        painter.setPen(Qt.NoPen)
        painter.setBrush(thumb_color)

        # Position thumb
        thumb_radius = 4.5
        y_pos = int(rect.height() / 2)
        x_pos = 17 + thumb_radius if checked else 3 + thumb_radius

        painter.drawEllipse(int(x_pos - thumb_radius), int(y_pos - thumb_radius), int(thumb_radius * 2), int(thumb_radius * 2))


class SecurityBackdrop(QWidget):
    """Faint background grid and icons for auth screens."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # Draw grid
        pen = QPen(QColor(197, 31, 93, 8)) # Very faint magenta (approx 3% alpha)
        pen.setWidth(1)
        painter.setPen(pen)

        grid_size = 56
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)

        # Draw ghost icons (approximations based on screenshot)
        painter.setPen(QColor(197, 31, 93, 12)) # ~5% alpha
        font = qta.font('ph', 72)
        painter.setFont(font)

        # Shield (left)
        painter.drawText(int(w * 0.1), int(h * 0.3), qta.charmap('ph.shield-check'))

        # Key (right bottom)
        font.setPixelSize(58)
        painter.setFont(font)
        painter.drawText(int(w * 0.8), int(h * 0.8), qta.charmap('ph.key'))

        # Lock (top right)
        font.setPixelSize(30)
        painter.setFont(font)
        painter.drawText(int(w * 0.75), int(h * 0.2), qta.charmap('ph.lock'))