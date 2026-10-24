"""OpenRouter provider."""

from .openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        super().__init__(api_key, base_url or "https://openrouter.ai/api/v1", model)
    
    async def list_models(self) -> list:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(f"{self.base_url}/models")
                resp.raise_for_status()
                data = resp.json()
                from .base import ModelInfo
                models = []
                for m in data.get("data", []):
                    models.append(ModelInfo(id=m["id"], name=m.get("name", m["id"])))
                return models[:100]
        except Exception:
            return []
