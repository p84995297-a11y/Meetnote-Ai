# ============================================
# Database Configuration & Models
# ============================================
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from config import get_settings

settings = get_settings()

# ============================================
# Database Engine Setup
# ============================================
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================
# Database Models
# ============================================

class User(Base):
    """User model for authentication and tracking"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # user, student, teacher, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class AudioFile(Base):
    """Model to track uploaded audio/video files"""
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer)  # in bytes
    duration = Column(Float)  # in seconds
    language = Column(String(10), default="en")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)


class TranscriptNote(Base):
    """Model to store generated transcripts and notes"""
    __tablename__ = "transcript_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    audio_file_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    transcript_language = Column(String(10), default="en")
    summary = Column(Text, nullable=True)
    summary_language = Column(String(10), default="en")
    key_points = Column(Text, nullable=True)  # JSON string
    speakers = Column(Text, nullable=True)  # JSON string
    duration = Column(Float)  # in seconds
    word_count = Column(Integer, default=0)
    generated_at = Column(DateTime, default=datetime.utcnow)
    language_translated_to = Column(String(10), nullable=True)


class PDFExport(Base):
    """Model to track PDF exports"""
    __tablename__ = "pdf_exports"
    
    id = Column(Integer, primary_key=True, index=True)
    transcript_note_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True)
    pdf_filename = Column(String(255), nullable=False)
    pdf_path = Column(String(512), nullable=False)
    file_size = Column(Integer)  # in bytes
    generated_at = Column(DateTime, default=datetime.utcnow)
    downloaded_count = Column(Integer, default=0)
    language = Column(String(10), default="en")


class ProcessingHistory(Base):
    """Model to track processing history for analytics"""
    __tablename__ = "processing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    audio_file_id = Column(Integer, nullable=True)
    action = Column(String(100))  # upload, transcribe, translate, summarize, export_pdf
    status = Column(String(50))  # success, failure
    duration_seconds = Column(Float)  # processing time
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)  # JSON string for extra info


# ============================================
# Database Initialization
# ============================================

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# Database Session Helper
# ============================================

class DatabaseSession:
    """Context manager for database operations"""
    
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        if exc_type:
            return False
        return True


# Initialize database on import
if not os.path.exists(settings.UPLOAD_DIR):
    init_db()
