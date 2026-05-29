# ============================================
# Translation Module for Multi-Language Support
# ============================================
from typing import Dict, List

try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    GoogleTranslator = None

try:
    from googletrans import Translator as GoogleTranslatorFallback
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    GoogleTranslatorFallback = None


# Language mapping
LANGUAGE_MAP = {
    "en": ("en", "English"),
    "hi": ("hi", "Hindi"),
    "kn": ("kn", "Kannada"),
    "ta": ("ta", "Tamil"),
    "te": ("te", "Telugu"),
    "ml": ("ml", "Malayalam"),
    "fr": ("fr", "French"),
    "es": ("es", "Spanish"),
    "de": ("de", "German"),
    "ja": ("ja", "Japanese"),
    "ko": ("ko", "Korean"),
    "zh-CN": ("zh-CN", "Chinese (Simplified)"),
    "zh": ("zh-CN", "Chinese (Simplified)"),
    "pt": ("pt", "Portuguese"),
    "ru": ("ru", "Russian"),
    "ar": ("ar", "Arabic"),
}

# Maximum characters for batch translation
MAX_CHARS_PER_REQUEST = 5000


def _get_language_code(language: str) -> str:
    """Convert language code to standard format"""
    lang = language.lower().strip()
    
    if lang in LANGUAGE_MAP:
        return LANGUAGE_MAP[lang][0]
    
    # Fallback
    return "en"


def _chunk_text(text: str, max_chars: int = MAX_CHARS_PER_REQUEST) -> List[str]:
    """Split text into chunks for translation"""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences to maintain context
    sentences = text.split('. ')
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += '. ' + sentence
            else:
                current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to target language
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'hi', 'fr', 'es')
    
    Returns:
        Translated text
    """
    
    # Validate input
    if not text or len(text.strip()) == 0:
        return text
    
    # Get language code
    target_lang = _get_language_code(target_language)
    
    # If already in target language, return as is
    if target_lang == "en" or target_language == "en":
        return text
    
    try:
        # Try deep_translator first (more reliable)
        if DEEP_TRANSLATOR_AVAILABLE:
            return _translate_with_deep_translator(text, target_lang)
        
        # Fallback to googletrans
        elif GOOGLETRANS_AVAILABLE:
            return _translate_with_googletrans(text, target_lang)
        
        else:
            print("⚠ Translation library not available. Returning original text.")
            return text
    
    except Exception as e:
        print(f"⚠ Translation error: {e}")
        return text


def _translate_with_deep_translator(text: str, target_lang: str) -> str:
    """Translate using deep_translator library"""
    try:
        chunks = _chunk_text(text)
        translated_chunks = []
        
        translator = GoogleTranslator(source='auto', target=target_lang)
        
        for chunk in chunks:
            try:
                translated = translator.translate(chunk)
                translated_chunks.append(translated)
            except Exception as e:
                print(f"⚠ Chunk translation error: {e}")
                translated_chunks.append(chunk)
        
        return ' '.join(translated_chunks)
    
    except Exception as e:
        print(f"✗ deep_translator error: {e}")
        raise


def _translate_with_googletrans(text: str, target_lang: str) -> str:
    """Translate using googletrans library (fallback)"""
    try:
        translator = GoogleTranslatorFallback()
        chunks = _chunk_text(text)
        translated_chunks = []
        
        for chunk in chunks:
            try:
                result = translator.translate(chunk, src_language='auto', dest_language=target_lang)
                translated_chunks.append(result['text'])
            except Exception as e:
                print(f"⚠ Chunk translation error: {e}")
                translated_chunks.append(chunk)
        
        return ' '.join(translated_chunks)
    
    except Exception as e:
        print(f"✗ googletrans error: {e}")
        raise


def translate_list(items: List[str], target_language: str) -> List[str]:
    """
    Translate a list of strings
    
    Args:
        items: List of strings to translate
        target_language: Target language code
    
    Returns:
        List of translated strings
    """
    
    target_lang = _get_language_code(target_language)
    
    if target_lang == "en":
        return items
    
    translated = []
    for item in items:
        try:
            translated.append(translate_text(item, target_language))
        except Exception as e:
            print(f"⚠ Translation error for item: {e}")
            translated.append(item)
    
    return translated


def batch_translate(texts: Dict[str, str], target_language: str) -> Dict[str, str]:
    """
    Translate multiple texts with keys
    
    Args:
        texts: Dictionary of {key: text} to translate
        target_language: Target language code
    
    Returns:
        Dictionary of translated texts with same keys
    """
    
    target_lang = _get_language_code(target_language)
    
    if target_lang == "en":
        return texts
    
    translated = {}
    
    for key, text in texts.items():
        try:
            translated[key] = translate_text(text, target_language)
        except Exception as e:
            print(f"⚠ Batch translation error for '{key}': {e}")
            translated[key] = text
    
    return translated


def detect_language(text: str) -> str:
    """
    Detect language of text
    
    Args:
        text: Text to detect language
    
    Returns:
        Language code
    """
    
    try:
        if GOOGLETRANS_AVAILABLE:
            translator = GoogleTranslatorFallback()
            result = translator.detect(text)
            return result['language']
    except Exception as e:
        print(f"⚠ Language detection error: {e}")
    
    return "en"  # Default to English


def get_supported_languages() -> Dict[str, str]:
    """Get all supported languages"""
    return {lang: name for lang, (code, name) in LANGUAGE_MAP.items()}
