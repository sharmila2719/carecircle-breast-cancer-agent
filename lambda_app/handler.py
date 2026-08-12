"""
AWS Lambda Handler for CareCircle API.
Self-contained FastAPI application wrapped with Mangum for Lambda + API Gateway.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Optional
from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="CareCircle API",
    description="Breast Cancer Screening & Care Coordination Agent - Serverless on AWS Lambda",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request Models
# ============================================================

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


class ChatRequest(BaseModel):
    message: str
    patient_id: Optional[int] = None


# ============================================================
# Risk Assessment Logic
# ============================================================

def calculate_risk_score(
    age: int,
    family_history: bool = False,
    genetic_markers: str = "",
    previous_biopsies: int = 0,
    breast_density: str = "scattered",
    hormone_therapy: bool = False,
    bmi: float = 25.0,
    smoking_history: bool = False,
    alcohol_consumption: str = "none",
    age_first_period: int = 12,
    age_first_birth: int = 25,
) -> dict:
    score = 0.0
    risk_factors = []

    if age >= 70:
        score += 25
        risk_factors.append({"factor": "Age 70+", "contribution": 25, "detail": "Highest age-related risk"})
    elif age >= 60:
        score += 20
        risk_factors.append({"factor": "Age 60-69", "contribution": 20, "detail": "High age-related risk"})
    elif age >= 50:
        score += 15
        risk_factors.append({"factor": "Age 50-59", "contribution": 15, "detail": "Moderate age-related risk"})
    elif age >= 40:
        score += 10
        risk_factors.append({"factor": "Age 40-49", "contribution": 10, "detail": "Moderate risk age group"})
    else:
        score += 5
        risk_factors.append({"factor": "Age <40", "contribution": 5, "detail": "Lower age-related risk"})

    if family_history:
        score += 20
        risk_factors.append({"factor": "Family History", "contribution": 20, "detail": "First-degree relative with breast cancer"})

    if genetic_markers:
        markers = genetic_markers.upper()
        if "BRCA1" in markers or "BRCA2" in markers:
            score += 25
            risk_factors.append({"factor": "BRCA Mutation", "contribution": 25, "detail": f"Carrier of {genetic_markers}"})
        elif markers:
            score += 10
            risk_factors.append({"factor": "Other Genetic Markers", "contribution": 10, "detail": f"Markers: {genetic_markers}"})

    if previous_biopsies > 0:
        biopsy_score = min(previous_biopsies * 4, 10)
        score += biopsy_score
        risk_factors.append({"factor": "Previous Biopsies", "contribution": biopsy_score, "detail": f"{previous_biopsies} previous biopsies"})

    density_scores = {"fatty": 0, "scattered": 5, "heterogeneous": 10, "dense": 15}
    density_score = density_scores.get(breast_density.lower(), 5)
    if density_score > 0:
        score += density_score
        risk_factors.append({"factor": "Breast Density", "contribution": density_score, "detail": f"{breast_density.capitalize()} breast tissue"})

    if hormone_therapy:
        score += 8
        risk_factors.append({"factor": "Hormone Therapy", "contribution": 8, "detail": "History of hormone replacement therapy"})

    if age >= 50 and bmi >= 30:
        score += 5
        risk_factors.append({"factor": "Elevated BMI", "contribution": 5, "detail": f"BMI {bmi:.1f} (postmenopausal)"})

    if smoking_history:
        score += 3
        risk_factors.append({"factor": "Smoking History", "contribution": 3, "detail": "Past or current smoking"})

    alcohol_scores = {"none": 0, "light": 2, "moderate": 4, "heavy": 6}
    alc_score = alcohol_scores.get(alcohol_consumption.lower(), 0)
    if alc_score > 0:
        score += alc_score
        risk_factors.append({"factor": "Alcohol Consumption", "contribution": alc_score, "detail": f"{alcohol_consumption.capitalize()} consumption"})

    if age_first_period < 12:
        score += 3
        risk_factors.append({"factor": "Early Menarche", "contribution": 3, "detail": f"First period at age {age_first_period}"})

    if age_first_birth > 30 or age_first_birth == 0:
        score += 4
        risk_factors.append({"factor": "Late/No First Birth", "contribution": 4, "detail": "First birth after 30 or nulliparous"})

    max_possible = 124
    normalized_score = min((score / max_possible) * 100, 100)

    if normalized_score >= 60:
        risk_category = "very_high"
        recommendation = "Enhanced screening with annual mammogram + MRI. Consider genetic counseling."
    elif normalized_score >= 40:
        risk_category = "high"
        recommendation = "Annual mammogram recommended. Consider supplemental MRI screening."
    elif normalized_score >= 20:
        risk_category = "moderate"
        recommendation = "Annual or biennial mammogram based on age. Regular clinical breast exams."
    else:
        risk_category = "low"
        recommendation = "Follow standard screening guidelines. Biennial mammogram starting at age 40-50."

    return {
        "risk_score": round(normalized_score, 1),
        "risk_category": risk_category,
        "recommendation": recommendation,
        "risk_factors": risk_factors,
        "total_raw_score": score,
    }


# ============================================================
# Screening Scheduler Logic
# ============================================================

_screening_store = []
_schedule_counter = 0


def schedule_screening_fn(patient_id, screening_type, preferred_date, facility="", provider="", notes=""):
    global _schedule_counter
    valid_types = ["mammogram", "mri", "ultrasound", "clinical_exam", "3d_mammogram", "biopsy"]
    if screening_type.lower() not in valid_types:
        return {"success": False, "error": f"Invalid type. Must be: {', '.join(valid_types)}"}

    try:
        scheduled_date = datetime.strptime(preferred_date, "%Y-%m-%d")
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}

    if scheduled_date.date() < datetime.now().date():
        return {"success": False, "error": "Cannot schedule in the past."}

    _schedule_counter += 1
    appointment = {
        "id": _schedule_counter,
        "patient_id": patient_id,
        "screening_type": screening_type.lower(),
        "scheduled_date": preferred_date,
        "facility": facility,
        "provider": provider,
        "status": "scheduled",
        "notes": notes,
    }
    _screening_store.append(appointment)

    prep = {
        "mammogram": {"title": "Mammogram Preparation", "instructions": ["No deodorant or powder day of exam", "Wear two-piece outfit", "Schedule 1-2 weeks after period"], "duration": "15-30 min"},
        "mri": {"title": "Breast MRI Preparation", "instructions": ["Inform of metal implants", "May need to fast 4 hours", "Remove all jewelry"], "duration": "30-60 min"},
        "ultrasound": {"title": "Ultrasound Preparation", "instructions": ["No special prep needed", "Wear two-piece outfit"], "duration": "15-30 min"},
    }

    return {
        "success": True,
        "appointment": appointment,
        "preparation": prep.get(screening_type.lower(), prep["mammogram"]),
        "message": f"Screening scheduled for {preferred_date} at {facility}",
    }


# ============================================================
# Care Plan Logic
# ============================================================

def generate_care_plan_fn(patient_id, risk_category, age, risk_score, risk_factors="[]"):
    today = datetime.now()
    try:
        factors = json.loads(risk_factors) if risk_factors else []
    except json.JSONDecodeError:
        factors = []

    screening_plan = {}
    if risk_category in ["very_high", "high"]:
        screening_plan = {
            "mammogram": {"frequency": "Annual", "next_due": (today + timedelta(days=180)).strftime("%Y-%m-%d")},
            "mri": {"frequency": "Annual", "next_due": (today + timedelta(days=90)).strftime("%Y-%m-%d")},
            "clinical_exam": {"frequency": "Every 6 months", "next_due": (today + timedelta(days=60)).strftime("%Y-%m-%d")},
        }
    else:
        screening_plan = {
            "mammogram": {"frequency": "Annual" if age >= 40 else "Discuss at 40", "next_due": (today + timedelta(days=365)).strftime("%Y-%m-%d")},
            "clinical_exam": {"frequency": "Annual", "next_due": (today + timedelta(days=365)).strftime("%Y-%m-%d")},
        }

    tasks = [
        {"title": "Review care plan with provider", "due": (today + timedelta(days=14)).strftime("%Y-%m-%d"), "priority": "high"},
        {"title": "Schedule next screening", "due": (today + timedelta(days=30)).strftime("%Y-%m-%d"), "priority": "high"},
        {"title": "Complete self-exam education", "due": (today + timedelta(days=7)).strftime("%Y-%m-%d"), "priority": "medium"},
        {"title": "Start exercise routine (150 min/week)", "due": (today + timedelta(days=14)).strftime("%Y-%m-%d"), "priority": "medium"},
    ]

    if risk_category in ["high", "very_high"]:
        tasks.append({"title": "Genetic counseling consultation", "due": (today + timedelta(days=21)).strftime("%Y-%m-%d"), "priority": "high"})

    return {
        "success": True,
        "care_plan": {
            "patient_id": patient_id,
            "title": f"Breast Health Care Plan - {risk_category.replace('_', ' ').title()} Risk",
            "risk_score": risk_score,
            "risk_category": risk_category,
            "screening_plan": screening_plan,
            "tasks": tasks,
            "lifestyle": [
                "Exercise 150+ minutes per week",
                "Maintain healthy BMI (18.5-24.9)",
                "Limit alcohol to ≤1 drink/day",
                "Eat Mediterranean-style diet",
                "Practice monthly breast self-awareness",
            ],
            "genetic_counseling_recommended": risk_category in ["high", "very_high"],
            "created_at": today.isoformat(),
        },
    }


# ============================================================
# Education Content
# ============================================================

EDUCATION_TOPICS = {
    "breast_self_exam": {
        "title": "Breast Self-Examination Guide",
        "summary": "Monthly self-exam helps you know what's normal for you so you can spot changes early.",
        "key_points": [
            "Perform monthly, 7-10 days after period starts",
            "Use three pressure levels: light, medium, firm",
            "Check visually in mirror and manually lying down",
            "Report any changes to your healthcare provider",
        ],
    },
    "mammogram_overview": {
        "title": "Understanding Mammograms",
        "summary": "Mammograms can detect cancer up to 2 years before a lump can be felt.",
        "key_points": [
            "Takes 15-30 minutes",
            "Some pressure is normal but brief",
            "Annual screening recommended from age 40",
            "BI-RADS 0-6 scoring classifies findings",
        ],
    },
    "risk_factors": {
        "title": "Breast Cancer Risk Factors",
        "summary": "Risk combines non-modifiable factors (age, genetics) and modifiable ones (lifestyle).",
        "key_points": [
            "Age and being female are the two biggest factors",
            "Only 5-10% of cases are hereditary",
            "Dense breasts increase risk and mask tumors",
            "Lifestyle modifications can meaningfully reduce risk",
        ],
    },
    "screening_guidelines": {
        "title": "Screening Guidelines",
        "summary": "Guidelines vary by age and risk. Your provider helps determine the best plan.",
        "key_points": [
            "Average risk: Annual mammogram starting at 40",
            "High risk (>20% lifetime): Mammogram + MRI starting at 30",
            "BRCA carriers: Annual mammogram + MRI from age 25-30",
            "Clinical breast exam recommended annually",
        ],
    },
    "genetic_testing": {
        "title": "Genetic Testing",
        "summary": "Testing identifies inherited mutations that significantly increase risk.",
        "key_points": [
            "BRCA1/BRCA2 carriers have 45-72% lifetime risk",
            "Simple blood or saliva test",
            "Genetic counseling recommended before and after",
            "Negative test doesn't eliminate all risk",
        ],
    },
    "lifestyle_prevention": {
        "title": "Lifestyle Prevention",
        "summary": "Lifestyle changes can reduce breast cancer risk by 10-30%.",
        "key_points": [
            "Exercise 150+ min/week reduces risk 10-20%",
            "Maintain healthy weight (BMI 18.5-24.9)",
            "Limit alcohol to ≤1 drink/day",
            "Quit smoking, especially before age 35",
            "Mediterranean diet associated with lower risk",
        ],
    },
    "early_detection": {
        "title": "Early Detection",
        "summary": "When found early, 5-year survival is 99%. Regular screening saves lives.",
        "key_points": [
            "Localized stage: 99% five-year survival",
            "Mammograms find cancers too small to feel",
            "Early treatment is less aggressive",
            "Don't skip screenings",
        ],
    },
    "dense_breasts": {
        "title": "Breast Density",
        "summary": "About 40-50% of women have dense breasts, which affects both risk and detection.",
        "key_points": [
            "Density is genetic, not related to breast size",
            "Dense tissue appears white on mammograms (like tumors)",
            "Supplemental MRI or 3D mammogram may be recommended",
            "Many states require density notification after mammogram",
        ],
    },
    "myths_facts": {
        "title": "Myths vs Facts",
        "summary": "Separating fact from fiction helps you make informed decisions.",
        "key_points": [
            "MYTH: Only those with family history get it. FACT: 85% have no family history",
            "MYTH: Mammograms cause cancer. FACT: Radiation dose is extremely low",
            "MYTH: A lump means cancer. FACT: 80% of lumps are benign",
            "MYTH: Men can't get breast cancer. FACT: ~2,800 men diagnosed annually in US",
        ],
    },
    "support_resources": {
        "title": "Support Resources",
        "summary": "Support is available at every step of your breast health journey.",
        "key_points": [
            "National Breast Cancer Helpline: 1-800-227-2345",
            "Patient navigators help coordinate care",
            "Financial assistance programs available",
            "Support groups offer community and shared experience",
        ],
    },
}


# ============================================================
# API Routes
# ============================================================

@app.get("/")
async def root():
    return {
        "name": "CareCircle API",
        "version": "1.0.0",
        "description": "Breast Cancer Screening & Care Coordination Agent",
        "deployment": "AWS Lambda + API Gateway (Serverless)",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "risk_assessment": "POST /api/risk-assessment",
            "screening": "POST /api/screening/schedule",
            "care_plan": "POST /api/care-plan/generate",
            "education": "GET /api/education/{topic}",
            "chat": "POST /api/chat",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "CareCircle", "runtime": "AWS Lambda", "version": "1.0.0"}


@app.post("/api/risk-assessment")
async def risk_assessment(request: RiskAssessmentRequest):
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
async def schedule_endpoint(request: ScreeningRequest):
    return schedule_screening_fn(
        patient_id=request.patient_id,
        screening_type=request.screening_type,
        preferred_date=request.preferred_date,
        facility=request.facility,
        provider=request.provider,
        notes=request.notes,
    )


@app.get("/api/screening/upcoming/{patient_id}")
async def upcoming(patient_id: int):
    results = [a for a in _screening_store if a["patient_id"] == patient_id]
    return {"patient_id": patient_id, "upcoming_count": len(results), "appointments": results}


@app.post("/api/care-plan/generate")
async def create_care_plan(request: CarePlanRequest):
    return generate_care_plan_fn(
        patient_id=request.patient_id,
        risk_category=request.risk_category,
        age=request.age,
        risk_score=request.risk_score,
        risk_factors=request.risk_factors,
    )


@app.get("/api/education")
async def list_topics():
    return {"topics": [{"id": k, "title": v["title"]} for k, v in EDUCATION_TOPICS.items()]}


@app.get("/api/education/{topic}")
async def get_education(topic: str):
    if topic in EDUCATION_TOPICS:
        return {"success": True, **EDUCATION_TOPICS[topic]}
    return {"success": False, "error": f"Topic '{topic}' not found", "available": list(EDUCATION_TOPICS.keys())}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    msg = request.message.lower()
    if any(w in msg for w in ["risk", "assess", "score"]):
        resp = "I can assess your risk! Use POST /api/risk-assessment with your health details."
    elif any(w in msg for w in ["schedule", "mammogram", "screening", "appointment"]):
        resp = "I can schedule screenings! Use POST /api/screening/schedule with patient_id, screening_type, and preferred_date."
    elif any(w in msg for w in ["care plan", "plan"]):
        resp = "I can generate care plans! First do a risk assessment, then POST /api/care-plan/generate."
    elif any(w in msg for w in ["education", "learn", "info"]):
        resp = "I have education on 10 topics! Use GET /api/education to see all topics."
    else:
        resp = "Hello! I'm CareCircle. I help with: risk assessment, screening scheduling, care plans, and education. How can I help?"
    return {"success": True, "response": resp}


# ============================================================
# Lambda Handler
# ============================================================

handler = Mangum(app, lifespan="off")
