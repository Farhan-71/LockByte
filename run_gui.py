"""Launcher script for the LockByte Graphical User Interface."""

import sys
from pathlib import Path

# Ensure the root directory is in the Python path
# so relative imports inside /gui work correctly.
sys.path.insert(0, str(Path(__file__).parent))

from gui.app import LockByteGUIApp

def main():
    """Launch the LockByte Desktop Application."""
    app = LockByteGUIApp()
    app.run()

if __name__ == "__main__":
    main()