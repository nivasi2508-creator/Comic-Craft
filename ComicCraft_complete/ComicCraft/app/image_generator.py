from pathlib import Path
import importlib
import re
import time
import requests
from io import BytesIO
from app.config import settings

Image = importlib.import_module("PIL.Image")

def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
    return value[:80] or "panel"

def _placeholder(path: Path, title: str):
    img = Image.new("RGB", (1024, 768), "white" )
    img.save(path, format="JPEG", quality=92)

def generate_image(image_prompt: str, panel_number: int, art_style: str) -> str:
    settings.ensure_directories()
    filename = f"panel-{panel_number}-{_safe_name(art_style)}-{int(time.time()*1000)}.jpg"
    output = settings.panels_dir / filename

    if settings.image_mode.lower() != "hf_api":
        _placeholder(output, image_prompt)
        return f"/static/panels/{filename}"

    if not settings.hf_api_key:
        # Keeps the app runnable for UI/PDF testing even before an HF token is configured.
        _placeholder(output, image_prompt)
        return f"/static/panels/{filename}"

    prompt = (
        f"{image_prompt}. Style: {art_style}. "
        "Clean comic illustration, expressive characters, cinematic composition, "
        "consistent character design, no text, no watermark."
    )
    url = f"https://router.huggingface.co/hf-inference/models/{settings.hf_image_model}"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {settings.hf_api_key}"},
        json={"inputs": prompt},
        timeout=180,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Hugging Face image generation failed ({response.status_code}): {response.text[:500]}")
    content_type = response.headers.get("content-type", "")
    if "image" not in content_type:
        raise RuntimeError("Hugging Face returned a non-image response.")

    image = Image.open(BytesIO(response.content)).convert("RGB")
    image.save(output, format="JPEG", quality=92)
    return f"/static/panels/{filename}"
