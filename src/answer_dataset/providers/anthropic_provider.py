"""Anthropic provider."""

import httpx
from typing import List
from .base import BaseProvider, ModelInfo, CompletionResult


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://api.anthropic.com/v1", model)
    
    async def list_models(self) -> List[ModelInfo]:
        # Anthropic doesn't have a simple models list endpoint in same format
        return [
            ModelInfo(id="claude-sonnet-4-5", name="Claude Sonnet 4.5"),
            ModelInfo(id="claude-haiku-4-5", name="Claude Haiku 4.5"),
            ModelInfo(id="claude-opus-4-1", name="Claude Opus 4.1"),
        ]
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
    async def complete(self, system_prompt: str, user_prompt: str,
                       temperature: float = 0.7, max_tokens: int = 2048) -> CompletionResult:
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-27",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model or "claude-sonnet-4-5",
                        "max_tokens": max_tokens,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": user_prompt}],
                        "temperature": temperature,
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                text = data["content"][0]["text"]
                usage = data.get("usage", {})
                return CompletionResult(
                    text=text,
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                )
        except Exception as e:
            return CompletionResult(text="", error=str(e))
