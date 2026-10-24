"""Data models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


class GenerationMode(Enum):
    PER_DOCUMENT = "per_document"
    PER_CHUNK = "per_chunk"
    MULTI_PER_CHUNK = "multi_per_chunk"


class DocumentType(Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"


@dataclass
class ProviderConfig:
    provider_type: ProviderType
    api_key: str = ""
    base_url: Optional[str] = None
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    max_concurrent: int = 2
    timeout: int = 120


@dataclass
class Document:
    path: str
    name: str
    doc_type: DocumentType
    text: str = ""
    chunks: List[str] = field(default_factory=list)
    status: str = "pending"


@dataclass
class DatasetRow:
    data: Dict[str, Any]
    source: str = ""
    chunk_index: int = -1
    validated: bool = False
    error: Optional[str] = None


@dataclass
class GenerationConfig:
    mode: GenerationMode = GenerationMode.PER_CHUNK
    rows_per_chunk: int = 3
    max_rows: int = 0  # 0 = unlimited
    system_prompt: str = ""
    user_prompt: str = ""
    output_format: str = "json"
    json_schema: Optional[Dict[str, Any]] = None
    example_row: Optional[Dict[str, Any]] = None
    add_source: bool = False
    language: str = "auto"
