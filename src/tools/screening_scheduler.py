"""
Screening Scheduler Tool for CareCircle.
Manages scheduling, tracking, and coordination of breast cancer screenings.
"""

import json
from datetime import datetime, timedelta
from typing import Any
from strands import tool


# In-memory store for demo (in production, use database)
_screening_store: list[dict] = []
_schedule_counter = 0


@tool
def schedule_screening(
    patient_id: int,
    screening_type: str,
    preferred_date: str,
    facility: str = "Community Breast Health Center",
    provider: str = "",
    notes: str = "",
) -> dict[str, Any]:
    """
    Schedule a breast cancer screening appointment for a patient.

    Args:
        patient_id: The patient's unique identifier
        screening_type: Type of screening (mammogram, mri, ultrasound, clinical_exam, 3d_mammogram)
        preferred_date: Preferred date in YYYY-MM-DD format
        facility: Screening facility name
        provider: Healthcare provider name
        notes: Additional notes for the appointment

    Returns:
        Scheduling confirmation with appointment details
    """
    global _schedule_counter

    # Validate screening type
    valid_types = ["mammogram", "mri", "ultrasound", "clinical_exam", "3d_mammogram", "biopsy"]
    if screening_type.lower() not in valid_types:
        return {
            "success": False,
            "error": f"Invalid screening type. Must be one of: {', '.join(valid_types)}",
        }

    # Parse date
    try:
        scheduled_date = datetime.strptime(preferred_date, "%Y-%m-%d")
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}

    # Check if date is in the future
    if scheduled_date.date() < datetime.now().date():
        return {"success": False, "error": "Cannot schedule appointments in the past."}

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
        "created_at": datetime.now().isoformat(),
        "reminders": [
            {"type": "email", "days_before": 7, "sent": False},
            {"type": "sms", "days_before": 1, "sent": False},
        ],
    }

    _screening_store.append(appointment)

    # Generate preparation instructions
    prep_instructions = _get_prep_instructions(screening_type.lower())

    return {
        "success": True,
        "appointment": appointment,
        "preparation_instructions": prep_instructions,
        "message": f"Screening scheduled successfully for {preferred_date} at {facility}.",
        "next_steps": [
            "Confirmation email/SMS will be sent to the patient",
            "Reminder will be sent 7 days before the appointment",
            "Day-before reminder with preparation instructions",
        ],
    }


@tool
def get_upcoming_screenings(patient_id: int, days_ahead: int = 90) -> dict[str, Any]:
    """
    Get upcoming screening appointments for a patient.

    Args:
        patient_id: The patient's unique identifier
        days_ahead: Number of days to look ahead (default 90)

    Returns:
        List of upcoming screening appointments
    """
    cutoff_date = datetime.now() + timedelta(days=days_ahead)
    upcoming = []

    for appointment in _screening_store:
        if appointment["patient_id"] == patient_id and appointment["status"] != "cancelled":
            apt_date = datetime.strptime(appointment["scheduled_date"], "%Y-%m-%d")
            if datetime.now() <= apt_date <= cutoff_date:
                days_until = (apt_date.date() - datetime.now().date()).days
                appointment_copy = appointment.copy()
                appointment_copy["days_until"] = days_until
                upcoming.append(appointment_copy)

    # Sort by date
    upcoming.sort(key=lambda x: x["scheduled_date"])

    return {
        "patient_id": patient_id,
        "upcoming_count": len(upcoming),
        "appointments": upcoming,
        "period": f"Next {days_ahead} days",
        "message": (
            f"Found {len(upcoming)} upcoming screening(s) for patient {patient_id}."
            if upcoming
            else f"No upcoming screenings found for patient {patient_id} in the next {days_ahead} days."
        ),
    }


@tool
def update_screening_status(
    appointment_id: int,
    new_status: str,
    result: str = "",
    birads_score: int = -1,
    notes: str = "",
) -> dict[str, Any]:
    """
    Update the status of a screening appointment.

    Args:
        appointment_id: The appointment's unique identifier
        new_status: New status (confirmed, completed, cancelled, missed, rescheduled)
        result: Screening result if completed (normal, abnormal, inconclusive)
        birads_score: BI-RADS score (0-6) if applicable
        notes: Additional notes

    Returns:
        Updated appointment details with any follow-up recommendations
    """
    valid_statuses = ["confirmed", "completed", "cancelled", "missed", "rescheduled"]
    if new_status.lower() not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        }

    # Find appointment
    appointment = None
    for apt in _screening_store:
        if apt["id"] == appointment_id:
            appointment = apt
            break

    if not appointment:
        return {"success": False, "error": f"Appointment {appointment_id} not found."}

    # Update appointment
    appointment["status"] = new_status.lower()
    appointment["updated_at"] = datetime.now().isoformat()

    if notes:
        appointment["notes"] = notes

    follow_up = None
    if new_status.lower() == "completed" and result:
        appointment["result"] = result
        if birads_score >= 0:
            appointment["birads_score"] = birads_score

        # Generate follow-up recommendations
        follow_up = _get_follow_up_recommendations(result, birads_score)

    return {
        "success": True,
        "appointment": appointment,
        "follow_up_recommendations": follow_up,
        "message": f"Appointment {appointment_id} updated to '{new_status}'.",
    }


