"""
AWS Lambda Handler for CareCircle API.
Uses Mangum to wrap FastAPI for Lambda + API Gateway deployment.
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.tools.risk_assessment import calculate_risk_score, assess_risk
from src.tools.screening_scheduler import (
    schedule_screening,
    get_upcoming_screenings,
    update_screening_status,
)
from src.tools.care_plan_generator import generate_care_plan, get_care_plan
from src.tools.patient_education import get_educational_content
from src.tools.notification_manager import send_reminder, get_notifications

# Create FastAPI app for Lambda
app = FastAPI(
    title="CareCircle API (Serverless)",
    description="Breast Cancer Screening & Care Coordination Agent - AWS Lambda Deployment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---
from pydantic import BaseModel, Field
from typing import Optional
import json


class RiskAssessmentRequest(BaseModel):
    age: int = Field(..., ge=18, le=120)
    family_history: bool = False
    genetic_markers: str = ""
    previous_biopsies: int = 0
    breast_density: str = "scattered"
    hormone_therapy: bool = False
    bmi: float = 25.0
    smoking_history: bool = False
    alcohol_consumption: str = "none"
    age_first_period: int = 12
    age_first_birth: int = 25


class ScreeningRequest(BaseModel):
    patient_id: int
    screening_type: str
    preferred_date: str
    facility: str = "Community Breast Health Center"
    provider: str = ""
    notes: str = ""


class CarePlanRequest(BaseModel):
    patient_id: int
    risk_category: str
    age: int
    risk_score: float
    risk_factors: str = "[]"
    preferences: str = "{}"


class ChatRequest(BaseModel):
    message: str
    patient_id: Optional[int] = None


# --- Routes ---


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "CareCircle API (Serverless)",
        "version": "1.0.0",
        "description": "Breast Cancer Screening & Care Coordination Agent",
        "status": "active",
        "deployment": "AWS Lambda + API Gateway",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "risk_assessment": "/api/risk-assessment",
            "screening_schedule": "/api/screening/schedule",
            "screening_upcoming": "/api/screening/upcoming/{patient_id}",
            "care_plan_generate": "/api/care-plan/generate",
            "care_plan_get": "/api/care-plan/{patient_id}",
            "education": "/api/education/{topic}",
            "education_list": "/api/education",
        },
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "CareCircle", "runtime": "AWS Lambda"}


@app.post("/api/risk-assessment")
async def risk_assessment(request: RiskAssessmentRequest):
    """Perform breast cancer risk assessment."""
    result = calculate_risk_score(
        age=request.age,
        family_history=request.family_history,
        genetic_markers=request.genetic_markers,
        previous_biopsies=request.previous_biopsies,
        breast_density=request.breast_density,
        hormone_therapy=request.hormone_therapy,
        bmi=request.bmi,
        smoking_history=request.smoking_history,
        alcohol_consumption=request.alcohol_consumption,
        age_first_period=request.age_first_period,
        age_first_birth=request.age_first_birth,
    )
    return {"success": True, "assessment": result}


@app.post("/api/screening/schedule")
async def schedule(request: ScreeningRequest):
    """Schedule a screening appointment."""
    result = schedule_screening(
        patient_id=request.patient_id,
        screening_type=request.screening_type,
        preferred_date=request.preferred_date,
        facility=request.facility,
        provider=request.provider,
        notes=request.notes,
    )
    return result


@app.get("/api/screening/upcoming/{patient_id}")
async def upcoming_screenings(patient_id: int, days_ahead: int = 90):
    """Get upcoming screenings."""
    return get_upcoming_screenings(patient_id=patient_id, days_ahead=days_ahead)


@app.post("/api/care-plan/generate")
async def create_care_plan(request: CarePlanRequest):
    """Generate personalized care plan."""
    result = generate_care_plan(
        patient_id=request.patient_id,
        risk_category=request.risk_category,
        age=request.age,
        risk_score=request.risk_score,
        risk_factors=request.risk_factors,
        preferences=request.preferences,
    )
    return result


@app.get("/api/care-plan/{patient_id}")
async def get_patient_care_plan(patient_id: int):
    """Get care plan for a patient."""
    return get_care_plan(patient_id=patient_id)


@app.get("/api/education")
async def list_topics():
    """List education topics."""
    return {
        "available_topics": [
            {"id": "breast_self_exam", "title": "Breast Self-Examination Guide"},
            {"id": "mammogram_overview", "title": "Understanding Mammograms"},
            {"id": "risk_factors", "title": "Understanding Breast Cancer Risk Factors"},
            {"id": "screening_guidelines", "title": "Breast Cancer Screening Guidelines"},
            {"id": "genetic_testing", "title": "Genetic Testing for Breast Cancer"},
            {"id": "dense_breasts", "title": "Understanding Breast Density"},
            {"id": "lifestyle_prevention", "title": "Lifestyle Factors for Prevention"},
            {"id": "early_detection", "title": "The Importance of Early Detection"},
            {"id": "support_resources", "title": "Support Resources"},
            {"id": "myths_facts", "title": "Breast Cancer: Myths vs. Facts"},
        ]
    }


@app.get("/api/education/{topic}")
async def get_education(topic: str, detail_level: str = "standard"):
    """Get educational content."""
    return get_educational_content(topic=topic, detail_level=detail_level)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint - returns helpful responses based on keywords."""
    message = request.message.lower()

    if any(w in message for w in ["risk", "assess", "score"]):
        response = (
            "I can assess your breast cancer risk. Please provide: age, family_history, "
            "genetic_markers, breast_density, and lifestyle factors. Use the /api/risk-assessment "
            "endpoint with a POST request for a detailed assessment."
        )
    elif any(w in message for w in ["schedule", "appointment", "mammogram", "screening"]):
        response = (
            "I can help schedule a screening. Use the /api/screening/schedule endpoint with: "
            "patient_id, screening_type (mammogram, mri, ultrasound, clinical_exam), "
            "preferred_date (YYYY-MM-DD), and facility."
        )
    elif any(w in message for w in ["care plan", "plan"]):
        response = (
            "I can generate a personalized care plan. First complete a risk assessment, "
            "then use /api/care-plan/generate with your risk results."
        )
    elif any(w in message for w in ["education", "learn", "information"]):
        response = (
            "I have educational content on: breast_self_exam, mammogram_overview, risk_factors, "
            "screening_guidelines, genetic_testing, dense_breasts, lifestyle_prevention, "
            "early_detection, myths_facts, support_resources. Use /api/education/{topic}."
        )
    else:
        response = (
            "Hello! I'm CareCircle, your breast cancer screening coordination agent. "
            "I can help with: risk assessment, screening scheduling, care plans, and education. "
            "How can I assist you?"
        )

    return {"success": True, "response": response}


# Lambda handler via Mangum
handler = Mangum(app, lifespan="off")
