# ============================================
# Configuration Management
# ============================================
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # ============================================
    # Server Configuration
    # ============================================
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENV: str = os.getenv("ENV", "development")
    
    # ============================================
    # Database Configuration
    # ============================================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./meetnote.db"
    )
    
    # ============================================
    # File Upload Configuration
    # ============================================
    MAX_FILE_SIZE: int = int(
        os.getenv("MAX_FILE_SIZE", 1073741824)  # 1GB
    )
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    ALLOWED_EXTENSIONS: list = [
        "mp3", "mp4", "wav", "m4a", 
        "ogg", "flac", "webm", "avi", "mov"
    ]
    
    # ============================================
    # Whisper Configuration
    # ============================================
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    LANGUAGE_DEFAULT: str = os.getenv("LANGUAGE_DEFAULT", "en")
    DEVICE: str = os.getenv("DEVICE", "cpu")  # cpu, cuda, mps
    
    # ============================================
    # Audio Processing
    # ============================================
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", 16000))
    AUDIO_FORMAT: str = os.getenv("AUDIO_FORMAT", "wav")
    NOISE_REDUCTION_ENABLED: bool = os.getenv(
        "NOISE_REDUCTION_ENABLED", "true"
    ).lower() == "true"
    NOISE_REDUCTION_STRENGTH: float = float(
        os.getenv("NOISE_REDUCTION_STRENGTH", 0.21)
    )
    
    # ============================================
    # PDF Configuration
    # ============================================
    PDF_ENABLE: bool = os.getenv("PDF_ENABLE", "true").lower() == "true"
    PDF_MARGIN: int = int(os.getenv("PDF_MARGIN", 20))
    PDF_PAPER_SIZE: str = os.getenv("PDF_PAPER_SIZE", "A4")
    PDF_ORIENTATION: str = os.getenv("PDF_ORIENTATION", "portrait")
    PDF_OUTPUT_DIR: str = os.getenv("PDF_OUTPUT_DIR", "./pdfs")
    
    # ============================================
    # Language Settings
    # ============================================
    SUPPORTED_LANGUAGES: dict = {
        "en": "English",
        "hi": "Hindi",
        "kn": "Kannada",
        "ta": "Tamil",
        "te": "Telugu",
        "ml": "Malayalam",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "ja": "Japanese",
        "ko": "Korean",
        "zh-CN": "Chinese (Simplified)"
    }
    ENABLE_TRANSLATION: bool = os.getenv(
        "ENABLE_TRANSLATION", "true"
    ).lower() == "true"
    
    # ============================================
    # CORS Configuration
    # ============================================
    CORS_ORIGINS: list = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "*"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # ============================================
    # Performance & Optimization
    # ============================================
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 3600))
    WORKERS: int = int(os.getenv("WORKERS", 4))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 1))
    
    # ============================================
    # Logging Configuration
    # ============================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/meetnote.log")
    
    # ============================================
    # JWT Authentication
    # ============================================
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-in-production-12345"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (cached)"""
    return Settings()


# Create necessary directories on startup
def ensure_directories():
    """Create required directories if they don't exist"""
    settings = get_settings()
    
    directories = [
        settings.UPLOAD_DIR,
        settings.TEMP_DIR,
        settings.PDF_OUTPUT_DIR,
        "./logs",
        "./database"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {directory}")


# Export settings
settings = get_settings()
