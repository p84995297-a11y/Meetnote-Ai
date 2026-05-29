# ============================================
# Updated PDF Routes with Database Support
# ============================================
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import datetime
import json

from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import FileResponse

try:
    from fpdf import FPDF
except Exception:
    FPDF = None

# Import database and models
try:
    from backend.database import SessionLocal, PDFExport, TranscriptNote, get_db
    from backend.config import get_settings
except Exception:
    from database import SessionLocal, PDFExport, TranscriptNote, get_db
    from config import get_settings

router = APIRouter()
settings = get_settings()

# Ensure PDF output directory exists
pdf_output_path = Path(settings.PDF_OUTPUT_DIR)
pdf_output_path.mkdir(parents=True, exist_ok=True)

latest_transcript = ""
latest_summary = ""
latest_points = []
latest_language = "en"

BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "NotoSans-Regular.ttf"


# =========================================================
# SAVE NOTES
# =========================================================

def save_notes(
    transcript: str,
    summary: str,
    points=None,
    language: str = "en"
):
    """Save notes in memory for PDF generation"""
    global latest_transcript, latest_summary, latest_points, latest_language

    latest_transcript = transcript or ""
    latest_summary = summary or ""
    latest_points = points or []
    latest_language = language


# =========================================================
# PDF HELPERS
# =========================================================

def _supports_modern_fpdf_api() -> bool:
    """Check if FPDF supports modern API"""
    try:
        import inspect
        return "new_x" in inspect.signature(FPDF.cell).parameters
    except Exception:
        return False


def _safe_pdf_text(value) -> str:
    """Convert text to PDF-safe format"""
    text = str(value or "")
    if FONT_PATH.exists():
        return text

    # Built-in FPDF fonts only support Latin-1
    return text.encode("latin-1", "replace").decode("latin-1")


def _cell_next(pdf: FPDF, width: float, height: float, text: str, align: str = ""):
    """Add cell with next line handling"""
    if _supports_modern_fpdf_api():
        pdf.cell(
            width,
            height,
            text=_safe_pdf_text(text),
            new_x="LMARGIN",
            new_y="NEXT",
            align=align
        )
    else:
        pdf.cell(width, height, txt=_safe_pdf_text(text), ln=1, align=align)


def _multi_cell(pdf: FPDF, width: float, height: float, text: str):
    """Add multi-line cell"""
    if _supports_modern_fpdf_api():
        pdf.multi_cell(width, height, text=_safe_pdf_text(text))
    else:
        pdf.multi_cell(width, height, txt=_safe_pdf_text(text))


def _configure_font(pdf: FPDF, size: int):
    """Configure PDF font for multilingual support"""
    if FONT_PATH.exists():
        try:
            pdf.add_font("Noto", "", str(FONT_PATH), uni=True)
            pdf.set_font("Noto", size=size)
            return
        except TypeError:
            try:
                pdf.add_font("Noto", "", str(FONT_PATH))
                pdf.set_font("Noto", size=size)
                return
            except Exception as e:
                print(f"Font configuration error: {e}")

    pdf.set_font("Arial", size=size)


def build_pdf(
    transcript: str,
    summary: str,
    points=None,
    language: str = "en"
) -> Path:
    """Build PDF document with all notes"""
    if FPDF is None:
        raise HTTPException(
            status_code=500,
            detail="PDF generation dependency missing. Install: pip install fpdf2"
        )

    if points is None:
        points = []

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ============= TITLE =============
    _configure_font(pdf, 18)
    _cell_next(pdf, 0, 12, "MeetNote AI - Smart Notes", align="C")
    
    _configure_font(pdf, 10)
    language_name = settings.SUPPORTED_LANGUAGES.get(language, "English")
    _cell_next(pdf, 0, 8, f"Language: {language_name} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", align="C")
    pdf.ln(8)

    # ============= TRANSCRIPT =============
    _configure_font(pdf, 14)
    _cell_next(pdf, 0, 10, "📝 Transcript", align="L")
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)

    _configure_font(pdf, 10)
    transcript_text = transcript or "No transcript available"
    _multi_cell(pdf, 0, 6, transcript_text)
    pdf.ln(5)

    # ============= SUMMARY =============
    _configure_font(pdf, 14)
    _cell_next(pdf, 0, 10, "📊 Summary", align="L")
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)

    _configure_font(pdf, 10)
    summary_text = summary or "No summary available"
    _multi_cell(pdf, 0, 6, summary_text)
    pdf.ln(5)

    # ============= KEY POINTS =============
    _configure_font(pdf, 14)
    _cell_next(pdf, 0, 10, "⭐ Key Points", align="L")
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)

    _configure_font(pdf, 10)
    if points and len(points) > 0:
        for index, point in enumerate(points, start=1):
            point_text = f"{index}. {point}"
            _multi_cell(pdf, 0, 6, point_text)
    else:
        _multi_cell(pdf, 0, 6, "• No key points extracted")

    pdf.ln(10)

    # ============= FOOTER =============
    _configure_font(pdf, 8)
    pdf.set_y(-15)
    pdf.cell(0, 10, "MeetNote AI - Intelligent Meeting Notes Generator", 0, 0, "C")

    # Save PDF to file
    filename = f"MeetNote_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = pdf_output_path / filename

    try:
        pdf.output(str(output_path))
        print(f"✓ PDF saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"✗ PDF save error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PDF: {str(e)}"
        )


