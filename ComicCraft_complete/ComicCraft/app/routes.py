from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as PDFImage,
    PageBreak,
)

from app.gemini_flash import generate_panel_image


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
GENERATED_DIR = STATIC_DIR / "generated"

GENERATED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FASTAPI ROUTER
# ============================================================

router = APIRouter()

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# ============================================================
# HELPER: CONVERT FILE PATH TO BROWSER URL
# ============================================================

def _to_url(path):
    """
    Convert:

    C:/.../ComicCraft/static/generated/panel_1.png

    into:

    /static/generated/panel_1.png
    """

    if not path:
        return ""

    path = Path(path).resolve()

    try:
        relative_path = path.relative_to(BASE_DIR)
    except ValueError:
        return ""

    return "/" + relative_path.as_posix()


# ============================================================
# HOME PAGE
# ============================================================

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


# ============================================================
# GENERATE ALL PANEL IMAGES
# ============================================================

def _generate_all_panel_images(
    layout,
    character_name,
    setting,
    art_style,
):
    """
    Generate one image for every comic panel.
    """

    for panel in layout:

        image_prompt = panel.get(
            "scene_description",
            panel.get("image_prompt", ""),
        )

        image_path = generate_panel_image(
            image_prompt=image_prompt,
            panel_number=panel["panel_number"],
            character_name=character_name,
            setting=setting,
            art_style=art_style,
        )

        panel["image_path"] = image_path
        panel["image_url"] = _to_url(image_path)

        print(
            f"Panel {panel['panel_number']} image:"
        )
        print(
            f"PATH: {image_path}"
        )
        print(
            f"URL: {panel['image_url']}"
        )

    return layout


# ============================================================
# CREATE PDF
# ============================================================

def _create_comic_pdf(
    layout,
    character_name,
    story_prompt,
):
    """
    Create a PDF containing all comic panels.
    """

    pdf_path = GENERATED_DIR / "comic.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    story = []

    # --------------------------------------------------------
    # PDF TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "ComicCraft - AI Comic",
            styles["Title"],
        )
    )

    story.append(
        Spacer(1, 12)
    )

    # --------------------------------------------------------
    # CHARACTER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            f"<b>Character:</b> "
            f"{character_name}",
            styles["Normal"],
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # --------------------------------------------------------
    # STORY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            f"<b>Story:</b> "
            f"{story_prompt}",
            styles["Normal"],
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # --------------------------------------------------------
    # PANELS
    # --------------------------------------------------------

    for index, panel in enumerate(layout):

        panel_number = panel.get(
            "panel_number",
            index + 1,
        )

        title = panel.get(
            "title",
            f"Panel {panel_number}",
        )

        story.append(
            Paragraph(
                f"<b>Panel {panel_number}: "
                f"{title}</b>",
                styles["Heading2"],
            )
        )

        story.append(
            Spacer(1, 8)
        )

        # ----------------------------------------------------
        # PANEL IMAGE
        # ----------------------------------------------------

        image_path = panel.get(
            "image_path",
            "",
        )

        if image_path:

            image_file = Path(
                image_path
            ).resolve()

            if image_file.exists():

                try:

                    img = PDFImage(
                        str(image_file),
                        width=6.5 * inch,
                        height=4.5 * inch,
                        kind="proportional",
                    )

                    story.append(img)

                    story.append(
                        Spacer(1, 10)
                    )

                except Exception as image_error:

                    print(
                        "PDF image error:",
                        image_error,
                    )

        # ----------------------------------------------------
        # CAPTION
        # ----------------------------------------------------

        caption = panel.get(
            "caption",
            "",
        )

        if caption:

            story.append(
                Paragraph(
                    f"<b>Caption:</b> "
                    f"{caption}",
                    styles["Normal"],
                )
            )

            story.append(
                Spacer(1, 6)
            )

        # ----------------------------------------------------
        # NARRATION
        # ----------------------------------------------------

        narration = panel.get(
            "narration",
            "",
        )

        if narration:

            story.append(
                Paragraph(
                    f"<b>Narration:</b> "
                    f"{narration}",
                    styles["Normal"],
                )
            )

            story.append(
                Spacer(1, 6)
            )

        # ----------------------------------------------------
        # DIALOGUE
        # ----------------------------------------------------

        dialogue = panel.get(
            "dialogue",
            "",
        )

        if dialogue:

            story.append(
                Paragraph(
                    f"<b>Dialogue:</b> "
                    f"{dialogue}",
                    styles["Normal"],
                )
            )

        # ----------------------------------------------------
        # NEW PAGE
        # ----------------------------------------------------

        if index < len(layout) - 1:

            story.append(
                PageBreak()
            )

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    doc.build(story)

    print(
        f"PDF created: {pdf_path}"
    )

    return str(pdf_path)


# ============================================================
# COMIC PIPELINE
# ============================================================

