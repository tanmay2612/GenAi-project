"""Shared pipeline: try the live model, fall back to demonstration data."""
from __future__ import annotations

import datetime as dt
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from PIL import Image

from core.gemini_client import GeminiClient, GeminiError

log = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    report: Dict[str, Any]
    mode: str  # "live" or "demo"
    warning: Optional[str] = None


def run_analysis(
    client: GeminiClient,
    prompt: str,
    image: Image.Image,
    normalizer: Callable[[Dict[str, Any]], Dict[str, Any]],
    demo_factory: Callable[[], Dict[str, Any]],
) -> AnalysisResult:
    """Run a multimodal analysis. Never raises: failures degrade to demo output with a warning."""
    started = time.time()
    mode, warning = "demo", None
    raw: Dict[str, Any]

    if client.enabled:
        try:
            raw = client.generate_json(prompt, image)
            mode = "live"
        except (GeminiError, ValueError) as exc:
            log.warning("Live analysis failed: %s", exc)
            warning = f"Live analysis failed ({exc}). Showing demonstration output instead."
            raw = demo_factory()
    else:
        raw = demo_factory()

    report = normalizer(raw)
    report["meta"] = {
        "mode": mode,
        "model": client.model if mode == "live" else "demonstration",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time() - started, 2),
    }
    return AnalysisResult(report=report, mode=mode, warning=warning)
