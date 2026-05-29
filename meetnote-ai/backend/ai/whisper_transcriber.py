import os

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
        except Exception as e:
            raise RuntimeError(f"Whisper import failed: {e}")

        try:
            _whisper_model = whisper.load_model("tiny")
        except Exception as e:
            raise RuntimeError(f"Whisper model load failed: {e}")

    return _whisper_model


def transcribe_audio(file_path, language=None):
    model = get_whisper_model()
    kwargs = {}
    if language:
        kwargs["language"] = language

    result = model.transcribe(file_path, **kwargs)
    return result.get("text", "")