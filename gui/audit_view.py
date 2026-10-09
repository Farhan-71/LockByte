"""Security Audit Dashboard View."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QThread, Signal
from typing import Optional
import sys
from pathlib import Path
import qtawesome as qta

sys.path.insert(0, str(Path(__file__).parent.parent))
from vault.repository import VaultRepository
from security.audit import SecurityAuditEngine, SecurityAuditResult
from security.breach_check import PrivacyAwareBreachCheck
from gui.components import PageHeader, ScoreRing

class AuditWorker(QThread):
    """Background thread to run the security audit without freezing the GUI."""

    finished_audit = Signal(object) # Emits SecurityAuditResult
    progress_update = Signal(str, int) # Emits status text and percentage

    def __init__(self, vault: VaultRepository):
        super().__init__()
        self.vault = vault

    def run(self):
        try:
            self.progress_update.emit("Fetching credentials...", 10)
            credentials = self.vault.list_credentials()

            if not credentials:
                self.progress_update.emit("No credentials to audit.", 100)
                self.finished_audit.emit(None)
                return

            self.progress_update.emit("Checking for exposed passwords (this may take a moment)...", 30)

            # Run breach check on unique passwords to save network calls
            exposed_credentials = set()
            unique_passwords = {c.password: [] for c in credentials}
            for c in credentials:
                unique_passwords[c.password].append(c.id)

            breach_checker = PrivacyAwareBreachCheck()
            total_unique = len(unique_passwords)

            for i, (pwd, ids) in enumerate(unique_passwords.items()):
                self.progress_update.emit(f"Checking password {i+1} of {total_unique} against HaveIBeenPwned...", 30 + int((i/total_unique)*40))
                try:
                    is_exposed, _ = breach_checker.checker.check_password(pwd)
                    if is_exposed:
                        for cid in ids:
                            exposed_credentials.add(cid)
                except Exception:
                    pass # Silently fail network issues for individual checks

            self.progress_update.emit("Analyzing password strength and reuse...", 80)

            engine = SecurityAuditEngine()
            result = engine.audit_credentials(credentials, exposed_credentials)

            self.progress_update.emit("Audit complete!", 100)
            self.finished_audit.emit(result)

        except Exception as e:
            self.progress_update.emit(f"Error during audit: {str(e)}", 0)
            self.finished_audit.emit(None)

class AuditView(QWidget):
    """View displaying security audit results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vault: Optional[VaultRepository] = None
        self.worker: Optional[AuditWorker] = None
        self._init_ui()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Header
        self.header = PageHeader("Security Audit", "Monitor the strength of your digital security")
        self.layout.addWidget(self.header)

        # Body
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(38, 28, 38, 40)

        # Top Card (Score Card)
        self.score_card = QFrame()
        self.score_card.setProperty("class", "ContentSurface")
        self.score_card.setObjectName("ContentSurface")
        score_layout = QHBoxLayout(self.score_card)
        score_layout.setContentsMargins(37, 28, 37, 28)
        score_layout.setSpacing(39)

        # Left side: Ring
        self.ring_container = QWidget()
        self.ring_layout = QVBoxLayout(self.ring_container)
        self.ring_layout.setContentsMargins(0,0,0,0)
        self.score_ring = ScoreRing(0) # Default 0
        self.ring_layout.addWidget(self.score_ring)
        score_layout.addWidget(self.ring_container)

        # Right side: Text and Button
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignLeft)

        lbl_eyebrow = QLabel("SECURITY SCORE")
        lbl_eyebrow.setStyleSheet("color: #c51f5d; font-size: 9px; font-weight: 700; letter-spacing: 1.9px;")

        self.lbl_score_title = QLabel("Run Audit to View Score")
        self.lbl_score_title.setStyleSheet("font-size: 21px; font-weight: 600; margin-top: 2px; margin-bottom: 9px;")

        lbl_desc = QLabel("Your vault is well protected. Resolve the remaining recommendations to strengthen your security posture.")
        lbl_desc.setStyleSheet("color: #92a3b2; font-size: 10px; max-width: 510px;")
        lbl_desc.setWordWrap(True)

        btn_layout = QHBoxLayout()
        self.btn_run = QPushButton(f"{qta.charmap('ph.shield-check')} Run Audit")
        self.btn_run.setFont(qta.font('ph', 12))
        self.btn_run.setObjectName("PrimaryButton")
        self.btn_run.setFixedWidth(150)
        self.btn_run.clicked.connect(self._run_audit)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #A0A0A0; font-size: 10px;")

        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.lbl_status)
        btn_layout.addStretch()

        text_layout.addWidget(lbl_eyebrow)
        text_layout.addWidget(self.lbl_score_title)
        text_layout.addWidget(lbl_desc)
        text_layout.addSpacing(18)
        text_layout.addLayout(btn_layout)

        score_layout.addLayout(text_layout)
        score_layout.addStretch()

        body_layout.addWidget(self.score_card)

        # Progress / Loading area (Under the card)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        body_layout.addWidget(self.progress_bar)

        # Results Area (Hidden initially)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)

        # Top Metrics Grid
        self.metrics_layout = QGridLayout()
        self.lbl_weak = self._create_metric_label("Weak Passwords", "-", "ph.warning", "#c6a75f")
        self.lbl_reused = self._create_metric_label("Reused Passwords", "-", "ph.arrows-clockwise", "#c6a75f")
        self.lbl_2fa = self._create_metric_label("Missing 2FA", "-", "ph.key", "#c95b6d")
        self.lbl_exposed = self._create_metric_label("Compromised Credentials", "-", "ph.shield-check", "#80aa91")

        self.metrics_layout.addWidget(self.lbl_weak, 0, 0)
        self.metrics_layout.addWidget(self.lbl_reused, 0, 1)
        self.metrics_layout.addWidget(self.lbl_2fa, 0, 2)
        self.metrics_layout.addWidget(self.lbl_exposed, 0, 3)

        self.results_layout.addLayout(self.metrics_layout)

        # Action Items List
        self.results_layout.addSpacing(10)
        lbl_rec = QLabel("Security recommendations")
        lbl_rec.setStyleSheet("font-size: 12px; font-weight: 600;")
        self.results_layout.addWidget(lbl_rec)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        self.actions_container = QWidget()
        self.actions_layout = QVBoxLayout(self.actions_container)
        self.actions_layout.setContentsMargins(0,0,0,0)
        self.actions_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.actions_container)

        self.results_layout.addWidget(self.scroll_area)

        self.results_widget.hide()
        body_layout.addWidget(self.results_widget)

        self.layout.addWidget(body_widget)

    def _create_metric_label(self, title: str, value: str, icon: str, color: str) -> QFrame:
        """Create a styled metric card."""
        frame = QFrame()
        frame.setProperty("class", "ContentSurface")
        frame.setObjectName("ContentSurface")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(17, 10, 17, 10)

        # Icon box
        icon_box = QLabel(qta.charmap(icon))
        icon_box.setFont(qta.font('ph', 15))
        icon_box.setStyleSheet(f"color: {color}; border: 1px solid #354d64; border-radius: 6px; padding: 8px;")
        icon_box.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        lbl_v = QLabel(value)
        lbl_v.setObjectName("Value")
        lbl_v.setStyleSheet("font-size: 18px; font-weight: 600; border: none; font-family: 'IBM Plex Mono';")

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: #8295a7; font-size: 8px; border: none;")

        text_layout.addWidget(lbl_v)
        text_layout.addWidget(lbl_t)

        layout.addWidget(icon_box)
        layout.addLayout(text_layout)
        layout.addStretch()
        return frame

    def set_vault(self, vault: VaultRepository):
        self.vault = vault

    def _run_audit(self):
        if not self.vault or not self.vault.is_unlocked():
            self.lbl_status.setText("Vault is locked.")
            return

        self.btn_run.setEnabled(False)
        self.results_widget.hide()
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.lbl_status.show()

        self.worker = AuditWorker(self.vault)
        self.worker.progress_update.connect(self._on_progress)
        self.worker.finished_audit.connect(self._on_audit_finished)
        self.worker.start()

    def _on_progress(self, message: str, percent: int):
        self.lbl_status.setText(message)
        self.progress_bar.setValue(percent)

    def _on_audit_finished(self, result: Optional[SecurityAuditResult]):
        self.btn_run.setEnabled(True)
        self.progress_bar.hide()

        if not result:
            # Error or no credentials
            return

        self.lbl_status.hide()
        self.results_widget.show()

        # Update Ring
        self.score_ring.score = result.overall_score
        self.score_ring.update()

        # Update metrics
        score_color = "#FF5252" if result.overall_score < 50 else ("#FFC107" if result.overall_score < 80 else "#4CAF50")

        # Access the child labels inside the frames
        self.lbl_score.findChild(QLabel, "Value").setText(f"{result.overall_score}/100")
        self.lbl_score.findChild(QLabel, "Value").setStyleSheet(f"font-size: 24px; font-weight: bold; border: none; color: {score_color};")

        self.lbl_weak.findChild(QLabel, "Value").setText(str(result.weak_passwords))
        self.lbl_reused.findChild(QLabel, "Value").setText(str(result.reused_passwords))
        self.lbl_2fa.findChild(QLabel, "Value").setText(str(result.missing_2fa))

        exp_color = "#c95b6d" if result.exposed_credentials > 0 else "#80aa91"
        self.lbl_exposed.findChild(QLabel, "Value").setText(str(result.exposed_credentials))
        # Keep icon updated too
        # self.lbl_exposed... (skipped for brevity, but could update color)

        # Update action items
        # Clear old items
        for i in reversed(range(self.actions_layout.count())):
            self.actions_layout.itemAt(i).widget().setParent(None)

        engine = SecurityAuditEngine()
        actions = engine.get_priority_actions(result)

        if not actions:
            lbl = QLabel("No priority actions needed. Great job!")
            lbl.setStyleSheet("color: #4CAF50; font-size: 16px; padding: 20px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.actions_layout.addWidget(lbl)
            return

        for action in actions:
            frame = QFrame()
            frame.setStyleSheet("border-bottom: 1px solid #293c4f; padding: 10px 20px;")

            l = QHBoxLayout(frame)
            l.setContentsMargins(0, 0, 0, 0)

            # Icon
            color = "#c95b6d" if action['priority'] == 'critical' else "#c6a75f"
            icon = QLabel(qta.charmap('ph.shield-warning'))
            icon.setFont(qta.font('ph', 15))
            icon.setStyleSheet(f"color: {color}; border-radius: 5px; background: #243447; padding: 8px;")
            icon.setFixedSize(30, 30)
            icon.setAlignment(Qt.AlignCenter)

            # Text
            t_layout = QVBoxLayout()
            t_layout.setSpacing(3)
            title = QLabel(f"<b>{action['action']}</b>")
            title.setStyleSheet("border: none; font-size: 9.5px; font-weight: 500;")
            desc = QLabel(action['reason'])
            desc.setStyleSheet("color: #8295a7; border: none; font-size: 8px;")
            t_layout.addWidget(title)
            t_layout.addWidget(desc)

            btn = QPushButton("Review")
            btn.setStyleSheet("padding: 5px 9px; border: 1px solid #374f67; border-radius: 4px; background: #1e2d3b; color: #a1b0bb; font-size: 8px;")

            l.addWidget(icon)
            l.addLayout(t_layout)
            l.addStretch()
            l.addWidget(btn)

            self.actions_layout.addWidget(frame)