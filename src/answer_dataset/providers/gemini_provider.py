"""Google Gemini provider."""

import httpx
from typing import List
from .base import BaseProvider, ModelInfo, CompletionResult


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://generativelanguage.googleapis.com/v1beta", model)
    
    async def list_models(self) -> List[ModelInfo]:
        try:
            if self.api_key:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(f"{self.base_url.rstrip('/')}/models?key={self.api_key}")
                    if resp.status_code == 200:
                        data = resp.json()
                        models = []
                        for m in data.get("models", []):
                            name = m.get("name", "").replace("models/", "")
                            if name and "gemini" in name.lower():
                                models.append(ModelInfo(id=name, name=name))
                        if models:
                            return sorted(models, key=lambda x: x.id)
        except Exception:
            pass
        return [
            ModelInfo(id="gemini-2.5-flash", name="gemini-2.5-flash"),
            ModelInfo(id="gemini-2.5-pro", name="gemini-2.5-pro"),
            ModelInfo(id="gemini-2.0-flash", name="gemini-2.0-flash"),
            ModelInfo(id="gemini-1.5-pro", name="gemini-1.5-pro"),
        ]
    
    async def test_connection(self) -> bool:
        if not self.api_key:
            return False
        try:
            models = await self.list_models()
            return len(models) > 0
        except Exception:
            return False
    
    async def complete(self, system_prompt: str, user_prompt: str,
                       temperature: float = 0.7, max_tokens: int = 2048) -> CompletionResult:
        try:
            model = self.model or "gemini-2.5-flash"
            url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "systemInstruction": {"parts": [{"text": system_prompt}]},
                        "contents": [{"parts": [{"text": user_prompt}]}],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens,
                        }
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                usage = data.get("usageMetadata", {})
                return CompletionResult(
                    text=text,
                    input_tokens=usage.get("promptTokenCount", 0),
                    output_tokens=usage.get("candidatesTokenCount", 0),
                )
        except Exception as e:
            return CompletionResult(text="", error=str(e))
