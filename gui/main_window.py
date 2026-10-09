"""Main window using QWebEngineView for modern WebEngine Desktop Architecture."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QUrl

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.bridge import VaultBridge

class MainWindow(QMainWindow):
    """Main application window using QWebEngineView."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LockByte - Private Password Manager")
        self.setMinimumSize(1024, 700)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create WebEngineView
        self.web_view = QWebEngineView()

        class WebPage(self.web_view.page().__class__):
            def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
                print(f"JS Console [{level}]: {message} (line {lineNumber})")

        self.web_page = WebPage()
        self.web_view.setPage(self.web_page)

        layout.addWidget(self.web_view)

        # Create Bridge and WebChannel
        self.bridge = VaultBridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject("pybridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Path to dist/index.html
        dist_path = Path(__file__).parent.parent / "LockByte Password Manager Design" / "dist" / "index.html"
        self.web_view.load(QUrl.fromLocalFile(str(dist_path.resolve())))