def _get_prep_instructions(screening_type: str) -> dict:
    """Get preparation instructions for a screening type."""
    instructions = {
        "mammogram": {
            "title": "Mammogram Preparation",
            "instructions": [
                "Do not wear deodorant, antiperspirant, powder, or lotion on the day of the exam",
                "Wear a two-piece outfit for easier access",
                "Schedule 1-2 weeks after your period when breasts are less tender",
                "Bring prior mammogram images if from a different facility",
                "Inform the technologist of any breast changes or concerns",
            ],
            "duration": "15-30 minutes",
            "what_to_expect": "Brief compression of each breast for imaging. May feel pressure but should not be painful.",
        },
        "3d_mammogram": {
            "title": "3D Mammogram (Tomosynthesis) Preparation",
            "instructions": [
                "Same preparation as standard mammogram",
                "Do not wear deodorant or body products near breast/underarm area",
                "The procedure takes slightly longer than a standard mammogram",
                "Bring prior imaging results for comparison",
            ],
            "duration": "20-40 minutes",
            "what_to_expect": "Similar to standard mammogram but the machine takes images from multiple angles.",
        },
        "mri": {
            "title": "Breast MRI Preparation",
            "instructions": [
                "Inform staff of any metal implants, pacemakers, or claustrophobia",
                "You may need to fast for 4 hours before if contrast dye is used",
                "Remove all metal objects and jewelry",
                "Schedule between days 7-14 of menstrual cycle if premenopausal",
                "Wear comfortable clothing without metal fasteners",
            ],
            "duration": "30-60 minutes",
            "what_to_expect": "You'll lie face down on a padded table. The machine makes loud noises; earplugs provided.",
        },
        "ultrasound": {
            "title": "Breast Ultrasound Preparation",
            "instructions": [
                "No special preparation required",
                "Wear a two-piece outfit",
                "Do not apply lotions or powders to the breast area",
            ],
            "duration": "15-30 minutes",
            "what_to_expect": "A gel is applied and a handheld device is moved over the breast. Painless procedure.",
        },
        "clinical_exam": {
            "title": "Clinical Breast Exam Preparation",
            "instructions": [
                "No special preparation needed",
                "Note any breast changes to discuss with provider",
                "Bring a list of current medications",
                "Be prepared to discuss family health history",
            ],
            "duration": "10-15 minutes",
            "what_to_expect": "Healthcare provider will visually inspect and manually examine breast tissue.",
        },
        "biopsy": {
            "title": "Breast Biopsy Preparation",
            "instructions": [
                "Discuss medications with your doctor - some blood thinners may need to be paused",
                "Arrange for someone to drive you home",
                "Wear a comfortable, supportive bra",
                "Do not apply lotions, powders, or deodorant",
                "Eat a light meal before the procedure",
            ],
            "duration": "30-60 minutes",
            "what_to_expect": "Local anesthesia will be used. Small tissue sample will be taken. Some pressure but minimal pain.",
        },
    }

    return instructions.get(screening_type, instructions["mammogram"])


def _get_follow_up_recommendations(result: str, birads_score: int) -> dict:
    """Generate follow-up recommendations based on screening results."""
    if result == "normal" or birads_score in [1, 2]:
        return {
            "urgency": "routine",
            "action": "Continue regular screening schedule",
            "timeline": "Next routine screening as per care plan",
            "details": "No additional follow-up needed at this time.",
        }
    elif result == "inconclusive" or birads_score == 0:
        return {
            "urgency": "soon",
            "action": "Additional imaging recommended",
            "timeline": "Schedule follow-up within 2-4 weeks",
            "details": "Additional views or different imaging modality needed for complete assessment.",
            "recommended_next": ["diagnostic mammogram", "ultrasound"],
        }
    elif birads_score == 3:
        return {
            "urgency": "moderate",
            "action": "Short-interval follow-up",
            "timeline": "Repeat imaging in 6 months",
            "details": "Probably benign finding. Short-interval follow-up to confirm stability.",
            "recommended_next": ["follow_up_mammogram_6_months"],
        }
    elif result == "abnormal" or birads_score in [4, 5]:
        return {
            "urgency": "high",
            "action": "Biopsy recommended",
            "timeline": "Schedule biopsy within 1-2 weeks",
            "details": "Suspicious finding that requires tissue sampling for definitive diagnosis.",
            "recommended_next": ["biopsy", "specialist_consultation"],
            "support_resources": [
                "Patient navigator available for support",
                "Genetic counseling referral if applicable",
                "Support group information provided",
            ],
        }
    elif birads_score == 6:
        return {
            "urgency": "immediate",
            "action": "Treatment planning",
            "timeline": "Immediate oncology referral",
            "details": "Known malignancy. Coordinate with oncology team for treatment planning.",
            "recommended_next": ["oncology_referral", "treatment_planning", "support_services"],
        }

    return {
        "urgency": "routine",
        "action": "Discuss with provider",
        "timeline": "At next scheduled visit",
        "details": "Consult with healthcare provider for personalized guidance.",
    }
