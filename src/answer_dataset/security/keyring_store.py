"""Secure API key storage using OS keyring."""

import keyring
from typing import Optional


class KeyringStore:
    SERVICE_NAME = "Answer"
    
    def save_key(self, provider: str, api_key: str):
        if not api_key:
            return
        try:
            keyring.set_password(self.SERVICE_NAME, provider, api_key)
        except Exception:
            # Fallback to in-memory if keyring fails
            pass
    
    def get_key(self, provider: str) -> Optional[str]:
        try:
            return keyring.get_password(self.SERVICE_NAME, provider)
        except Exception:
            return None
    
    def delete_key(self, provider: str):
        try:
            keyring.delete_password(self.SERVICE_NAME, provider)
        except Exception:
            pass


keyring_store = KeyringStore()
