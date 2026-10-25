"""Main application entry point."""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from answer_dataset import __app_name__, __version__
from answer_dataset.ui.main_window import MainWindow, SplashScreen


def get_logo_path():
    """Get path to logo file."""
    candidates = [
        Path(__file__).parent.parent.parent / "logos" / "Answer_Logo.png",
        Path(__file__).parent / "resources" / "Answer_Logo.png",
        Path.cwd() / "logos" / "Answer_Logo.png",
        Path.cwd() / "Answer_Logo.png",
    ]
    if getattr(sys, 'frozen', False):
        candidates.append(Path(sys.executable).parent / "logos" / "Answer_Logo.png")
        candidates.append(Path(sys.executable).parent / "Answer_Logo.png")
    
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def main():
    """Run the Answer application."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Articipate")
    app.setOrganizationDomain("articipate.com")
    
    logo_path = get_logo_path()
    if logo_path:
        app.setWindowIcon(QIcon(logo_path))
    
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        print(f"{__app_name__} v{__version__} - self-test OK")
        sys.exit(0)
    
    # Show splash animation
    splash = SplashScreen(logo_path)
    splash.exec()
    
    window = MainWindow()
    if logo_path:
        window.setWindowIcon(QIcon(logo_path))
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
