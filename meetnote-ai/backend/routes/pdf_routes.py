from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse

try:
    from fpdf import FPDF
except Exception:  # pragma: no cover - handled at runtime with clear message
    FPDF = None

router = APIRouter()

latest_transcript = ""
latest_summary = ""
latest_points: list[str] = []

BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "NotoSans-Regular.ttf"


# =========================================================
# SAVE NOTES
# =========================================================

def save_notes(transcript: str, summary: str, points: list[str] | None):
    global latest_transcript, latest_summary, latest_points

    latest_transcript = transcript or ""
    latest_summary = summary or ""
    latest_points = points or []


# =========================================================
# PDF HELPERS
# =========================================================

def _supports_modern_fpdf_api() -> bool:
    try:
        import inspect

        return "new_x" in inspect.signature(FPDF.cell).parameters
    except Exception:
        return False


def _safe_pdf_text(value) -> str:
    text = str(value or "")
    if FONT_PATH.exists():
        return text

    # Built-in FPDF fonts only support Latin-1. Replace unsupported characters
    # when the Unicode font is unavailable instead of crashing PDF generation.
    return text.encode("latin-1", "replace").decode("latin-1")


def _cell_next(pdf: FPDF, width: float, height: float, text: str, align: str = ""):
    if _supports_modern_fpdf_api():
        pdf.cell(width, height, text=_safe_pdf_text(text), new_x="LMARGIN", new_y="NEXT", align=align)
    else:
        pdf.cell(width, height, txt=_safe_pdf_text(text), ln=1, align=align)


def _multi_cell(pdf: FPDF, width: float, height: float, text: str):
    if _supports_modern_fpdf_api():
        pdf.multi_cell(width, height, text=_safe_pdf_text(text))
    else:
        pdf.multi_cell(width, height, txt=_safe_pdf_text(text))


def _configure_font(pdf: FPDF, size: int):
    if FONT_PATH.exists():
        try:
            pdf.add_font("Noto", "", str(FONT_PATH), uni=True)
            pdf.set_font("Noto", size=size)
            return
        except TypeError:
            pdf.add_font("Noto", "", str(FONT_PATH))
            pdf.set_font("Noto", size=size)
            return

    pdf.set_font("Arial", size=size)


def build_pdf(transcript: str, summary: str, points: list[str]) -> Path:
    if FPDF is None:
        raise HTTPException(
            status_code=500,
            detail="PDF generation dependency is missing. Install it with: pip install fpdf2",
        )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    _configure_font(pdf, 18)
    _cell_next(pdf, 0, 10, "MeetNote AI Notes", align="C")
    pdf.ln(8)

    _configure_font(pdf, 14)
    _cell_next(pdf, 0, 10, "Transcript")
    _configure_font(pdf, 11)
    _multi_cell(pdf, 0, 8, transcript or "No transcript")
    pdf.ln(5)

    _configure_font(pdf, 14)
    _cell_next(pdf, 0, 10, "Summary")
    _configure_font(pdf, 11)
    _multi_cell(pdf, 0, 8, summary or "No summary")
    pdf.ln(5)

    _configure_font(pdf, 14)
    _cell_next(pdf, 0, 10, "Important Points")
    _configure_font(pdf, 11)

    if points:
        for index, point in enumerate(points, start=1):
            _multi_cell(pdf, 0, 8, f"{index}. {point}")
    else:
        _multi_cell(pdf, 0, 8, "No important points")

    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf", prefix="MeetNote_")
    output_path = Path(temp_file.name)
    temp_file.close()
    pdf.output(str(output_path))
    return output_path


# =========================================================
# PDF DOWNLOAD
# =========================================================

@router.get("/download-pdf")
def download_pdf():
    output_path = build_pdf(latest_transcript, latest_summary, latest_points)
    return FileResponse(
        str(output_path),
        media_type="application/pdf",
        filename="MeetNote_AI_Notes.pdf",
    )


# =========================================================
# DOWNLOAD PDF FROM JSON
# =========================================================

@router.post("/download-pdf-from-json")
def download_pdf_from_json(payload: dict = Body(...)):
    transcript = payload.get("transcript", "")
    summary = payload.get("summary", "")
    points = payload.get("key_points", [])

    if not isinstance(points, list):
        points = []

    points = [str(point) for point in points]
    save_notes(transcript, summary, points)
    return download_pdf()
