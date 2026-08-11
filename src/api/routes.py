"""
API Routes for CareCircle.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from src.agent.care_agent import create_agent
from src.tools.risk_assessment import calculate_risk_score, assess_risk
from src.tools.screening_scheduler import (
    schedule_screening,
    get_upcoming_screenings,
    update_screening_status,
)
from src.tools.care_plan_generator import generate_care_plan, get_care_plan
from src.tools.patient_education import get_educational_content
from src.tools.notification_manager import send_reminder, get_notifications

router = APIRouter(prefix="/api", tags=["CareCircle"])


# --- Request/Response Models ---


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message to the CareCircle agent")
    patient_id: Optional[int] = Field(None, description="Optional patient context")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    success: bool = True


class RiskAssessmentRequest(BaseModel):
    """Risk assessment request model."""
    age: int = Field(..., ge=18, le=120, description="Patient age")
    family_history: bool = Field(False, description="Family history of breast cancer")
    genetic_markers: str = Field("", description="Known genetic markers (e.g., BRCA1, BRCA2)")
    previous_biopsies: int = Field(0, ge=0, description="Number of previous biopsies")
    breast_density: str = Field("scattered", description="Breast density category")
    hormone_therapy: bool = Field(False, description="History of hormone replacement therapy")
    bmi: float = Field(25.0, ge=10, le=80, description="Body Mass Index")
    smoking_history: bool = Field(False, description="Smoking history")
    alcohol_consumption: str = Field("none", description="Alcohol consumption level")
    age_first_period: int = Field(12, ge=8, le=20, description="Age at first period")
    age_first_birth: int = Field(25, ge=0, le=55, description="Age at first birth (0 if none)")


class ScreeningRequest(BaseModel):
    """Screening scheduling request."""
    patient_id: int = Field(..., description="Patient ID")
    screening_type: str = Field(..., description="Type of screening")
    preferred_date: str = Field(..., description="Preferred date (YYYY-MM-DD)")
    facility: str = Field("Community Breast Health Center", description="Facility name")
    provider: str = Field("", description="Provider name")
    notes: str = Field("", description="Additional notes")


class ScreeningUpdateRequest(BaseModel):
    """Screening status update request."""
    appointment_id: int = Field(..., description="Appointment ID")
    new_status: str = Field(..., description="New status")
    result: str = Field("", description="Result if completed")
    birads_score: int = Field(-1, ge=-1, le=6, description="BI-RADS score")
    notes: str = Field("", description="Additional notes")


class CarePlanRequest(BaseModel):
    """Care plan generation request."""
    patient_id: int = Field(..., description="Patient ID")
    risk_category: str = Field(..., description="Risk category")
    age: int = Field(..., description="Patient age")
    risk_score: float = Field(..., description="Risk score")
    risk_factors: str = Field("[]", description="JSON string of risk factors")
    preferences: str = Field("{}", description="JSON string of patient preferences")


class NotificationRequest(BaseModel):
    """Notification request."""
    patient_id: int = Field(..., description="Patient ID")
    notification_type: str = Field(..., description="Delivery method (email, sms, in_app)")
    category: str = Field(..., description="Notification category")
    message: str = Field(..., description="Message content")
    subject: str = Field("", description="Subject line")
    schedule_time: str = Field("", description="Schedule time (ISO format)")


# --- Chat Endpoint ---


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat with the CareCircle agent.
    The agent can perform risk assessments, schedule screenings,
    generate care plans, and provide educational content.
    """
    try:
        agent = create_agent()
        response = agent.chat(request.message)
        return ChatResponse(response=response, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


# --- Risk Assessment Endpoints ---


@router.post("/risk-assessment")
async def perform_risk_assessment(request: RiskAssessmentRequest):
    """Perform a breast cancer risk assessment."""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Screening Endpoints ---


@router.post("/screening/schedule")
async def schedule_screening_endpoint(request: ScreeningRequest):
    """Schedule a breast cancer screening appointment."""
    try:
        result = schedule_screening(
            patient_id=request.patient_id,
            screening_type=request.screening_type,
            preferred_date=request.preferred_date,
            facility=request.facility,
            provider=request.provider,
            notes=request.notes,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/screening/upcoming/{patient_id}")
async def get_upcoming_screenings_endpoint(patient_id: int, days_ahead: int = 90):
    """Get upcoming screening appointments for a patient."""
    try:
        result = get_upcoming_screenings(patient_id=patient_id, days_ahead=days_ahead)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/screening/status")
async def update_screening_status_endpoint(request: ScreeningUpdateRequest):
    """Update screening appointment status."""
    try:
        result = update_screening_status(
            appointment_id=request.appointment_id,
            new_status=request.new_status,
            result=request.result,
            birads_score=request.birads_score,
            notes=request.notes,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Care Plan Endpoints ---


@router.post("/care-plan/generate")
async def generate_care_plan_endpoint(request: CarePlanRequest):
    """Generate a personalized care plan."""
    try:
        result = generate_care_plan(
            patient_id=request.patient_id,
            risk_category=request.risk_category,
            age=request.age,
            risk_score=request.risk_score,
            risk_factors=request.risk_factors,
            preferences=request.preferences,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/care-plan/{patient_id}")
async def get_care_plan_endpoint(patient_id: int):
    """Get active care plan for a patient."""
    try:
        result = get_care_plan(patient_id=patient_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Education Endpoints ---


@router.get("/education/{topic}")
async def get_education_endpoint(topic: str, detail_level: str = "standard"):
    """Get educational content on a breast health topic."""
    try:
        result = get_educational_content(topic=topic, detail_level=detail_level)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/education")
async def list_education_topics():
    """List available education topics."""
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


# --- Notification Endpoints ---


@router.post("/notifications/send")
async def send_notification_endpoint(request: NotificationRequest):
    """Send a notification to a patient."""
    try:
        result = send_reminder(
            patient_id=request.patient_id,
            notification_type=request.notification_type,
            category=request.category,
            message=request.message,
            subject=request.subject,
            schedule_time=request.schedule_time,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/{patient_id}")
async def get_notifications_endpoint(
    patient_id: int, unread_only: bool = False, category: str = ""
):
    """Get notifications for a patient."""
    try:
        result = get_notifications(
            patient_id=patient_id, unread_only=unread_only, category=category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
