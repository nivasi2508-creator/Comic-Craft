import os
from pathlib import Path

try:
    from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False

from google import genai

# Load .env from ComicCraft_complete
project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")

api_key = os.getenv("GEMINI_API_KEY")

print("Key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError("GEMINI_API_KEY was not found in .env")

print("Key prefix:", api_key[:5])
print("Key length:", len(api_key))

client = genai.Client(
    api_key=api_key,
    http_options={"api_version": "v1"},
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Reply with exactly: OK",
)

print("Gemini response:", response.text)