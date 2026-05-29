from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

try:
    # When running from project root: `uvicorn backend.main:app`
    from backend.routes.upload_routes import router as upload_router
    from backend.routes.pdf_routes import router as pdf_router
except Exception:
    # When running from the backend folder: `uvicorn main:app`
    from routes.upload_routes import router as upload_router
    from routes.pdf_routes import router as pdf_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(upload_router)
app.include_router(pdf_router)

# Mount static folders so CSS/JS/images are served from backend
base_dir = os.path.dirname(__file__)
frontend_dir = os.path.normpath(os.path.join(base_dir, "..", "frontend"))
static_dir = os.path.join(base_dir, "static")

if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if os.path.isdir(frontend_dir):
    # expose frontend folder under /public so we can serve raw pages if needed
    app.mount("/public", StaticFiles(directory=frontend_dir), name="public")


@app.get("/")
def index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Landing page not found")


@app.get("/dashboard")
def dashboard():
    dashboard_path = os.path.join(frontend_dir, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="Dashboard page not found")


@app.get("/features")
def features():
    features_path = os.path.join(frontend_dir, "features.html")
    if os.path.exists(features_path):
        return FileResponse(features_path)
    raise HTTPException(status_code=404, detail="Features page not found")