from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    version="1.0.0",
    description="Generate four-panel AI comics with Gemini and Hugging Face.",
)

app.mount(
    "/static",
    StaticFiles(
        directory=str(settings.static_dir)
    ),
    name="static",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}
