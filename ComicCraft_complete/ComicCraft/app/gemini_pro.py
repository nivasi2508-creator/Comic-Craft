import json
import re
from google import genai
from google.genai import types
from app.config import settings

def _client():
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
    return genai.Client(api_key=settings.gemini_api_key)

def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Gemini returned invalid story JSON.")
        return json.loads(match.group(0))

def generate_story(outline: list[dict], character_name: str, tone: str) -> list[dict]:
    prompt = f"""
Expand this five-panel comic outline into finished comic text.

Main character: {character_name}
Tone: {tone}
Outline:
{json.dumps(outline, ensure_ascii=False, indent=2)}

Return ONLY valid JSON:
{{
  "panels": [
    {{
      "panel_number": 1,
      "caption": "short ambient caption",
      "narration": "2-4 sentences of comic narration",
      "dialogue": "optional short dialogue, or empty string"
    }}
  ]
}}

Keep exactly five panels and preserve panel numbers.
"""
    response = _client().models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            max_output_tokens=5000,
        ),
    )
    data = _extract_json(response.text)
    panels = data.get("panels")
    if not isinstance(panels, list) or len(panels) != 5:
        raise ValueError("Gemini did not return exactly five story panels.")
    return panels
