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
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        theme = get_theme()
        if theme == "light":
            self.setStyleSheet("background-color: #f5f5f5;")
        else:
            self.setStyleSheet("background-color: #1e1e1e;")
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.raise_()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        if logo_path and Path(logo_path).exists():
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        else:
            self.label.setText("Answer")
            self.label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        layout.addWidget(self.label)
        
        self.opacity = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(1.0)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_step)
        self.phase = "down"
        self.cycle = 0
        self.timer.start(40)
    
    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        super().resizeEvent(event)
    
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
        self._sidebar_visible = True
        self._splash = None
        
        self.setup_ui()
        self.setup_status_bar()
        self._apply_theme()
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
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
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
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)
        
        # Navigation buttons overlay
        self.nav_widget = QWidget(central)
        self.nav_widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QHBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(16, 0, 16, 16)
        nav_layout.setSpacing(10)
        self.toggle_sidebar_btn = QPushButton()
        sidebar_icon = Path("icons/Answer_Sidebar_Icon.png")
        if not sidebar_icon.exists():
            sidebar_icon = Path("src/answer_dataset/ui/resources/Answer_Sidebar_Icon.png")
        if sidebar_icon.exists():
            self.toggle_sidebar_btn.setIcon(QIcon(str(sidebar_icon)))
            from PySide6.QtCore import QSize
            self.toggle_sidebar_btn.setIconSize(QSize(26, 26))
        else:
            self.toggle_sidebar_btn.setText("☰")
        self.toggle_sidebar_btn.setFixedSize(48, 48)
        self.toggle_sidebar_btn.setToolTip("Toggle Sidebar")
        self.prev_btn = QPushButton("◀  Previous")
        self.next_btn = QPushButton("Next  ▶")
        self.prev_btn.setFixedHeight(48)
        self.next_btn.setFixedHeight(48)
        self.prev_btn.setStyleSheet("color: #000000;")
        self.next_btn.setStyleSheet("color: #000000;")
        self.toggle_sidebar_btn.setStyleSheet("color: #000000;")
        self.prev_btn.clicked.connect(self.go_prev)
        self.next_btn.clicked.connect(self.go_next)
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        nav_layout.addWidget(self.toggle_sidebar_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        self.nav_widget.setGeometry(0, self.height()-90, self.width(), 90)
        self.nav_widget.raise_()
        self.nav_widget.show()
    
    def resizeEvent(self, event):
        if hasattr(self, 'nav_widget'):
            self.nav_widget.setGeometry(0, self.height()-90, self.width(), 90)
        try:
            if hasattr(self, '_splash') and self._splash is not None:
                if not self._splash.isHidden() and hasattr(self._splash, 'isVisible'):
                    self._splash.setGeometry(0, 0, self.width(), self.height())
        except Exception:
            pass
        super().resizeEvent(event)
    
    def toggle_sidebar(self):
        if not hasattr(self, '_sidebar_visible'):
            self._sidebar_visible = True
        if self._sidebar_visible:
            self.sidebar.hide()
            self._sidebar_visible = False
        else:
            self.sidebar.show()
            self._sidebar_visible = True
    
    def go_prev(self):
        idx = self.stack.currentIndex()
        if idx > 0:
            self.stack.setCurrentIndex(idx - 1)
            self.sidebar.setCurrentRow(idx - 1)
    
    def go_next(self):
        idx = self.stack.currentIndex()
        if idx < self.stack.count() - 1:
            self.stack.setCurrentIndex(idx + 1)
            self.sidebar.setCurrentRow(idx + 1)
    
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
    
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
