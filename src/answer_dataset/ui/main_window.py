"""Main window."""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem, QStackedWidget,
                               QLabel, QPushButton, QStatusBar, QDialog,
                               QGraphicsOpacityEffect, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from pathlib import Path
import sys

from answer_dataset import __app_name__, __version__
from answer_dataset.ui.pages.provider_page import ProviderPage
from answer_dataset.ui.pages.documents_page import DocumentsPage
from answer_dataset.ui.pages.format_page import FormatPage
from answer_dataset.ui.pages.generate_page import GeneratePage
from answer_dataset.ui.theme import apply_theme, get_theme


class SplashOverlay(QWidget):
    def __init__(self, parent, logo_path=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        theme = get_theme()
        if theme == "light":
            self.setStyleSheet("background-color: #f5f5f5;")
        else:
            self.setStyleSheet("background-color: #1e1e1e;")
        self.setGeometry(parent.rect())
        self.raise_()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        if logo_path and Path(logo_path).exists():
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        else:
            self.label.setText("Answer")
            self.label.setStyleSheet("font-size: 28px; font-weight: bold;")
        
        layout.addWidget(self.label)
        
        self.opacity = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(1.0)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_step)
        self.phase = "down"
        self.cycle = 0
        self.timer.start(45)
    
    def animate_step(self):
        if self.phase == "down":
            val = self.opacity.opacity() - 0.09
            if val <= 0.35:
                val = 0.35
                self.phase = "up"
            self.opacity.setOpacity(val)
        else:
            val = self.opacity.opacity() + 0.09
            if val >= 1.0:
                val = 1.0
                self.cycle += 1
                if self.cycle >= 6:
                    self.timer.stop()
                    self.close()
                    self.deleteLater()
                    return
                self.phase = "down"
            self.opacity.setOpacity(val)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{__app_name__} {__version__}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self._logo_path = self._get_logo_path()
        self._set_icon()
        
        self.setup_ui()
        self.setup_status_bar()
        self._apply_theme()
        # Show splash animation on main window
        QTimer.singleShot(50, self.show_splash_overlay)
    def _get_logo_path(self):
        candidates = [
            Path(__file__).parent.parent.parent.parent / "logos" / "Answer_Logo.png",
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
    
    def _set_icon(self):
        if self._logo_path:
            self.setWindowIcon(QIcon(self._logo_path))
    
    def _apply_theme(self):
        theme = get_theme()
        apply_theme(self, theme)
        if hasattr(self, 'theme_btn'):
            self.theme_btn.setText("☀️ Light Mode" if theme == "dark" else "🌙 Dark Mode")
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        
        items = ["1. Provider", "2. Documents", "3. Format", "4. Generate"]
        for item in items:
            self.sidebar.addItem(item)
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.switch_page)
        
        # Pages
        self.stack = QStackedWidget()
        self.provider_page = ProviderPage()
        self.documents_page = DocumentsPage()
        self.format_page = FormatPage()
        self.generate_page = GeneratePage()
        
        self.stack.addWidget(self.provider_page)
        self.stack.addWidget(self.documents_page)
        self.stack.addWidget(self.format_page)
        self.stack.addWidget(self.generate_page)
        
        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)
    
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.status_bar.addPermanentWidget(self.theme_btn)
    
    def toggle_theme(self):
        from answer_dataset.ui.theme import toggle_theme
        theme = toggle_theme()
        apply_theme(self, theme)
        self.theme_btn.setText("☀️ Light Mode" if theme == "dark" else "🌙 Dark Mode")
    
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
    
    def update_status(self, message: str):
        self.status_label.setText(message)
    
    def show_splash(self):
        splash = SplashOverlay(self, self._logo_path)
        splash.show()
        splash.raise_()
    
    def show_splash_overlay(self):
        self._splash = SplashOverlay(self, self._logo_path)
        self._splash.show()
        self._splash.raise_()
        self._splash.activateWindow()
