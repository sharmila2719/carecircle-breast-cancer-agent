"""
Tests for the Risk Assessment Tool.
"""

import json
import pytest
from src.tools.risk_assessment import calculate_risk_score, assess_risk


class TestCalculateRiskScore:
    """Tests for calculate_risk_score function."""

    def test_low_risk_patient(self):
        """Test a patient with minimal risk factors."""
        result = calculate_risk_score(
            age=35,
            family_history=False,
            genetic_markers="",
            previous_biopsies=0,
            breast_density="fatty",
            hormone_therapy=False,
            bmi=22.0,
            smoking_history=False,
            alcohol_consumption="none",
        )
        assert result["risk_category"] == "low"
        assert result["risk_score"] < 20

    def test_high_risk_patient(self):
        """Test a patient with multiple risk factors."""
        result = calculate_risk_score(
            age=55,
            family_history=True,
            genetic_markers="BRCA1",
            previous_biopsies=2,
            breast_density="dense",
            hormone_therapy=True,
            bmi=32.0,
            smoking_history=True,
            alcohol_consumption="moderate",
        )
        assert result["risk_category"] in ["high", "very_high"]
        assert result["risk_score"] >= 40

    def test_moderate_risk_patient(self):
        """Test a patient with moderate risk factors."""
        result = calculate_risk_score(
            age=50,
            family_history=True,
            genetic_markers="",
            previous_biopsies=0,
            breast_density="heterogeneous",
            hormone_therapy=False,
            bmi=26.0,
            smoking_history=False,
            alcohol_consumption="light",
        )
        assert result["risk_category"] in ["moderate", "high"]
        assert result["risk_score"] >= 20

    def test_risk_factors_are_returned(self):
        """Test that risk factors breakdown is included."""
        result = calculate_risk_score(
            age=50,
            family_history=True,
            genetic_markers="",
            previous_biopsies=0,
            breast_density="scattered",
            hormone_therapy=False,
            bmi=25.0,
            smoking_history=False,
            alcohol_consumption="none",
        )
        assert "risk_factors" in result
        assert len(result["risk_factors"]) > 0
        assert all("factor" in f and "contribution" in f for f in result["risk_factors"])

    def test_brca_mutation_increases_risk(self):
        """Test that BRCA mutations significantly increase risk."""
        without_brca = calculate_risk_score(age=45, family_history=False, genetic_markers="")
        with_brca = calculate_risk_score(age=45, family_history=False, genetic_markers="BRCA1")
        assert with_brca["risk_score"] > without_brca["risk_score"]

    def test_recommendation_included(self):
        """Test that a recommendation is always returned."""
        result = calculate_risk_score(age=50, family_history=False)
        assert "recommendation" in result
        assert len(result["recommendation"]) > 0


class TestAssessRisk:
    """Tests for assess_risk function."""

    def test_valid_json_input(self):
        """Test with valid JSON patient data."""
        patient_data = json.dumps({
            "age": 52,
            "family_history": True,
            "breast_density": "heterogeneous",
        })
        result = assess_risk(patient_data=patient_data)
        assert "risk_score" in result
        assert "screening_recommendations" in result

    def test_invalid_json_input(self):
        """Test with invalid JSON input."""
        result = assess_risk(patient_data="not valid json")
        assert "error" in result

    def test_screening_recommendations_included(self):
        """Test that screening recommendations are generated."""
        patient_data = json.dumps({"age": 55, "family_history": True})
        result = assess_risk(patient_data=patient_data)
        assert "screening_recommendations" in result
        recs = result["screening_recommendations"]
        assert "mammogram_frequency" in recs
