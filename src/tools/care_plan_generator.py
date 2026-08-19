"""
Care Plan Generator Tool for CareCircle.
Creates personalized care plans based on risk assessment and patient profile.
"""

import json
from datetime import datetime, timedelta
from typing import Any

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


# In-memory store for demo
_care_plans: list[dict] = []
_plan_counter = 0


@tool
def generate_care_plan(
    patient_id: int,
    risk_category: str,
    age: int,
    risk_score: float,
    risk_factors: str = "[]",
    preferences: str = "{}",
) -> dict[str, Any]:
    """
    Generate a personalized breast cancer care plan based on risk assessment.

    Args:
        patient_id: Patient's unique identifier
        risk_category: Risk category (low, moderate, high, very_high)
        age: Patient's current age
        risk_score: Calculated risk score (0-100)
        risk_factors: JSON string of identified risk factors
        preferences: JSON string of patient preferences (e.g., preferred facilities, language)

    Returns:
        Comprehensive personalized care plan
    """
    global _plan_counter

    try:
        factors = json.loads(risk_factors) if risk_factors else []
        prefs = json.loads(preferences) if preferences else {}
    except json.JSONDecodeError:
        factors = []
        prefs = {}

    _plan_counter += 1
    today = datetime.now()

    # Generate screening schedule based on risk
    screening_schedule = _generate_screening_schedule(risk_category, age, today)

    # Generate lifestyle recommendations
    lifestyle_recs = _generate_lifestyle_recommendations(risk_category, factors)

    # Generate care tasks
    tasks = _generate_care_tasks(risk_category, age, factors, today)

    # Determine if genetic counseling is needed
    needs_genetic_counseling = _should_recommend_genetic_counseling(risk_category, factors)

    care_plan = {
        "id": _plan_counter,
        "patient_id": patient_id,
        "title": f"Personalized Breast Health Care Plan - {risk_category.replace('_', ' ').title()} Risk",
        "created_at": today.isoformat(),
        "status": "active",
        "risk_summary": {
            "score": risk_score,
            "category": risk_category,
            "key_factors": [f.get("factor", f) if isinstance(f, dict) else f for f in factors[:5]],
        },
        "screening_plan": screening_schedule,
        "lifestyle_recommendations": lifestyle_recs,
        "care_tasks": tasks,
        "genetic_counseling": {
            "recommended": needs_genetic_counseling,
            "reason": _genetic_counseling_reason(factors) if needs_genetic_counseling else None,
        },
        "support_resources": _get_support_resources(risk_category),
        "review_schedule": {
            "next_review": (today + timedelta(days=90)).strftime("%Y-%m-%d"),
            "frequency": "Quarterly" if risk_category in ["high", "very_high"] else "Semi-annually",
        },
        "patient_preferences": prefs,
    }

    _care_plans.append(care_plan)

    return {
        "success": True,
        "care_plan": care_plan,
        "message": f"Personalized care plan generated for patient {patient_id} based on {risk_category} risk profile.",
        "immediate_actions": _get_immediate_actions(risk_category, age),
    }


@tool
def get_care_plan(patient_id: int) -> dict[str, Any]:
    """
    Retrieve the active care plan for a patient.

    Args:
        patient_id: Patient's unique identifier

    Returns:
        Active care plan details or message if none found
    """
    active_plans = [
        p for p in _care_plans if p["patient_id"] == patient_id and p["status"] == "active"
    ]

    if not active_plans:
        return {
            "success": False,
            "message": f"No active care plan found for patient {patient_id}.",
            "recommendation": "Run a risk assessment to generate a personalized care plan.",
        }

    # Return most recent active plan
    latest_plan = active_plans[-1]

    return {
        "success": True,
        "care_plan": latest_plan,
        "message": f"Active care plan found for patient {patient_id}.",
    }


