"""Documents page."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QListWidget, QListWidgetItem,
                               QFileDialog, QMessageBox, QTextEdit, QSplitter)
from PySide6.QtCore import Qt
from pathlib import Path

from answer_dataset.documents.loaders import DocumentLoader
from answer_dataset.documents.chunker import Chunker
from answer_dataset.models import Document, DocumentType


class DocumentsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.documents = []
        self.chunker = Chunker()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Documents")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_files_btn = QPushButton("Add Files...")
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn = QPushButton("Add Folder...")
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.add_files_btn)
        btn_layout.addWidget(self.add_folder_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self.on_selection_changed)
        splitter.addWidget(self.file_list)
        
        # Preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(5, 5, 5, 5)
        preview_label = QLabel("Preview")
        preview_label.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        self.info_label = QLabel("")
        preview_layout.addWidget(self.info_label)
        splitter.addWidget(preview_widget)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
    
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Documents",
            "",
            "Documents (*.pdf *.docx *.txt *.md);;PDF (*.pdf);;Word (*.docx);;Text (*.txt);;Markdown (*.md);;All Files (*.*)"
        )
        for f in files:
            self.add_document(f)
    
    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for ext in ['*.pdf', '*.docx', '*.txt', '*.md']:
                for f in Path(folder).rglob(ext):
                    self.add_document(str(f))
    
    def add_document(self, path: str):
        if not DocumentLoader.is_supported(path):
            return
        # Check if already added
        for doc in self.documents:
            if doc.path == path:
                return
        
        text, error = DocumentLoader.load(path)
        if error:
            QMessageBox.warning(self, "Error", f"Failed to load {Path(path).name}: {error}")
            return
        
        chunks = self.chunker.chunk(text)
        doc_type_map = {'.pdf': DocumentType.PDF, '.docx': DocumentType.DOCX, '.txt': DocumentType.TXT, '.md': DocumentType.MD}
        ext = Path(path).suffix.lower()
        
        doc = Document(
            path=path,
            name=Path(path).name,
            doc_type=doc_type_map.get(ext, DocumentType.TXT),
            text=text,
            chunks=chunks,
            status="loaded"
        )
        self.documents.append(doc)
        
        item = QListWidgetItem(f"{doc.name} ({len(chunks)} chunks, {self.chunker.count_tokens(text)} tokens)")
        item.setData(Qt.UserRole, len(self.documents) - 1)
        self.file_list.addItem(item)
    
    def clear_all(self):
        self.documents = []
        self.file_list.clear()
        self.preview_text.clear()
        self.info_label.clear()
    
    def on_selection_changed(self, current, previous):
        if not current:
            return
        idx = current.data(Qt.UserRole)
        if 0 <= idx < len(self.documents):
            doc = self.documents[idx]
            # Show preview (first 2000 chars)
            preview = doc.text[:2000]
            if len(doc.text) > 2000:
                preview += "\n\n... [truncated]"
            self.preview_text.setPlainText(preview)
            self.info_label.setText(f"Size: {len(doc.text)} chars | Chunks: {len(doc.chunks)} | Tokens: ~{self.chunker.count_tokens(doc.text)}")
    
    def get_documents(self):
        return self.documents
