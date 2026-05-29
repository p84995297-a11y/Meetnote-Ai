# MeetNote AI 🎙️

**Smart Meeting & Classroom Note Generator**

MeetNote AI is an intelligent audio/video processing application that automatically converts meeting and classroom recordings into structured, actionable notes using advanced AI and NLP technologies.

---

## 🌟 Features

### Core Capabilities
- **🎙️ Speech-to-Text Conversion** - Convert audio and video recordings to accurate text using OpenAI Whisper
- **🧠 Smart Summarization** - Automatically generate concise summaries from long conversations
- **⭐ Key Point Extraction** - Highlight important points with intelligent extraction
- **👤 Speaker Identification** - Identify and track different speakers in recordings
- **🔊 Background Noise Removal** - Advanced noise reduction for cleaner transcriptions
- **🌐 Multi-Language Support** - Support for 12+ languages including:
  - English, Hindi, Kannada, Tamil, Telugu, Malayalam
  - French, Spanish, German, Japanese, Korean, Chinese (Simplified)
- **📁 Large File Support** - Process audio/video files up to 1GB+
- **📄 PDF Export** - Download notes as professionally formatted PDF documents
- **📜 History Tracking** - View and manage all previous uploads and results
- **⚡ Fast Processing** - Optimized AI models for quick transcription
- **🗄️ Secure Storage** - All results securely stored in database

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **Python 3.8+** - Core programming language
- **OpenAI Whisper** - Speech recognition and transcription
- **Faster Whisper** - Optimized Whisper implementation
- **spaCy** - NLP for text processing and analysis
- **NLTK** - Natural Language Toolkit for processing
- **librosa** - Audio processing and analysis
- **noisereduce** - Background noise elimination
- **WeasyPrint** - PDF generation
- **SQLAlchemy** - Database ORM
- **deep-translator** - Multi-language translation

### Frontend
- **HTML5** - Semantic markup (35.6%)
- **CSS3** - Modern styling (28%)
- **JavaScript** - Dynamic interactions
- **Responsive Design** - Mobile-first approach

### Infrastructure
- **Uvicorn** - ASGI web server
- **Python-multipart** - File upload handling
- **Requests** - HTTP client library

---

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- FFmpeg (for audio/video processing)
- 2GB RAM minimum (4GB+ recommended)
- 500MB disk space

### Python Dependencies
See `requirements.txt` for the complete list of 80+ dependencies including:
- FastAPI & Uvicorn
- OpenAI Whisper & Faster Whisper
- spaCy with language models
- librosa, scipy, numpy
- WeasyPrint for PDF generation
- SQLAlchemy for database operations
- And many more...

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/p84995297-a11y/Meetnote-Ai.git
cd Meetnote-Ai
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install FFmpeg
```bash
# Windows (using Chocolatey)
choco install ffmpeg

# macOS (using Homebrew)
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Download Whisper Model (Optional)
```bash
python -m whisper --model base  # Downloads base model
```

### 6. Environment Configuration
Create a `.env` file in the root directory:
```env
# Backend Configuration
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=False

# Database
DATABASE_URL=sqlite:///./meetnote.db

# File Upload
MAX_FILE_SIZE=1073741824  # 1GB in bytes
UPLOAD_DIR=./uploads
TEMP_DIR=./temp

# Whisper Configuration
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
LANGUAGE_DEFAULT=en

# API Keys (if needed)
OPENAI_API_KEY=your_key_here
```

### 7. Run the Backend Server
```bash
# Development
python -m uvicorn main:app --reload

# Production
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 8. Access the Application
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8000/dashboard

---

## 🚀 Usage

### Via Web Interface
1. Navigate to the Dashboard
2. Upload an audio or video file (MP3, MP4, WAV, etc.)
3. Select the language of the recording
4. Click "Generate Notes"
5. Wait for processing to complete
6. View transcript, summary, and key points
7. Download as text or PDF

### API Endpoints

#### Upload & Generate Notes
```
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: (audio/video file)
- language: (language code, e.g., "en", "hi", "fr")

Response:
{
  "transcript": "...",
  "summary": "...",
  "key_points": ["point1", "point2", ...],
  "speakers": ["Speaker 1", "Speaker 2", ...],
  "duration": 3600
}
```

