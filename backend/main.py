"""CASA MVP — FastAPI application entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.api.applications import router as app_router
from backend.api.chat import router as chat_router
from backend.api.dashboard import router as dash_router
from backend.api.documents import router as doc_router

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CASA — AI Loan Origination System",
    description="Credit Assessment and Servicing Automation API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_router)
app.include_router(chat_router)
app.include_router(dash_router)
app.include_router(doc_router)


@app.on_event("startup")
def startup():
    logger.info(f"Starting {settings.app_name} for {settings.bank_name}")
    init_db()
    logger.info("Database initialized")


@app.get("/")
def root():
    return {"name": settings.app_name, "bank": settings.bank_name, "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
