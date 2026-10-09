import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from .main_window import MainWindow
from .styles import DARK_THEME

class LockByteGUIApp:
    """Wrapper class for the PySide6 QApplication."""

    def __init__(self):
        # Create the QApplication instance
        self.app = QApplication(sys.argv)

        # Load Custom Fonts
        font_dir = Path(__file__).parent / "assets" / "fonts"
        for font_file in font_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))

        # Apply the global Dark Mode stylesheet
        self.app.setStyleSheet(DARK_THEME)

        # Initialize and show the main window
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        """Execute the application event loop."""
        sys.exit(self.app.exec())