#### Get History
```
GET /history

Response:
{
  "history": [
    {
      "filename": "meeting.mp4",
      "summary": "...",
      "created_at": "2024-05-29T10:00:00"
    }
  ]
}
```

#### Ask Chatbot
```
POST /chatbot
Content-Type: application/json

Body:
{
  "question": "What were the main topics discussed?",
  "transcript": "..."
}

Response:
{
  "response": "..."
}
```

#### Download PDF
```
POST /download-pdf-from-json
Content-Type: application/json

Body:
{
  "transcript": "...",
  "summary": "...",
  "key_points": ["point1", "point2", ...]
}

Response: PDF file
```

---

## 📁 Project Structure

```
meetnote-ai/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── routes/              # API endpoints
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   └── config.py            # Configuration settings
├── frontend/
│   ├── index.html           # Landing page
│   ├── dashboard.html       # Main dashboard
│   ├── login.html           # Authentication
│   ├── register.html        # User registration
│   ├── features.html        # Features page
│   ├── history.html         # Upload history
│   ├── chatbot.html         # AI chatbot interface
│   ├── admin.html           # Admin panel
│   ├── users.html           # User management
│   ├── notes.html           # Notes management
│   ├── css/
│   │   └── style.css        # Global styles
│   └── js/
│       └── main.js          # Frontend logic
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

---

## 🔐 Security Features

- Secure file upload validation
- Input sanitization and validation
- CORS configuration
- Rate limiting (recommended)
- User authentication via JWT tokens
- Password hashing and encryption
- Secure database connections

---

## 🎯 Use Cases

### Educational Institutions
- Automatically generate lecture notes
- Create study materials from recordings
- Accessibility support for deaf/hard of hearing students

### Business & Meetings
- Meeting minutes generation
- Decision tracking and documentation
- Multi-language meeting support

### Content Creation
- Podcast transcription
- Interview documentation
- Video content summarization

### Research & Academia
- Interview transcription
- Research session notes
- Multilingual documentation

---

## ⚡ Performance Optimization

- **Whisper Model Selection**: Use `tiny` or `base` for speed, `medium` for accuracy
- **Batch Processing**: Process multiple files efficiently
- **Caching**: Implement result caching for repeated queries
- **Async Processing**: Non-blocking file uploads and processing
- **GPU Support**: Utilize GPU for faster transcription (CUDA/ROCm)

---

## 🐛 Troubleshooting

### Common Issues

#### "No module named 'whisper'"
```bash
pip install openai-whisper
```

#### "FFmpeg not found"
- Install FFmpeg from https://ffmpeg.org/download.html
- Add to system PATH

#### "CUDA not found" (GPU support)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Large file processing timeout
- Increase server timeout in configuration
- Split large files before processing
- Use faster Whisper implementation

#### Database errors
```bash
# Reset database
rm meetnote.db
```

---

## 📊 Supported Languages

| Code | Language |
|------|----------|
| en | English |
| hi | Hindi |
| kn | Kannada |
| ta | Tamil |
| te | Telugu |
| ml | Malayalam |
| fr | French |
| es | Spanish |
| de | German |
| ja | Japanese |
| ko | Korean |
| zh-CN | Chinese (Simplified) |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Author

**p84995297-a11y**

- GitHub: [@p84995297-a11y](https://github.com/p84995297-a11y)

---

## 📞 Support & Contact

For issues, feature requests, or contributions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review project discussions

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI Whisper Guide](https://github.com/openai/whisper)
- [spaCy NLP](https://spacy.io/)
- [Python Audio Processing](https://librosa.org/)

---

## 🔮 Future Enhancements

- [ ] Real-time transcription support
- [ ] Advanced speaker diarization
- [ ] Custom model training
- [ ] API key authentication
- [ ] Webhook notifications
- [ ] Batch processing API
- [ ] Mobile application
- [ ] Cloud deployment templates
- [ ] Integration with calendar apps
- [ ] Advanced search and filtering

---

## 📈 Statistics

- **Language Composition**: Python (36.4%), HTML (35.6%), CSS (28%)
- **Max File Size**: 1GB+
- **Supported Languages**: 12+
- **Processing Speed**: Varies by file size and model (tiny: fastest, large: most accurate)

---

**Made with ❤️ for better meetings and note-taking**
