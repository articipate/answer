"""Google Gemini provider."""

import httpx
from typing import List
from .base import BaseProvider, ModelInfo, CompletionResult


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://generativelanguage.googleapis.com/v1beta", model)
    
    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id="gemini-2.5-flash", name="Gemini 2.5 Flash"),
            ModelInfo(id="gemini-2.5-pro", name="Gemini 2.5 Pro"),
            ModelInfo(id="gemini-2.0-flash", name="Gemini 2.0 Flash"),
        ]
    
    async def test_connection(self) -> bool:
        return bool(self.api_key)
    
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
