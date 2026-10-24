"""Ollama provider."""

import httpx
from typing import List
from .base import BaseProvider, ModelInfo, CompletionResult


class OllamaProvider(BaseProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "http://localhost:11434/v1", model)
    
    async def list_models(self) -> List[ModelInfo]:
        try:
            # Ollama native API
            base = self.base_url.replace("/v1", "")
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{base}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                models = []
                for m in data.get("models", []):
                    name = m["name"]
                    models.append(ModelInfo(id=name, name=name))
                return models
        except Exception:
            return []
    
    async def test_connection(self) -> bool:
        try:
            models = await self.list_models()
            return len(models) > 0
        except Exception:
            return False
    
    async def complete(self, system_prompt: str, user_prompt: str,
                       temperature: float = 0.7, max_tokens: int = 2048) -> CompletionResult:
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False,
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return CompletionResult(
                    text=text,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                )
        except Exception as e:
            return CompletionResult(text="", error=str(e))
