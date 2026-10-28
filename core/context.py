"""Shared application context passed from the sidebar to every tab."""
from __future__ import annotations

from dataclasses import dataclass

from core.gemini_client import GeminiClient


@dataclass
class AppContext:
    client: GeminiClient

    @property
    def live(self) -> bool:
        return self.client.enabled
