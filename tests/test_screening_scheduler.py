"""
Tests for the Screening Scheduler Tool.
"""

import pytest
from datetime import datetime, timedelta
from src.tools.screening_scheduler import (
    schedule_screening,
    get_upcoming_screenings,
    update_screening_status,
)


class TestScheduleScreening:
    """Tests for schedule_screening function."""

    def test_schedule_valid_mammogram(self):
        """Test scheduling a valid mammogram appointment."""
        future_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        result = schedule_screening(
            patient_id=100,
            screening_type="mammogram",
            preferred_date=future_date,
            facility="Test Clinic",
        )
        assert result["success"] is True
        assert "appointment" in result
        assert result["appointment"]["screening_type"] == "mammogram"

    def test_schedule_invalid_type(self):
        """Test scheduling with invalid screening type."""
        future_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        result = schedule_screening(
            patient_id=100,
            screening_type="invalid_type",
            preferred_date=future_date,
        )
        assert result["success"] is False
        assert "error" in result

    def test_schedule_past_date(self):
        """Test scheduling with a past date."""
        past_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        result = schedule_screening(
            patient_id=100,
            screening_type="mammogram",
            preferred_date=past_date,
        )
        assert result["success"] is False

    def test_preparation_instructions_included(self):
        """Test that preparation instructions are returned."""
        future_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        result = schedule_screening(
            patient_id=100,
            screening_type="mri",
            preferred_date=future_date,
        )
        assert "preparation_instructions" in result
        assert "instructions" in result["preparation_instructions"]


class TestGetUpcomingScreenings:
    """Tests for get_upcoming_screenings function."""

    def test_get_screenings_for_patient(self):
        """Test retrieving upcoming screenings."""
        # Schedule one first
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        schedule_screening(
            patient_id=200,
            screening_type="mammogram",
            preferred_date=future_date,
        )

        result = get_upcoming_screenings(patient_id=200, days_ahead=90)
        assert "appointments" in result
        assert result["upcoming_count"] >= 1

    def test_no_screenings_found(self):
        """Test when no screenings are found."""
        result = get_upcoming_screenings(patient_id=9999, days_ahead=90)
        assert result["upcoming_count"] == 0


class TestUpdateScreeningStatus:
    """Tests for update_screening_status function."""

    def test_update_to_completed(self):
        """Test updating screening to completed with results."""
        # Schedule first
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        scheduled = schedule_screening(
            patient_id=300,
            screening_type="mammogram",
            preferred_date=future_date,
        )
        apt_id = scheduled["appointment"]["id"]

        result = update_screening_status(
            appointment_id=apt_id,
            new_status="completed",
            result="normal",
            birads_score=1,
        )
        assert result["success"] is True
        assert result["appointment"]["status"] == "completed"

    def test_invalid_status(self):
        """Test updating with invalid status."""
        result = update_screening_status(
            appointment_id=1,
            new_status="invalid_status",
        )
        assert result["success"] is False

    def test_follow_up_for_abnormal(self):
        """Test that abnormal results include follow-up recommendations."""
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        scheduled = schedule_screening(
            patient_id=301,
            screening_type="mammogram",
            preferred_date=future_date,
        )
        apt_id = scheduled["appointment"]["id"]

        result = update_screening_status(
            appointment_id=apt_id,
            new_status="completed",
            result="abnormal",
            birads_score=4,
        )
        assert result["follow_up_recommendations"] is not None
        assert result["follow_up_recommendations"]["urgency"] == "high"
