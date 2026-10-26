"""Theme management for Answer app."""

from PySide6.QtWidgets import QApplication
import json
from pathlib import Path
from platformdirs import user_config_dir
from answer_dataset.ui.color_utils import BUTTON_COLOR, BUTTON_HOVER, BUTTON_PRESSED

CONFIG_DIR = Path(user_config_dir("Answer", "Articipate"))
CONFIG_FILE = CONFIG_DIR / "theme.json"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

DARK_THEME = f"""
QMainWindow {{
    background-color: #1e1e1e;
    color: #e0e0e0;
}}
QWidget {{
    background-color: #1e1e1e;
    color: #e0e0e0;
}}
QListWidget {{
    background-color: #252526;
    color: #e0e0e0;
    border: none;
    padding: 10px;
}}
QListWidgetItem {{
    padding: 12px;
    border-radius: 6px;
}}
QListWidgetItem:selected {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
}}
QListWidgetItem:hover {{
    background-color: #2d2d30;
}}
QGroupBox {{
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}}
QPushButton {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: {BUTTON_HOVER};
}}
QPushButton:pressed {{
    background-color: {BUTTON_PRESSED};
}}
QPushButton:disabled {{
    background-color: #3c3c3c;
    color: #6c6c6c;
}}
QLineEdit, QTextEdit, QComboBox, QSpinBox {{
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1px solid {BUTTON_COLOR};
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: #2d2d30;
    color: #e0e0e0;
    selection-background-color: {BUTTON_COLOR};
}}
QTableWidget {{
    background-color: #252526;
    color: #e0e0e0;
    gridline-color: #3c3c3c;
    border: 1px solid #3c3c3c;
}}
QTableWidget::item {{
    padding: 4px;
}}
QTableWidget::item:selected {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
}}
QHeaderView::section {{
    background-color: #2d2d30;
    color: #e0e0e0;
    padding: 6px;
    border: none;
    border-right: 1px solid #3c3c3c;
}}
QTabWidget::pane {{
    border: 1px solid #3c3c3c;
    background-color: #252526;
}}
QTabBar::tab {{
    background-color: #2d2d30;
    color: #e0e0e0;
    padding: 8px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
}}
QProgressBar {{
    background-color: #2d2d30;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {BUTTON_COLOR};
}}
QStatusBar {{
    background-color: #252526;
    color: #e0e0e0;
}}
QLabel {{
    color: #e0e0e0;
}}
"""

LIGHT_THEME = f"""
QMainWindow {{
    background-color: #f5f5f5;
    color: #1e1e1e;
}}
QWidget {{
    background-color: #f5f5f5;
    color: #1e1e1e;
}}
QListWidget {{
    background-color: #ffffff;
    color: #1e1e1e;
    border: 1px solid #d0d0d0;
    padding: 10px;
}}
QListWidgetItem {{
    padding: 12px;
    border-radius: 6px;
}}
QListWidgetItem:selected {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
}}
QListWidgetItem:hover {{
    background-color: #e9ecef;
}}
QGroupBox {{
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}}
QPushButton {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: {BUTTON_HOVER};
}}
QPushButton:pressed {{
    background-color: {BUTTON_PRESSED};
}}
QPushButton:disabled {{
    background-color: #e9ecef;
    color: #6c757d;
}}
QLineEdit, QTextEdit, QComboBox, QSpinBox {{
    background-color: #ffffff;
    color: #1e1e1e;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 6px;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1px solid {BUTTON_COLOR};
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #1e1e1e;
    selection-background-color: {BUTTON_COLOR};
    selection-color: #ffffff;
}}
QTableWidget {{
    background-color: #ffffff;
    color: #1e1e1e;
    gridline-color: #dee2e6;
    border: 1px solid #d0d0d0;
}}
QTableWidget::item {{
    padding: 4px;
}}
QTableWidget::item:selected {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
}}
QHeaderView::section {{
    background-color: #f8f9fa;
    color: #1e1e1e;
    padding: 6px;
    border: none;
    border-right: 1px solid #dee2e6;
}}
QTabWidget::pane {{
    border: 1px solid #d0d0d0;
    background-color: #ffffff;
}}
QTabBar::tab {{
    background-color: #e9ecef;
    color: #1e1e1e;
    padding: 8px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {BUTTON_COLOR};
    color: #ffffff;
}}
QProgressBar {{
    background-color: #e9ecef;
    border: 1px solid #ced4da;
    border-radius: 4px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {BUTTON_COLOR};
}}
QStatusBar {{
    background-color: #ffffff;
    color: #1e1e1e;
    border-top: 1px solid #d0d0d0;
}}
QLabel {{
    color: #1e1e1e;
}}
"""


def get_theme():
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            theme = data.get("theme", "dark")
            if theme in ("dark", "light"):
                return theme
    except Exception:
        pass
    return "dark"


def set_theme(theme):
    try:
        CONFIG_FILE.write_text(json.dumps({"theme": theme}, indent=2), encoding="utf-8")
    except Exception:
        pass


def apply_theme(widget, theme=None):
    if theme is None:
        theme = get_theme()
    app = QApplication.instance()
    if app:
        if theme == "light":
            app.setStyleSheet(LIGHT_THEME)
        else:
            app.setStyleSheet(DARK_THEME)


def toggle_theme():
    current = get_theme()
    new_theme = "light" if current == "dark" else "dark"
    set_theme(new_theme)
    return new_theme
