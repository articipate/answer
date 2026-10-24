"""Main application entry point."""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from answer_dataset import __app_name__, __version__
from answer_dataset.ui.main_window import MainWindow


def main():
    """Run the Answer application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Articipate")
    app.setOrganizationDomain("articipate.com")
    
    # Handle self-test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        print(f"{__app_name__} v{__version__} - self-test OK")
        sys.exit(0)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