def _generate_screening_schedule(risk_category: str, age: int, start_date: datetime) -> dict:
    """Generate screening schedule based on risk and age."""
    schedules = {
        "very_high": {
            "mammogram": {
                "frequency": "Every 12 months",
                "next_due": (start_date + timedelta(days=180)).strftime("%Y-%m-%d"),
                "modality": "3D Mammogram (Tomosynthesis)",
            },
            "mri": {
                "frequency": "Every 12 months (alternating with mammogram)",
                "next_due": (start_date + timedelta(days=90)).strftime("%Y-%m-%d"),
                "modality": "Contrast-enhanced breast MRI",
            },
            "clinical_exam": {
                "frequency": "Every 6 months",
                "next_due": (start_date + timedelta(days=60)).strftime("%Y-%m-%d"),
            },
            "self_exam": {"frequency": "Monthly", "education_provided": True},
        },
        "high": {
            "mammogram": {
                "frequency": "Every 12 months",
                "next_due": (start_date + timedelta(days=365)).strftime("%Y-%m-%d"),
                "modality": "3D Mammogram (Tomosynthesis)",
            },
            "mri": {
                "frequency": "Annual (supplemental)",
                "next_due": (start_date + timedelta(days=180)).strftime("%Y-%m-%d"),
                "modality": "Breast MRI",
            },
            "clinical_exam": {
                "frequency": "Every 6-12 months",
                "next_due": (start_date + timedelta(days=180)).strftime("%Y-%m-%d"),
            },
            "self_exam": {"frequency": "Monthly", "education_provided": True},
        },
        "moderate": {
            "mammogram": {
                "frequency": "Every 12 months" if age >= 40 else "Discuss with provider at age 40",
                "next_due": (start_date + timedelta(days=365)).strftime("%Y-%m-%d"),
                "modality": "Standard or 3D Mammogram",
            },
            "clinical_exam": {
                "frequency": "Annual",
                "next_due": (start_date + timedelta(days=365)).strftime("%Y-%m-%d"),
            },
            "self_exam": {"frequency": "Monthly awareness", "education_provided": True},
        },
        "low": {
            "mammogram": {
                "frequency": "Every 1-2 years" if age >= 50 else "Begin at age 40-50",
                "next_due": (start_date + timedelta(days=730 if age >= 50 else 365)).strftime(
                    "%Y-%m-%d"
                ),
                "modality": "Standard Mammogram",
            },
            "clinical_exam": {
                "frequency": "Annual",
                "next_due": (start_date + timedelta(days=365)).strftime("%Y-%m-%d"),
            },
            "self_exam": {"frequency": "Monthly awareness", "education_provided": True},
        },
    }

    return schedules.get(risk_category, schedules["moderate"])


def _generate_lifestyle_recommendations(risk_category: str, factors: list) -> list[dict]:
    """Generate personalized lifestyle recommendations."""
    recommendations = []

    # Universal recommendations
    recommendations.append({
        "category": "Physical Activity",
        "recommendation": "Aim for at least 150 minutes of moderate aerobic activity per week",
        "detail": "Regular exercise can reduce breast cancer risk by 10-20%",
        "priority": "high",
    })

    recommendations.append({
        "category": "Nutrition",
        "recommendation": "Follow a balanced diet rich in fruits, vegetables, and whole grains",
        "detail": "Mediterranean diet pattern associated with reduced breast cancer risk",
        "priority": "high",
    })

    recommendations.append({
        "category": "Weight Management",
        "recommendation": "Maintain a healthy BMI (18.5-24.9)",
        "detail": "Excess body weight increases postmenopausal breast cancer risk",
        "priority": "high" if risk_category in ["high", "very_high"] else "medium",
    })

    # Factor-specific recommendations
    factor_names = [f.get("factor", "") if isinstance(f, dict) else str(f) for f in factors]

    if any("alcohol" in f.lower() for f in factor_names):
        recommendations.append({
            "category": "Alcohol",
            "recommendation": "Limit alcohol to no more than 1 drink per day, or eliminate entirely",
            "detail": "Even moderate alcohol consumption increases breast cancer risk",
            "priority": "high",
        })

    if any("smoking" in f.lower() for f in factor_names):
        recommendations.append({
            "category": "Tobacco",
            "recommendation": "Quit smoking - resources and cessation programs available",
            "detail": "Smoking is linked to increased breast cancer risk, especially in premenopausal women",
            "priority": "high",
        })

    if any("hormone" in f.lower() for f in factor_names):
        recommendations.append({
            "category": "Hormone Therapy",
            "recommendation": "Discuss HRT duration and alternatives with your provider",
            "detail": "Limiting HRT use to less than 5 years may reduce associated risk",
            "priority": "high",
        })

    # Mental health and stress management
    recommendations.append({
        "category": "Stress Management",
        "recommendation": "Practice stress reduction techniques (meditation, yoga, deep breathing)",
        "detail": "Chronic stress may impact immune function and overall health",
        "priority": "medium",
    })

    # Sleep
    recommendations.append({
        "category": "Sleep",
        "recommendation": "Aim for 7-9 hours of quality sleep per night",
        "detail": "Disrupted sleep patterns may be associated with increased cancer risk",
        "priority": "medium",
    })

    return recommendations


