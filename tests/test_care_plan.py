"""
Tests for the Care Plan Generator Tool.
"""

import json
import pytest
from src.tools.care_plan_generator import generate_care_plan, get_care_plan


class TestGenerateCarePlan:
    """Tests for generate_care_plan function."""

    def test_generate_high_risk_plan(self):
        """Test generating a care plan for high-risk patient."""
        result = generate_care_plan(
            patient_id=400,
            risk_category="high",
            age=55,
            risk_score=52.0,
            risk_factors=json.dumps([{"factor": "Family History", "contribution": 20}]),
        )
        assert result["success"] is True
        plan = result["care_plan"]
        assert plan["patient_id"] == 400
        assert "screening_plan" in plan
        assert "lifestyle_recommendations" in plan
        assert "care_tasks" in plan
        assert plan["genetic_counseling"]["recommended"] is True

    def test_generate_low_risk_plan(self):
        """Test generating a care plan for low-risk patient."""
        result = generate_care_plan(
            patient_id=401,
            risk_category="low",
            age=42,
            risk_score=12.0,
        )
        assert result["success"] is True
        plan = result["care_plan"]
        assert plan["genetic_counseling"]["recommended"] is False

    def test_plan_includes_screening_schedule(self):
        """Test that care plan includes a screening schedule."""
        result = generate_care_plan(
            patient_id=402,
            risk_category="moderate",
            age=50,
            risk_score=30.0,
        )
        plan = result["care_plan"]
        assert "mammogram" in plan["screening_plan"]

    def test_plan_includes_tasks(self):
        """Test that care plan includes actionable tasks."""
        result = generate_care_plan(
            patient_id=403,
            risk_category="very_high",
            age=60,
            risk_score=70.0,
        )
        plan = result["care_plan"]
        assert len(plan["care_tasks"]) > 0
        assert all("title" in task and "due_date" in task for task in plan["care_tasks"])

    def test_immediate_actions_returned(self):
        """Test that immediate actions are included in response."""
        result = generate_care_plan(
            patient_id=404,
            risk_category="high",
            age=48,
            risk_score=45.0,
        )
        assert "immediate_actions" in result
        assert len(result["immediate_actions"]) > 0


class TestGetCarePlan:
    """Tests for get_care_plan function."""

    def test_get_existing_plan(self):
        """Test retrieving an existing care plan."""
        # Generate first
        generate_care_plan(
            patient_id=500,
            risk_category="moderate",
            age=45,
            risk_score=25.0,
        )

        result = get_care_plan(patient_id=500)
        assert result["success"] is True
        assert result["care_plan"]["patient_id"] == 500

    def test_get_nonexistent_plan(self):
        """Test retrieving plan for patient with no plan."""
        result = get_care_plan(patient_id=9999)
        assert result["success"] is False
        assert "recommendation" in result
