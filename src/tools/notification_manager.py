"""
Notification Manager Tool for CareCircle.
Handles patient communications including reminders, alerts, and educational messages.
"""

import json
from datetime import datetime
from typing import Any
from strands import tool


# In-memory notification store for demo
_notifications: list[dict] = []
_notification_counter = 0


@tool
def send_reminder(
    patient_id: int,
    notification_type: str,
    category: str,
    message: str,
    subject: str = "",
    schedule_time: str = "",
) -> dict[str, Any]:
    """
    Send or schedule a notification/reminder for a patient.

    Args:
        patient_id: Patient's unique identifier
        notification_type: Delivery method (email, sms, in_app)
        category: Notification category (screening_reminder, follow_up, education, care_plan_update, appointment_confirmation)
        message: The notification message content
        subject: Subject line (for email notifications)
        schedule_time: When to send (ISO format). If empty, sends immediately.

    Returns:
        Notification confirmation with delivery details
    """
    global _notification_counter

    valid_types = ["email", "sms", "in_app"]
    if notification_type.lower() not in valid_types:
        return {
            "success": False,
            "error": f"Invalid notification type. Must be one of: {', '.join(valid_types)}",
        }

    valid_categories = [
        "screening_reminder",
        "follow_up",
        "education",
        "care_plan_update",
        "appointment_confirmation",
        "results_available",
        "general",
    ]
    if category.lower() not in valid_categories:
        return {
            "success": False,
            "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}",
        }

    _notification_counter += 1
    now = datetime.now()

    notification = {
        "id": _notification_counter,
        "patient_id": patient_id,
        "notification_type": notification_type.lower(),
        "category": category.lower(),
        "subject": subject or _generate_subject(category),
        "message": message,
        "status": "scheduled" if schedule_time else "sent",
        "scheduled_at": schedule_time if schedule_time else None,
        "sent_at": now.isoformat() if not schedule_time else None,
        "created_at": now.isoformat(),
        "is_read": False,
    }

    _notifications.append(notification)

    return {
        "success": True,
        "notification": notification,
        "message": (
            f"Notification {'scheduled' if schedule_time else 'sent'} successfully "
            f"via {notification_type} to patient {patient_id}."
        ),
    }


@tool
def get_notifications(
    patient_id: int, unread_only: bool = False, category: str = ""
) -> dict[str, Any]:
    """
    Retrieve notifications for a patient.

    Args:
        patient_id: Patient's unique identifier
        unread_only: If True, return only unread notifications
        category: Filter by category (empty for all)

    Returns:
        List of notifications matching criteria
    """
    results = [n for n in _notifications if n["patient_id"] == patient_id]

    if unread_only:
        results = [n for n in results if not n["is_read"]]

    if category:
        results = [n for n in results if n["category"] == category.lower()]

    # Sort by most recent first
    results.sort(key=lambda x: x["created_at"], reverse=True)

    return {
        "success": True,
        "patient_id": patient_id,
        "total_count": len(results),
        "unread_count": sum(1 for n in results if not n["is_read"]),
        "notifications": results,
        "filters_applied": {
            "unread_only": unread_only,
            "category": category or "all",
        },
    }


def _generate_subject(category: str) -> str:
    """Generate a default subject line based on category."""
    subjects = {
        "screening_reminder": "🩺 Upcoming Breast Cancer Screening Reminder",
        "follow_up": "📋 Follow-Up Action Required",
        "education": "📚 Your Breast Health Education Update",
        "care_plan_update": "📝 Your Care Plan Has Been Updated",
        "appointment_confirmation": "✅ Appointment Confirmed",
        "results_available": "📊 Your Screening Results Are Available",
        "general": "💗 CareCircle Health Update",
    }
    return subjects.get(category, "CareCircle Notification")
