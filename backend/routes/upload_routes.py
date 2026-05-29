# ============================================
# Updated Upload Routes with Database & Fix
# ============================================
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime

# Import local AI helpers robustly
try:
    from backend.ai.summarizer import generate_summary
    from backend.ai.translator import translate_text
    from backend.database import SessionLocal, AudioFile, TranscriptNote, get_db
    from backend.config import get_settings
    from backend.routes.pdf_routes import save_notes
except Exception:
    from ai.summarizer import generate_summary
    from ai.translator import translate_text
    from database import SessionLocal, AudioFile, TranscriptNote, get_db
    from config import get_settings
    from routes.pdf_routes import save_notes

router = APIRouter()
settings = get_settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Lazy-load Whisper model
_whisper_model = None


def get_whisper_model():
    """Lazy-load Whisper model to avoid heavy import at startup"""
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
        except Exception as e:
            raise RuntimeError(f"Whisper import failed: {e}")

        try:
            _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        except Exception as e:
            raise RuntimeError(f"Whisper model load failed: {e}")

    return _whisper_model


# =========================================================
# UPLOAD & PROCESS FILE
# =========================================================

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    language: str = Form("en"),
    user_id: int = Form(None)
):
    """
    Upload audio/video file and process it:
    1. Save file to disk
    2. Transcribe using Whisper
    3. Generate summary using AI
    4. Extract key points
    5. Translate if needed
    6. Save all to database
    7. Prepare PDF download
    """
    
    db = SessionLocal()
    audio_file = None
    
    try:
        # ============= VALIDATE FILE =============
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )

        # Check file extension
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # ============= SAVE FILE TO DISK =============
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        print(f"✓ File saved: {file_path}")

        # ============= SAVE AUDIO FILE RECORD TO DATABASE =============
        audio_file = AudioFile(
            user_id=user_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            language=language,
            processing_status="processing"
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        print(f"✓ Audio file record created: ID {audio_file.id}")

        # ============= TRANSCRIBE AUDIO =============
        try:
            model = get_whisper_model()
        except RuntimeError as e:
            audio_file.processing_status = "failed"
            audio_file.error_message = str(e)
            db.commit()
            raise HTTPException(status_code=500, detail=str(e))

        try:
            result = model.transcribe(file_path, language=language if language != "en" else None)
            transcript = result.get("text", "").strip()
            
            if not transcript:
                raise ValueError("Empty transcript generated")
                
            print(f"✓ Transcription complete: {len(transcript)} characters")
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            audio_file.processing_status = "failed"
            audio_file.error_message = error_msg
            db.commit()
            raise HTTPException(status_code=500, detail=error_msg)

        # ============= GENERATE SUMMARY =============
        try:
            summary = generate_summary(transcript)
            print(f"✓ Summary generated: {len(summary)} characters")
        except Exception as e:
            print(f"⚠ Summary generation failed: {e}")
            summary = transcript[:500]  # Fallback to transcript excerpt

        # ============= EXTRACT KEY POINTS =============
        try:
            key_points = [
                sentence.strip()
                for sentence in transcript.split(".")
                if len(sentence.strip()) > 25
            ][:8]  # Get top 8 points
            print(f"✓ Key points extracted: {len(key_points)} points")
        except Exception as e:
            print(f"⚠ Key point extraction failed: {e}")
            key_points = []

        # ============= TRANSLATE IF NEEDED =============
        translated_transcript = transcript
        translated_summary = summary
        translated_points = key_points
        
        if language != "en" and settings.ENABLE_TRANSLATION:
            try:
                print(f"🌐 Translating to {language}...")
                translated_transcript = translate_text(transcript, language)
                translated_summary = translate_text(summary, language)
                
                translated_points = []
                for point in key_points:
                    try:
                        translated_points.append(translate_text(point, language))
                    except:
                        translated_points.append(point)
                
                print(f"✓ Translation complete")
            except Exception as e:
                print(f"⚠ Translation failed: {e}")
                translated_transcript = transcript
                translated_summary = summary
                translated_points = key_points

        # ============= SAVE TRANSCRIPT NOTE TO DATABASE =============
        try:
            transcript_note = TranscriptNote(
                audio_file_id=audio_file.id,
                user_id=user_id,
                transcript=translated_transcript,
                transcript_language=language,
                summary=translated_summary,
                summary_language=language,
                key_points=json.dumps(translated_points),
                duration=0,  # Would need ffprobe to get actual duration
                word_count=len(translated_transcript.split()),
                language_translated_to=language
            )
            db.add(transcript_note)
            db.commit()
            db.refresh(transcript_note)
            print(f"✓ Transcript note saved: ID {transcript_note.id}")
        except Exception as e:
            print(f"⚠ Database save error: {e}")
            db.rollback()
            transcript_note = None

        # ============= SAVE NOTES FOR PDF GENERATION =============
        try:
            save_notes(translated_transcript, translated_summary, translated_points, language)
        except Exception as e:
            print(f"⚠ Could not save notes for PDF: {e}")

        # ============= UPDATE AUDIO FILE STATUS =============
        audio_file.processing_status = "completed"
        audio_file.is_processed = True
        audio_file.processed_at = datetime.utcnow()
        db.commit()

        # ============= RETURN RESPONSE =============
        response_data = {
            "status": "success",
            "audio_file_id": audio_file.id,
            "transcript_note_id": transcript_note.id if transcript_note else None,
            "transcript": translated_transcript,
            "summary": translated_summary,
            "key_points": translated_points,
            "language": language,
            "message": "✓ Processing complete! PDF ready for download."
        }

        print(f"✓ Upload processing complete for file: {file.filename}")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        if audio_file:
            audio_file.processing_status = "failed"
            audio_file.error_message = str(e)
            try:
                db.commit()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    finally:
        db.close()


# =========================================================
# GET UPLOAD HISTORY
# =========================================================

@router.get("/history")
async def get_history(user_id: int = None):
    """Get upload history for a user or all uploads"""
    db = SessionLocal()
    try:
        if user_id:
            files = db.query(AudioFile).filter(AudioFile.user_id == user_id).all()
        else:
            files = db.query(AudioFile).all()

        history = [
            {
                "id": f.id,
                "filename": f.original_filename,
                "file_size": f.file_size,
                "language": f.language,
                "uploaded_at": f.uploaded_at.isoformat(),
                "processing_status": f.processing_status,
                "processed_at": f.processed_at.isoformat() if f.processed_at else None
            }
            for f in files
        ]

        return {
            "total": len(history),
            "history": history
        }

    except Exception as e:
        print(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
