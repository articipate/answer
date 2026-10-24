"""Base provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModelInfo:
    id: str
    name: str


@dataclass
class CompletionResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None


class BaseProvider(ABC):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        pass
    
    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str, 
                       temperature: float = 0.7, max_tokens: int = 2048) -> CompletionResult:
        pass
