"""Main window."""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem, QStackedWidget,
                               QLabel, QPushButton, QStatusBar, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from answer_dataset import __app_name__, __version__
from answer_dataset.ui.pages.provider_page import ProviderPage
from answer_dataset.ui.pages.documents_page import DocumentsPage
from answer_dataset.ui.pages.format_page import FormatPage
from answer_dataset.ui.pages.generate_page import GeneratePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{__app_name__} v{__version__}")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self.setup_ui()
        self.setup_status_bar()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                padding: 10px;
            }
            QListWidgetItem {
                padding: 12px;
                border-radius: 6px;
            }
            QListWidgetItem:selected {
                background-color: #0d6efd;
            }
            QListWidgetItem:hover {
                background-color: #3b3b3b;
            }
        """)
        
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
    
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
    
    def update_status(self, message: str):
        self.status_label.setText(message)
