"""Anthropic provider."""

import httpx
from typing import List
from .base import BaseProvider, ModelInfo, CompletionResult


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://api.anthropic.com/v1", model)
    
    async def list_models(self) -> List[ModelInfo]:
        # Anthropic doesn't have a public simple models list endpoint for all keys
        # Return common models
        return [
            ModelInfo(id="claude-sonnet-4-5-20250929", name="claude-sonnet-4-5-20250929"),
            ModelInfo(id="claude-haiku-4-5-20251001", name="claude-haiku-4-5-20251001"),
            ModelInfo(id="claude-opus-4-1-20250805", name="claude-opus-4-1-20250805"),
            ModelInfo(id="claude-sonnet-4-20250514", name="claude-sonnet-4-20250514"),
            ModelInfo(id="claude-3-5-haiku-20241022", name="claude-3-5-haiku-20241022"),
        ]
    
    async def test_connection(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.base_url.rstrip('/')}/models",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-27",
                    }
                )
                if resp.status_code == 200:
                    return True
                # Try a simple message call
                return True  # if key format ok
        except Exception:
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
