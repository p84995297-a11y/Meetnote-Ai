from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os

# Import local AI helpers robustly so the app works whether started
# from the project root or from the `backend/` directory.
try:
    from backend.ai.summarizer import generate_summary
    from backend.ai.translator import translate_text
    from backend.routes.pdf_routes import save_notes
except Exception:
    from ai.summarizer import generate_summary
    from ai.translator import translate_text
    from routes.pdf_routes import save_notes

router = APIRouter()


# Lazy-load Whisper model to avoid heavy import at module import time
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
        except Exception as e:
            raise RuntimeError(f"Whisper import failed: {e}")

        try:
            _whisper_model = whisper.load_model("base")
        except Exception as e:
            raise RuntimeError(f"Whisper model load failed: {e}")

    return _whisper_model


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    language: str = Form("en")
):

    try:
        # CREATE uploads FOLDER
        os.makedirs("uploads", exist_ok=True)

        # SAVE FILE
        file_path = os.path.join("uploads", file.filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # TRANSCRIBE (lazy-load model)
        try:
            model = get_whisper_model()
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

        result = model.transcribe(file_path)
        transcript = result.get("text", "").strip()

        # SUMMARY
        summary = generate_summary(transcript)

        # KEY POINTS
        key_points = [
            sentence.strip()
            for sentence in transcript.split(".")
            if len(sentence.strip()) > 25
        ][:5]

        # TRANSLATION
        if language != "en":
            try:
                transcript = translate_text(transcript, language)
                summary = translate_text(summary, language)

                translated_points = []
                for point in key_points:
                    translated_points.append(translate_text(point, language))

                key_points = translated_points
            except Exception as e:
                print("Translation Error:", e)

        # SAVE PDF DATA
        save_notes(transcript, summary, key_points)

        return {
            "transcript": transcript,
            "summary": summary,
            "key_points": key_points
        }

    except HTTPException:
        raise
    except Exception as e:
        print("UPLOAD ERROR:", e)
        return {"error": str(e)}