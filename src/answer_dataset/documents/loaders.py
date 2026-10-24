"""Document loaders."""

import os
from pathlib import Path
from typing import Tuple

from pypdf import PdfReader
from docx import Document as DocxDocument


class DocumentLoader:
    @staticmethod
    def load(path: str) -> Tuple[str, str]:
        """Load document and return (text, error)."""
        ext = Path(path).suffix.lower()
        try:
            if ext == ".pdf":
                return DocumentLoader._load_pdf(path), ""
            elif ext == ".docx":
                return DocumentLoader._load_docx(path), ""
            elif ext in (".txt", ".md"):
                return DocumentLoader._load_text(path), ""
            else:
                return "", f"Unsupported file type: {ext}"
        except Exception as e:
            return "", str(e)
    
    @staticmethod
    def _load_pdf(path: str) -> str:
        reader = PdfReader(path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _load_docx(path: str) -> str:
        doc = DocxDocument(path)
        parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text)
        return "\n\n".join(parts)
    
    @staticmethod
    def _load_text(path: str) -> str:
        # Try UTF-8 first, then latin-1
        for encoding in ["utf-8", "utf-8-sig", "latin-1"]:
            try:
                return Path(path).read_text(encoding=encoding)
            except UnicodeError:
                continue
        return ""
    
    @staticmethod
    def is_supported(path: str) -> bool:
        ext = Path(path).suffix.lower()
        return ext in (".pdf", ".docx", ".txt", ".md")