def _generate_care_tasks(
    risk_category: str, age: int, factors: list, start_date: datetime
) -> list[dict]:
    """Generate actionable care tasks."""
    tasks = []

    # Immediate tasks
    tasks.append({
        "title": "Review care plan with primary care provider",
        "type": "consultation",
        "priority": "high",
        "due_date": (start_date + timedelta(days=14)).strftime("%Y-%m-%d"),
        "status": "pending",
    })

    if risk_category in ["high", "very_high"]:
        tasks.append({
            "title": "Schedule breast cancer screening",
            "type": "screening",
            "priority": "high",
            "due_date": (start_date + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "pending",
        })
        tasks.append({
            "title": "Genetic counseling consultation",
            "type": "consultation",
            "priority": "high",
            "due_date": (start_date + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "pending",
        })

    # Education tasks
    tasks.append({
        "title": "Complete breast self-exam education module",
        "type": "education",
        "priority": "medium",
        "due_date": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
        "status": "pending",
    })

    tasks.append({
        "title": "Review screening preparation guidelines",
        "type": "education",
        "priority": "medium",
        "due_date": (start_date + timedelta(days=14)).strftime("%Y-%m-%d"),
        "status": "pending",
    })

    # Lifestyle tasks
    tasks.append({
        "title": "Set up exercise routine (150 min/week goal)",
        "type": "lifestyle",
        "priority": "medium",
        "due_date": (start_date + timedelta(days=14)).strftime("%Y-%m-%d"),
        "status": "pending",
    })

    return tasks


def _should_recommend_genetic_counseling(risk_category: str, factors: list) -> bool:
    """Determine if genetic counseling should be recommended."""
    if risk_category in ["high", "very_high"]:
        return True

    factor_names = [f.get("factor", "").lower() if isinstance(f, dict) else str(f).lower() for f in factors]
    if any("brca" in f or "genetic" in f or "family" in f for f in factor_names):
        return True

    return False


def _genetic_counseling_reason(factors: list) -> str:
    """Get reason for genetic counseling recommendation."""
    factor_names = [f.get("factor", "").lower() if isinstance(f, dict) else str(f).lower() for f in factors]

    if any("brca" in f for f in factor_names):
        return "Known BRCA mutation carrier - genetic counseling for family planning and risk management"
    elif any("family" in f for f in factor_names):
        return "Strong family history warrants genetic testing discussion"
    else:
        return "Elevated risk profile suggests benefit from genetic risk assessment"


def _get_support_resources(risk_category: str) -> list[dict]:
    """Get relevant support resources based on risk category."""
    resources = [
        {
            "name": "National Breast Cancer Foundation",
            "type": "information",
            "url": "https://www.nationalbreastcancer.org",
            "description": "Comprehensive breast cancer information and resources",
        },
        {
            "name": "Breast Self-Exam Guide",
            "type": "education",
            "description": "Step-by-step guide for monthly breast self-examination",
        },
    ]

    if risk_category in ["high", "very_high"]:
        resources.extend([
            {
                "name": "FORCE (Facing Our Risk of Cancer Empowered)",
                "type": "support",
                "url": "https://www.facingourrisk.org",
                "description": "Support for individuals at high risk for hereditary cancer",
            },
            {
                "name": "Patient Navigator Program",
                "type": "navigation",
                "description": "Dedicated navigator to help coordinate care and appointments",
            },
            {
                "name": "Genetic Counseling Services",
                "type": "consultation",
                "description": "Professional genetic counseling for risk assessment and family planning",
            },
        ])

    return resources


def _get_immediate_actions(risk_category: str, age: int) -> list[str]:
    """Get immediate action items based on risk category."""
    actions = ["Review this care plan with your healthcare provider"]

    if risk_category == "very_high":
        actions.extend([
            "Schedule genetic counseling appointment within 2 weeks",
            "Schedule breast MRI within 30 days",
            "Begin monthly breast self-exams",
            "Discuss risk-reducing medication options with provider",
        ])
    elif risk_category == "high":
        actions.extend([
            "Schedule mammogram within 30 days if overdue",
            "Discuss supplemental MRI screening with provider",
            "Consider genetic testing referral",
            "Begin monthly breast self-exams",
        ])
    elif risk_category == "moderate":
        actions.extend([
            "Ensure mammogram is scheduled per guidelines",
            "Begin monthly breast self-awareness practices",
            "Implement lifestyle modifications",
        ])
    else:
        actions.extend([
            "Schedule routine mammogram per age-appropriate guidelines",
            "Practice monthly breast awareness",
            "Maintain healthy lifestyle habits",
        ])

    return actions
