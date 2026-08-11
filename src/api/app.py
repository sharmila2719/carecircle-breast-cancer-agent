"""
CareCircle FastAPI Application.
Provides REST API endpoints for the breast cancer screening agent.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.models.database import init_db
from src.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    print("🩺 CareCircle API started successfully")
    print(f"📡 Running on {settings.APP_HOST}:{settings.APP_PORT}")
    yield
    # Shutdown
    print("👋 CareCircle API shutting down")


app = FastAPI(
    title="CareCircle API",
    description=(
        "Breast Cancer Screening & Care Coordination Agent API. "
        "Powered by AWS Bedrock Strands Agents."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CareCircle API",
        "version": "1.0.0",
        "description": "Breast Cancer Screening & Care Coordination Agent",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "chat": "/api/chat",
            "risk_assessment": "/api/risk-assessment",
            "screening": "/api/screening",
            "care_plan": "/api/care-plan",
            "education": "/api/education",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CareCircle", "version": "1.0.0"}
