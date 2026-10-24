"""Provider registry."""

from typing import Dict, Type
from .base import BaseProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openrouter_provider import OpenRouterProvider


PROVIDERS: Dict[str, Type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
}


def get_provider(name: str, api_key: str = "", base_url: str = "", model: str = "") -> BaseProvider:
    cls = PROVIDERS.get(name, OpenAIProvider)
    return cls(api_key=api_key, base_url=base_url, model=model)