# =========================================================
# SAVE PDF TO DATABASE
# =========================================================

def save_pdf_to_database(
    pdf_path: Path,
    transcript_note_id: int,
    user_id: int = None,
    language: str = "en"
):
    """Save PDF export record to database"""
    db = SessionLocal()
    try:
        file_size = pdf_path.stat().st_size if pdf_path.exists() else 0
        
        pdf_export = PDFExport(
            transcript_note_id=transcript_note_id,
            user_id=user_id,
            pdf_filename=pdf_path.name,
            pdf_path=str(pdf_path),
            file_size=file_size,
            generated_at=datetime.utcnow(),
            language=language
        )
        
        db.add(pdf_export)
        db.commit()
        db.refresh(pdf_export)
        
        print(f"✓ PDF record saved to database: ID {pdf_export.id}")
        return pdf_export
    except Exception as e:
        print(f"✗ Database save error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# =========================================================
# PDF DOWNLOAD ENDPOINT
# =========================================================

@router.get("/download-pdf")
async def download_pdf(transcript_note_id: int = None):
    """Download PDF from generated notes"""
    try:
        output_path = build_pdf(
            latest_transcript,
            latest_summary,
            latest_points,
            latest_language
        )

        # Save to database if transcript_note_id provided
        if transcript_note_id:
            try:
                save_pdf_to_database(
                    output_path,
                    transcript_note_id=transcript_note_id,
                    language=latest_language
                )
            except Exception as e:
                print(f"Warning: Could not save PDF record: {e}")

        return FileResponse(
            str(output_path),
            media_type="application/pdf",
            filename=output_path.name
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Download error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF download failed: {str(e)}"
        )


# =========================================================
# DOWNLOAD PDF FROM JSON
# =========================================================

@router.post("/download-pdf-from-json")
async def download_pdf_from_json(
    payload: dict = Body(...),
    transcript_note_id: int = None,
    user_id: int = None
):
    """Generate and download PDF from JSON payload"""
    try:
        transcript = payload.get("transcript", "")
        summary = payload.get("summary", "")
        points = payload.get("key_points", [])
        language = payload.get("language", "en")

        # Validate inputs
        if not isinstance(points, list):
            points = []

        points = [str(point) for point in points]

        # Save notes in memory
        save_notes(transcript, summary, points, language)

        # Generate PDF
        output_path = build_pdf(transcript, summary, points, language)

        # Save to database
        if transcript_note_id:
            try:
                save_pdf_to_database(
                    output_path,
                    transcript_note_id=transcript_note_id,
                    user_id=user_id,
                    language=language
                )
            except Exception as e:
                print(f"Warning: Database save failed: {e}")

        return FileResponse(
            str(output_path),
            media_type="application/pdf",
            filename=output_path.name,
            headers={"Content-Disposition": f"attachment; filename={output_path.name}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"PDF generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )


# =========================================================
# GET PDF HISTORY
# =========================================================

@router.get("/pdf-history/{transcript_note_id}")
async def get_pdf_history(transcript_note_id: int):
    """Get PDF export history for a transcript"""
    db = SessionLocal()
    try:
        pdfs = db.query(PDFExport).filter(
            PDFExport.transcript_note_id == transcript_note_id
        ).all()

        return {
            "total": len(pdfs),
            "pdfs": [
                {
                    "id": pdf.id,
                    "filename": pdf.pdf_filename,
                    "language": pdf.language,
                    "generated_at": pdf.generated_at.isoformat(),
                    "file_size": pdf.file_size,
                    "download_count": pdf.downloaded_count
                }
                for pdf in pdfs
            ]
        }
    except Exception as e:
        print(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
