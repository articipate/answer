"""Format configuration page."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QSpinBox, QTextEdit, QGroupBox,
                               QFormLayout, QCheckBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
import json

from answer_dataset.models import GenerationConfig, GenerationMode
from answer_dataset.pipeline.schema import SchemaHandler


class FormatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Dataset Format")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Generation mode
        mode_group = QGroupBox("Generation Mode")
        mode_layout = QFormLayout(mode_group)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Per Document", "Per Chunk", "Multiple per Chunk"])
        mode_layout.addRow("Mode:", self.mode_combo)
        
        self.rows_per_chunk_spin = QSpinBox()
        self.rows_per_chunk_spin.setRange(1, 20)
        self.rows_per_chunk_spin.setValue(3)
        mode_layout.addRow("Rows per chunk:", self.rows_per_chunk_spin)
        
        layout.addWidget(mode_group)
        
        # Format definition
        format_group = QGroupBox("Format Definition")
        format_layout = QVBoxLayout(format_group)
        
        format_layout.addWidget(QLabel("Example JSON Row (or describe the format):"))
        self.example_edit = QTextEdit()
        self.example_edit.setPlaceholderText('{"question": "...", "answer": "..."}')
        self.example_edit.setMaximumHeight(150)
        format_layout.addWidget(self.example_edit)
        
        format_layout.addWidget(QLabel("Additional Instructions:"))
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setPlaceholderText("Any additional instructions for the AI...")
        self.instructions_edit.setMaximumHeight(100)
        format_layout.addWidget(self.instructions_edit)
        
        validate_layout = QHBoxLayout()
        self.validate_btn = QPushButton("Validate Format")
        self.validate_btn.clicked.connect(self.validate_format)
        validate_layout.addWidget(self.validate_btn)
        validate_layout.addStretch()
        format_layout.addLayout(validate_layout)
        
        layout.addWidget(format_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QFormLayout(options_group)
        
        self.add_source_check = QCheckBox()
        self.add_source_check.setChecked(True)
        options_layout.addRow("Add source info:", self.add_source_check)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Auto", "English", "Turkish"])
        options_layout.addRow("Language:", self.language_combo)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
    
    def validate_format(self):
        text = self.example_edit.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Info", "Please provide an example row or format description.")
            return
        
        valid, error, data = SchemaHandler.validate_format(text)
        if valid and data:
            schema = SchemaHandler.infer_schema(data)
            QMessageBox.information(self, "Valid", f"Format is valid!\nInferred schema for {len(schema.get('properties', {}))} fields.")
        elif valid:
            QMessageBox.information(self, "Valid", "Format description is acceptable.")
        else:
            QMessageBox.warning(self, "Invalid", f"Format validation failed:\n{error}")
    
    def get_config(self) -> GenerationConfig:
        mode_map = {
            "Per Document": GenerationMode.PER_DOCUMENT,
            "Per Chunk": GenerationMode.PER_CHUNK,
            "Multiple per Chunk": GenerationMode.MULTI_PER_CHUNK,
        }
        
        example_row = None
        text = self.example_edit.toPlainText().strip()
        if text:
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    example_row = data
                elif isinstance(data, list) and data and isinstance(data[0], dict):
                    example_row = data[0]
            except:
                pass
        
        return GenerationConfig(
            mode=mode_map[self.mode_combo.currentText()],
            rows_per_chunk=self.rows_per_chunk_spin.value(),
            system_prompt=self.instructions_edit.toPlainText(),
            example_row=example_row,
            add_source=self.add_source_check.isChecked(),
            language=self.language_combo.currentText().lower(),
        )
