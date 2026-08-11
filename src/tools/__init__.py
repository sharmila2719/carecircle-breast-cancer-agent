"""
CareCircle Agent Tools - Custom tools for the Strands Agent.
"""

from src.tools.risk_assessment import assess_risk, calculate_risk_score
from src.tools.screening_scheduler import (
    schedule_screening,
    get_upcoming_screenings,
    update_screening_status,
)
from src.tools.care_plan_generator import generate_care_plan, get_care_plan
from src.tools.patient_education import get_educational_content
from src.tools.notification_manager import send_reminder, get_notifications

__all__ = [
    "assess_risk",
    "calculate_risk_score",
    "schedule_screening",
    "get_upcoming_screenings",
    "update_screening_status",
    "generate_care_plan",
    "get_care_plan",
    "get_educational_content",
    "send_reminder",
    "get_notifications",
]
