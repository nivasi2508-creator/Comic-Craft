# ComicCraft — AI Comic Story Creator

A complete FastAPI + Jinja2 application based on the supplied ComicCraft documentation. It generates a five-panel outline with Gemini, expands it into narration/dialogue, generates panel artwork through Hugging Face, previews the comic, and exports it as PDF.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   ├── export_success.html
│   └── error.html
├── static/
│   ├── css/style.css
│   ├── panels/
│   └── exports/
├── .env.example
├── requirements.txt
└── README.md
```

## 1. Open in VS Code

Open the `ComicCraft` folder, then open a VS Code terminal.

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure API keys

Copy `.env.example` to `.env`.

Put your Gemini API key in:

```env
GEMINI_API_KEY=your_key
```

For real AI images, also set:

```env
HF_API_KEY=your_huggingface_token
```

If `HF_API_KEY` is empty, the site still runs and the PDF workflow can be tested with generated placeholder images.

## 5. Start the server

```bash
python -m uvicorn app.main:app --reload
```

Open:

- Website: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 6. Test

1. Open the website.
2. Enter a story prompt.
3. Enter a character name.
4. Select setting, tone, and art style.
5. Click Generate My Comic.
6. Wait for the AI pipeline to finish.
7. Review the five panels.
8. Click Download Your Comic as PDF.

### API test

POST `/generate-comic/json` with:

```json
{
  "story_prompt": "A brave fox discovers a hidden portal in an enchanted forest.",
  "character_name": "Nova",
  "setting": "Enchanted forest",
  "tone": "Adventurous",
  "art_style": "Comic book"
}
```

## Troubleshooting

### "GEMINI_API_KEY is missing"

Make sure `.env` exists in the project root and contains a real key. Restart Uvicorn after changing `.env`.

### Image generation fails

Check `HF_API_KEY`. You can temporarily leave it empty; ComicCraft will use placeholder images so the rest of the application can be tested.

### Model not found

The original project document names older Gemini models. This implementation uses an environment-configurable Gemini model, defaulting to `gemini-3.8-flash`. If your API account exposes a different model, change `GEMINI_MODEL` in `.env`.

### PowerShell blocks activation

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Notes

The supplied documentation describes Gemini Flash for the outline, Gemini Pro for story expansion, Stable Diffusion for images, FastAPI/Jinja2 for the website, and FPDF for PDF export. This implementation keeps those architectural responsibilities while using the current Google Gen AI Python SDK and an environment-configurable Gemini model so the application is easier to maintain.
