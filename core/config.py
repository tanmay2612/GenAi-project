"""Central configuration and constants for the platform."""
from __future__ import annotations

APP_NAME = "Multimodal Construction Intelligence Platform"
APP_TAGLINE = "Skill Wallet Capstone · Project 1 · Generative AI for construction and real estate"
SCHEMA_VERSION = "1.0"

DEFAULT_MODEL = "gemini-2.5-flash"
MAX_UPLOAD_MB = 10
MAX_IMAGE_SIDE = 1600
SUPPORTED_TYPES = ["jpg", "jpeg", "png"]

PPE_ITEMS = ("Helmet", "High-Vis Vest", "Safety Boots", "Safety Harness")
SEVERITIES = ("Low", "Medium", "High", "Critical")
SAFETY_STATUSES = ("Compliant", "Needs Improvement", "Non-Compliant", "Critical")
DEFECT_TYPES = ("Hairline", "Settlement", "Structural Shear", "Thermal Expansion", "Spalling")

DISCLAIMER = (
    "AI-generated guidance for decision support only. It does not replace inspection by a "
    "certified safety officer or a licensed structural engineer."
)
