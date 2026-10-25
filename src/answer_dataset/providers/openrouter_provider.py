"""OpenRouter provider."""

from .openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://openrouter.ai/api/v1", model)
    
    async def list_models(self) -> list:
        try:
            import httpx
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{self.base_url.rstrip('/')}/models", headers=headers)
                resp.raise_for_status()
                data = resp.json()
                from .base import ModelInfo
                models = []
                for m in data.get("data", []):
                    model_id = m.get("id") or ""
                    if model_id:
                        models.append(ModelInfo(id=model_id, name=m.get("name", model_id)))
                return sorted(models, key=lambda x: x.id)[:200]
        except Exception:
            return []
    
    async def test_connection(self) -> bool:
        try:
            if not self.api_key:
                return False
            models = await self.list_models()
            return len(models) > 0
        except Exception:
            return False
