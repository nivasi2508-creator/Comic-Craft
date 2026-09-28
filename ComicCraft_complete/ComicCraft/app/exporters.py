from pathlib import Path
from datetime import datetime
from fpdf import FPDF  # type: ignore[reportMissingModuleSource]
from PIL import Image  # type: ignore[reportMissingImports]
from app.config import settings

def _local_image(image_path: str) -> Path:
    return settings.static_dir.parent / image_path.lstrip("/")

def save_pdf(layout: list[dict], title: str = "ComicCraft Comic") -> str:
    settings.ensure_directories()
    filename = f"comic-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
    output = settings.exports_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, panel["title"][:80], ln=True)
        image_file = _local_image(panel["image_path"])
        if image_file.exists():
            with Image.open(image_file) as im:
                w, h = im.size
            max_w, max_h = 180, 105
            ratio = min(max_w / w, max_h / h)
            pdf.image(str(image_file), x=15, y=28, w=w*ratio, h=h*ratio)
            pdf.set_y(28 + h*ratio + 8)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, panel["scene_description"][:1000])
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 11)
        for label, value in [
            ("Caption", panel["caption"]),
            ("Narration", panel["narration"]),
            ("Dialogue", panel["dialogue"]),
        ]:
            if value:
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 6, f"{label}:", ln=True)
                pdf.set_font("Helvetica", "", 11)
                pdf.multi_cell(0, 6, value[:1500])
                pdf.ln(1)

    pdf.output(str(output))
    return f"/static/exports/{filename}"
