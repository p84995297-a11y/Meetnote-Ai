from fastapi import APIRouter, Body
from fastapi.responses import FileResponse, JSONResponse

from fpdf import FPDF

import os
import uuid

router = APIRouter()

latest_transcript = ""
latest_summary = ""
latest_points = []


# =========================================================
# SAVE NOTES
# =========================================================

def save_notes(transcript, summary, points):

    global latest_transcript
    global latest_summary
    global latest_points

    latest_transcript = transcript
    latest_summary = summary
    latest_points = points


# =========================================================
# DOWNLOAD PDF
# =========================================================

@router.get("/download-pdf")
def download_pdf():

    try:

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # YOUR REAL FONT FILE
        FONT_PATH = os.path.join(
            BASE_DIR,
            "NotoSans-Regular.ttf"
        )

        print("FONT PATH:", FONT_PATH)

        # CHECK FONT
        if not os.path.exists(FONT_PATH):

            return JSONResponse({
                "error": f"Font not found: {FONT_PATH}"
            })

        pdf = FPDF()

        pdf.add_page()

        # REGISTER FONT
        pdf.add_font(
            "Noto",
            "",
            FONT_PATH,
            uni=True
        )

        pdf.set_font("Noto", size=18)

        # TITLE
        pdf.cell(
            200,
            10,
            txt="MeetNote AI Notes",
            ln=True,
            align="C"
        )

        pdf.ln(10)

        # TRANSCRIPT
        pdf.set_font("Noto", size=14)

        pdf.cell(0, 10, "Transcript", ln=True)

        pdf.set_font("Noto", size=11)

        transcript_text = latest_transcript or "No transcript"

        pdf.multi_cell(
            0,
            8,
            transcript_text
        )

        pdf.ln(5)

        # SUMMARY
        pdf.set_font("Noto", size=14)

        pdf.cell(0, 10, "Summary", ln=True)

        pdf.set_font("Noto", size=11)

        summary_text = latest_summary or "No summary"

        pdf.multi_cell(
            0,
            8,
            summary_text
        )

        pdf.ln(5)

        # IMPORTANT POINTS
        pdf.set_font("Noto", size=14)

        pdf.cell(0, 10, "Important Points", ln=True)

        pdf.set_font("Noto", size=11)

        if latest_points:

            for point in latest_points:

                pdf.multi_cell(
                    0,
                    8,
                    f"• {point}"
                )

        else:

            pdf.multi_cell(
                0,
                8,
                "No important points"
            )

        # SAVE PDF
        filename = f"MeetNote_{uuid.uuid4().hex}.pdf"

        output_path = os.path.join(
            BASE_DIR,
            filename
        )

        pdf.output(output_path)

        print("PDF SAVED:", output_path)

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename="MeetNote_AI_Notes.pdf"
        )

    except Exception as e:

        return JSONResponse({
            "error": str(e)
        })


# =========================================================
# DOWNLOAD PDF FROM JSON
# =========================================================

@router.post("/download-pdf-from-json")
def download_pdf_from_json(
    payload: dict = Body(...)
):

    transcript = payload.get(
        "transcript",
        ""
    )

    summary = payload.get(
        "summary",
        ""
    )

    points = payload.get(
        "key_points",
        []
    )

    save_notes(
        transcript,
        summary,
        points
    )

    return download_pdf()