def _run_comic_pipeline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style,
):
    """
    Complete comic generation pipeline.
    """

    # ========================================================
    # CREATE COMIC LAYOUT
    # ========================================================

    layout = [

        {
            "panel_number": 1,
            "title": "The Beginning",
            "scene_description": (
                f"{character_name} begins "
                f"an adventure in {setting}. "
                f"The scene should establish "
                f"the character, environment, "
                f"and mood."
            ),
            "caption": (
                "A new adventure begins."
            ),
            "narration": (
                f"{character_name} looks "
                f"around and prepares for "
                f"the journey."
            ),
            "dialogue": (
                "Let's begin!"
            ),
            "image_path": "",
            "image_url": "",
        },

        {
            "panel_number": 2,
            "title": "The Adventure",
            "scene_description": (
                f"{character_name} explores "
                f"{setting} and discovers "
                f"something interesting. "
                f"The scene should show "
                f"movement and adventure."
            ),
            "caption": (
                "Something unexpected appears."
            ),
            "narration": (
                "The journey becomes "
                "more exciting."
            ),
            "dialogue": (
                "What is that?"
            ),
            "image_path": "",
            "image_url": "",
        },

        {
            "panel_number": 3,
            "title": "The Discovery",
            "scene_description": (
                f"{character_name} discovers "
                f"the secret behind the "
                f"adventure in {setting}. "
                f"The scene should feel "
                f"dramatic and exciting."
            ),
            "caption": (
                "The mystery is finally revealed."
            ),
            "narration": (
                "Everything starts "
                "to make sense."
            ),
            "dialogue": (
                "I finally understand!"
            ),
            "image_path": "",
            "image_url": "",
        },

        {
            "panel_number": 4,
            "title": "The Ending",
            "scene_description": (
                f"{character_name} returns "
                f"home happily after the "
                f"adventure in {setting}. "
                f"The ending should feel "
                f"positive and satisfying."
            ),
            "caption": (
                "And so the adventure ends."
            ),
            "narration": (
                "It was an adventure "
                "to remember."
            ),
            "dialogue": (
                "What an amazing day!"
            ),
            "image_path": "",
            "image_url": "",
        },
    ]

    # ========================================================
    # GENERATE IMAGES
    # ========================================================

    layout = _generate_all_panel_images(
        layout=layout,
        character_name=character_name,
        setting=setting,
        art_style=art_style,
    )

    # ========================================================
    # CREATE PDF
    # ========================================================

    pdf_path = _create_comic_pdf(
        layout=layout,
        character_name=character_name,
        story_prompt=story_prompt,
    )

    return layout, pdf_path


# ============================================================
# GENERATE COMIC - HTML PAGE
# ============================================================

@router.post("/generate")
async def generate_comic(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(
        "Alex"
    ),

    setting: str = Form(
        "a magical forest"
    ),

    tone: str = Form(
        "adventure"
    ),

    art_style: str = Form(
        "comic book"
    ),
):

    try:

        layout, pdf_path = _run_comic_pipeline(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

    except Exception as exc:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Comic generation failed: "
                f"{exc}"
            ),
        )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "request": request,

            "layout": layout,

            "pdf_path": _to_url(
                pdf_path
            ),

            "character_name": (
                character_name
            ),

            "story_prompt": (
                story_prompt
            ),

            "setting": setting,

            "tone": tone,

            "art_style": art_style,
        },
    )


# ============================================================
# GENERATE COMIC - JSON API
# ============================================================

@router.post("/generate-comic/json")
async def generate_comic_json(
    story_prompt: str = Form(...),

    character_name: str = Form(
        "Alex"
    ),

    setting: str = Form(
        "a magical forest"
    ),

    tone: str = Form(
        "adventure"
    ),

    art_style: str = Form(
        "comic book"
    ),
):

    try:

        layout, pdf_path = _run_comic_pipeline(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        return JSONResponse(
            {
                "success": True,

                "character_name": (
                    character_name
                ),

                "story_prompt": (
                    story_prompt
                ),

                "layout": layout,

                "pdf_url": _to_url(
                    pdf_path
                ),
            }
        )

    except Exception as exc:

        import traceback

        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(exc),
            },
        )


# ============================================================
# TEST IMAGE GENERATION
# ============================================================

@router.post("/test-image")
async def test_image(
    prompt: str = Form(...),

    art_style: str = Form(
        "comic book"
    ),
):

    try:

        image_path = generate_panel_image(
            image_prompt=prompt,

            panel_number=1,

            character_name=(
                "Test Character"
            ),

            setting=(
                "Test Setting"
            ),

            art_style=art_style,
        )

        return JSONResponse(
            {
                "success": True,

                "image_url": _to_url(
                    image_path
                ),

                "image_path": str(
                    image_path
                ),
            }
        )

    except Exception as exc:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Image generation failed: "
                f"{exc}"
            ),
        )


# ============================================================
# EXPORT SUCCESS PAGE
# ============================================================

@router.get("/export-success")
async def export_success(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request,
        },
    )