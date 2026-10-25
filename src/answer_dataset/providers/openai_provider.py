"""OpenAI provider."""

import httpx
from typing import List
from .base import BaseProvider, ModelInfo, CompletionResult


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://api.openai.com/v1", model)
    
    async def list_models(self) -> List[ModelInfo]:
        try:
            base = (self.base_url or "https://api.openai.com/v1").rstrip("/")
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            async with httpx.AsyncClient(timeout=90, follow_redirects=True) as client:
                # Try /models first
                try:
                    resp = await client.get(f"{base}/models", headers=headers)
                    if resp.status_code in (401, 403) and self.api_key:
                        # Try without changing headers, maybe key issue
                        pass
                    if resp.status_code < 400:
                        data = resp.json()
                        items = data.get("data") or data.get("models") or []
                        models = []
                        for m in items:
                            if isinstance(m, dict):
                                model_id = m.get("id") or m.get("name") or m.get("model") or ""
                            elif isinstance(m, str):
                                model_id = m
                            else:
                                continue
                            if model_id and isinstance(model_id, str) and model_id.strip():
                                models.append(ModelInfo(id=model_id.strip(), name=model_id.strip()))
                        if models:
                            priority = ["gpt-4o", "gpt-4.1", "gpt-5", "o3", "o1", "gpt-4-turbo"]
                            def sort_key(x):
                                for i, p in enumerate(priority):
                                    if x.id.startswith(p) or p in x.id:
                                        return (0, i, x.id)
                                return (1, 0, x.id)
                            return sorted(models, key=sort_key)
                except Exception:
                    pass
                # Fallback: try /v1/models style
                if not base.endswith('/v1'):
                    try:
                        resp = await client.get(f"{base}/v1/models", headers=headers)
                        if resp.status_code < 400:
                            data = resp.json()
                            items = data.get("data") or []
                            models = []
                            for m in items:
                                model_id = m.get("id") if isinstance(m, dict) else str(m)
                                if model_id:
                                    models.append(ModelInfo(id=str(model_id), name=str(model_id)))
                            if models:
                                return sorted(models, key=lambda x: x.id)
                    except Exception:
                        pass
        except Exception:
            pass
        # Last resort defaults
        if "api.openai.com" in (self.base_url or ""):
            return [
                ModelInfo(id="gpt-4o", name="gpt-4o"),
                ModelInfo(id="gpt-4o-mini", name="gpt-4o-mini"),
                ModelInfo(id="gpt-4.1", name="gpt-4.1"),
                ModelInfo(id="gpt-4.1-mini", name="gpt-4.1-mini"),
            ]
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
