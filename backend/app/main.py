import threading
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.database import engine, Base, db_type
from app.routers import moderation, slang, analytics, warning
from app.services.classifier import load_transformer_model
from app.services.slang_monitor import SlangMonitorService
from app.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bhashashield.main")

# Auto-create tables on startup
logger.info(f"Initializing database tables on {db_type}...")
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description="Explainable Regional Language Safety Intelligence Engine for Indian Languages (Tamil, Telugu, Hindi)"
)

# Enable CORS for frontend Vite/React (usually port 5173) and Streamlit (usually port 8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev environments. Restrict in production.
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Register Routers
app.include_router(moderation.router, prefix=config.API_PREFIX)
app.include_router(slang.router, prefix=config.API_PREFIX)
app.include_router(analytics.router, prefix=config.API_PREFIX)
app.include_router(warning.router, prefix=config.API_PREFIX)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": config.PROJECT_NAME,
        "version": config.VERSION,
        "database": db_type,
        "features": {
            "transliteration": ["Tamil", "Telugu", "Hindi"],
            "explainability": "Enabled (Token Highlights + Reasoning)",
            "slang_monitoring": "Active",
            "early_warning": "Active"
        }
    }

# Non-blocking loading of heavy ML models in background
@app.on_event("startup")
def startup_event():
    logger.info("Application starting up...")
    thread = threading.Thread(target=load_transformer_model)
    thread.start()
