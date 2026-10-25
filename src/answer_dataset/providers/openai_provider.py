"""OpenAI provider."""

import httpx
from typing import List
from .base import BaseProvider, ModelInfo, CompletionResult


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://api.openai.com/v1", model)
    
    async def list_models(self) -> List[ModelInfo]:
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.base_url.rstrip('/')}/models",
                    headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                models = []
                for m in data.get("data", []):
                    model_id = m.get("id") or m.get("name") or ""
                    if model_id:
                        models.append(ModelInfo(id=model_id, name=model_id))
                return sorted(models, key=lambda x: x.id)
        except Exception:
            return []
    
    async def test_connection(self) -> bool:
        try:
            if not self.api_key and "api.openai.com" in (self.base_url or ""):
                return False
            models = await self.list_models()
            return len(models) > 0
        except Exception:
            return False
    
    async def complete(self, system_prompt: str, user_prompt: str,
                       temperature: float = 0.7, max_tokens: int = 2048) -> CompletionResult:
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
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
