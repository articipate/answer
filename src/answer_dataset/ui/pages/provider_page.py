"""Provider configuration page."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QLineEdit, QPushButton, QFormLayout,
                               QGroupBox, QListWidget, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal

from answer_dataset.providers.registry import get_provider
from answer_dataset.security.keyring_store import keyring_store
import asyncio


class ProviderPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Provider Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Provider selection
        provider_group = QGroupBox("AI Provider")
        provider_layout = QFormLayout(provider_group)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Google Gemini", "Ollama", "OpenRouter"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addRow("Provider:", self.provider_combo)
        
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("Leave empty for default")
        provider_layout.addRow("Base URL:", self.base_url_edit)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter API key")
        provider_layout.addRow("API Key:", self.api_key_edit)
        
        layout.addWidget(provider_group)
        
        # Model selection
        model_group = QGroupBox("Model")
        model_layout = QVBoxLayout(model_group)
        
        model_form = QHBoxLayout()
        model_form.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        model_form.addWidget(self.model_combo)
        self.refresh_btn = QPushButton("Refresh Models")
        self.refresh_btn.clicked.connect(self.refresh_models)
        model_form.addWidget(self.refresh_btn)
        model_layout.addLayout(model_form)
        
        layout.addWidget(model_group)
        
        # Test connection
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        layout.addLayout(test_layout)
        
        layout.addStretch()
        
        # Load saved key
        self.on_provider_changed()
    
    def on_provider_changed(self):
        provider_map = {
            "OpenAI": ("openai", ""),
            "Anthropic": ("anthropic", "https://api.anthropic.com/v1"),
            "Google Gemini": ("gemini", "https://generativelanguage.googleapis.com/v1beta"),
            "Ollama": ("ollama", "http://localhost:11434/v1"),
            "OpenRouter": ("openrouter", "https://openrouter.ai/api/v1"),
        }
        name, default_url = provider_map[self.provider_combo.currentText()]
        self.base_url_edit.clear()
        self.base_url_edit.setText(default_url)
        self.model_combo.clear()
        
        # Load API key from keyring
        key = keyring_store.get_key(name)
        if key:
            self.api_key_edit.setText(key)
        else:
            self.api_key_edit.clear()
    
    def refresh_models(self):
        provider_map = {
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "Google Gemini": "gemini",
            "Ollama": "ollama",
            "OpenRouter": "openrouter",
        }
        name = provider_map[self.provider_combo.currentText()]
        
        # Save key if provided
        if self.api_key_edit.text():
            keyring_store.save_key(name, self.api_key_edit.text())
        
        provider = get_provider(
            name,
            api_key=self.api_key_edit.text(),
            base_url=self.base_url_edit.text() or "",
        )
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            models = loop.run_until_complete(provider.list_models())
            loop.close()
            
            self.model_combo.clear()
            if not models:
                QMessageBox.warning(self, "Warning", "No models found. You can enter model name manually.")
                return
            for m in models:
                self.model_combo.addItem(m.name, m.id)
            QMessageBox.information(self, "Success", f"Loaded {len(models)} models")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to fetch models: {e}")
    
    def test_connection(self):
        provider_map = {
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "Google Gemini": "gemini",
            "Ollama": "ollama",
            "OpenRouter": "openrouter",
        }
        name = provider_map[self.provider_combo.currentText()]
        
        api_key = self.api_key_edit.text()
        if name != "ollama" and not api_key:
            QMessageBox.warning(self, "Warning", "API key is required for this provider")
            return
        
        if api_key:
            keyring_store.save_key(name, api_key)
        
        provider = get_provider(
            name,
            api_key=api_key,
            base_url=self.base_url_edit.text() or "",
        )
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(provider.test_connection())
            loop.close()
            
            if success:
                QMessageBox.information(self, "Success", "Connection successful!")
            else:
                QMessageBox.warning(self, "Failed", "Connection failed. Check your API key and settings.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Connection error: {e}")
    
    def get_config(self):
        provider_map = {
            "OpenAI": "openai",
            "Anthropic": "anthropic",
            "Google Gemini": "gemini",
            "Ollama": "ollama",
            "OpenRouter": "openrouter",
        }
        from answer_dataset.models import ProviderConfig, ProviderType
        return ProviderConfig(
            provider_type=ProviderType(provider_map[self.provider_combo.currentText()]),
            api_key=self.api_key_edit.text(),
            base_url=self.base_url_edit.text() or None,
            model=self.model_combo.currentData() or self.model_combo.currentText(),
        )
