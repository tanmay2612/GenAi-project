"""Thin wrapper around the Google Gen AI SDK (``google-genai``).

The rest of the app only talks to :class:`GeminiClient`, so swapping in another multimodal
provider (for example a LLaMA vision endpoint) means changing this one file.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from PIL import Image

from core.config import DEFAULT_MODEL
from core.schemas import extract_json

log = logging.getLogger(__name__)

_FATAL_HINTS = ("api key", "api_key", "permission", "unauthenticated", "invalid argument", "not found")


class GeminiError(RuntimeError):
    """Raised for any failure talking to the model."""


class GeminiClient:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = (api_key or "").strip()
        self.model = (model or DEFAULT_MODEL).strip()
        self._client: Any = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    # ------------------------------------------------------------------ internals
    def _sdk(self):
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise GeminiError("The 'google-genai' package is not installed.") from exc
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return types

    def _generate(self, contents: List[Any], config: Any, retries: int = 2) -> str:
        last: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                self._sdk()
                response = self._client.models.generate_content(
                    model=self.model, contents=contents, config=config
                )
                text = getattr(response, "text", None)
                if not text:
                    raise GeminiError("The model returned no text (the response may have been blocked).")
                return text
            except GeminiError:
                raise
            except Exception as exc:  # network, quota, auth, ...
                last = exc
                log.warning("Gemini call failed (attempt %s): %s", attempt + 1, exc)
                if any(hint in str(exc).lower() for hint in _FATAL_HINTS):
                    break  # retrying will not fix a bad key or model name
                time.sleep(1.5 * (attempt + 1))
        raise GeminiError(f"Gemini request failed: {last}") from last

    # ------------------------------------------------------------------ public API
    def generate_json(self, prompt: str, image: Optional[Image.Image] = None) -> Dict[str, Any]:
        types = self._sdk()
        config = types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
        contents: List[Any] = [prompt] + ([image] if image is not None else [])
        text = self._generate(contents, config)
        try:
            return extract_json(text)
        except ValueError as exc:
            raise GeminiError(f"Could not parse the model's JSON: {exc}") from exc

    def chat(self, system_prompt: str, history: List[Dict[str, str]], message: str) -> str:
        types = self._sdk()
        config = types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.4)
        contents = [
            types.Content(
                role="model" if turn["role"] == "assistant" else "user",
                parts=[types.Part.from_text(text=turn["content"])],
            )
            for turn in history
        ]
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
        return self._generate(contents, config).strip()
