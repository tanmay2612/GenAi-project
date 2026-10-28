"""Image validation and preparation for multimodal prompts."""
from __future__ import annotations

import hashlib
import io
from typing import Tuple

from PIL import Image, ImageOps, UnidentifiedImageError

from core.config import MAX_IMAGE_SIDE, MAX_UPLOAD_MB


def prepare_image(uploaded_file) -> Tuple[Image.Image, str]:
    """Validate an uploaded file and return (RGB image resized for the model, content digest)."""
    data = uploaded_file.getvalue()
    if not data:
        raise ValueError("The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"The image is larger than {MAX_UPLOAD_MB} MB. Upload a smaller photo.")
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("This file could not be read as an image. Upload a JPG or PNG.") from exc

    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    return image, hashlib.sha256(data).hexdigest()
