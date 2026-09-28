from pathlib import Path
import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "black-forest-labs/FLUX.1-schnell",
)

if not HF_API_KEY:
    raise RuntimeError("HF_API_KEY is missing from your .env file.")

image_client = InferenceClient(
    api_key=HF_API_KEY,
    provider="auto",
)


def generate_panel_image(
    image_prompt: str,
    panel_number: int,
    character_name: str = "",
    setting: str = "",
    art_style: str = "comic book",
):
    base_dir = Path(__file__).resolve().parent.parent

    output_dir = base_dir / "static" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = f"""
Create a single comic-book panel.

Character: {character_name}
Setting: {setting}
Art style: {art_style}

Scene:
{image_prompt}

Requirements:
- colorful comic-book illustration
- clear composition
- expressive character
- cinematic lighting
- no text
- no speech bubbles
- no captions
"""

    try:
        print()
        print("=" * 60)
        print("HUGGING FACE IMAGE GENERATION")
        print("Model:", HF_IMAGE_MODEL)
        print("Prompt:", prompt[:500])
        print("=" * 60)

        image = image_client.text_to_image(
            prompt=prompt,
            model=HF_IMAGE_MODEL,
        )

        if image is None:
            raise RuntimeError(
                "Hugging Face returned None instead of an image."
            )

        output_path = output_dir / f"panel_{panel_number}.png"

        image.save(output_path)

        print("IMAGE SAVED:", output_path)
        print("=" * 60)

        return str(output_path)

    except Exception as exc:
        print()
        print("!!! HUGGING FACE ERROR !!!")
        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR:", repr(exc))
        print("ERROR TEXT:", str(exc))
        print("!!! END HUGGING FACE ERROR !!!")
        print()

        raise RuntimeError(
            f"Hugging Face image generation failed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc