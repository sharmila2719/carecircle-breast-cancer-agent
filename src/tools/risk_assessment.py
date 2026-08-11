"""
Risk Assessment Tool for CareCircle.
Implements the Gail Model-inspired risk assessment for breast cancer screening.
Uses evidence-based factors to calculate personalized risk scores.
"""

import json
from typing import Any
from strands import tool


@tool
def calculate_risk_score(
    age: int,
    family_history: bool,
    genetic_markers: str = "",
    previous_biopsies: int = 0,
    breast_density: str = "scattered",
    hormone_therapy: bool = False,
    bmi: float = 25.0,
    smoking_history: bool = False,
    alcohol_consumption: str = "none",
    age_first_period: int = 12,
    age_first_birth: int = 25,
) -> dict[str, Any]:
    """
    Calculate breast cancer risk score based on patient factors.
    Uses a modified Gail Model approach with additional lifestyle factors.

    Args:
        age: Patient's current age
        family_history: Whether first-degree relatives had breast cancer
        genetic_markers: Known genetic markers (e.g., "BRCA1", "BRCA2", "")
        previous_biopsies: Number of previous breast biopsies
        breast_density: Breast density category (fatty, scattered, heterogeneous, dense)
        hormone_therapy: Whether patient uses/used hormone replacement therapy
        bmi: Body Mass Index
        smoking_history: Whether patient has smoking history
        alcohol_consumption: Alcohol consumption level (none, light, moderate, heavy)
        age_first_period: Age at first menstrual period
        age_first_birth: Age at first live birth (0 if nulliparous)

    Returns:
        Dictionary with risk score, category, and detailed breakdown
    """
    score = 0.0
    risk_factors = []

    # Age factor (weight: 0-25 points)
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

    # Family history (weight: 0-20 points)
    if family_history:
        score += 20
        risk_factors.append({"factor": "Family History", "contribution": 20, "detail": "First-degree relative with breast cancer"})

    # Genetic markers (weight: 0-25 points)
    if genetic_markers:
        markers = genetic_markers.upper()
        if "BRCA1" in markers or "BRCA2" in markers:
            score += 25
            risk_factors.append({"factor": "BRCA Mutation", "contribution": 25, "detail": f"Carrier of {genetic_markers}"})
        elif markers:
            score += 10
            risk_factors.append({"factor": "Other Genetic Markers", "contribution": 10, "detail": f"Markers: {genetic_markers}"})

    # Previous biopsies (weight: 0-10 points)
    if previous_biopsies > 0:
        biopsy_score = min(previous_biopsies * 4, 10)
        score += biopsy_score
        risk_factors.append({"factor": "Previous Biopsies", "contribution": biopsy_score, "detail": f"{previous_biopsies} previous biopsies"})

    # Breast density (weight: 0-15 points)
    density_scores = {"fatty": 0, "scattered": 5, "heterogeneous": 10, "dense": 15}
    density_score = density_scores.get(breast_density.lower(), 5)
    if density_score > 0:
        score += density_score
        risk_factors.append({"factor": "Breast Density", "contribution": density_score, "detail": f"{breast_density.capitalize()} breast tissue"})

    # Hormone therapy (weight: 0-8 points)
    if hormone_therapy:
        score += 8
        risk_factors.append({"factor": "Hormone Therapy", "contribution": 8, "detail": "History of hormone replacement therapy"})

    # BMI factor (weight: 0-5 points for postmenopausal)
    if age >= 50 and bmi >= 30:
        bmi_score = 5
        score += bmi_score
        risk_factors.append({"factor": "Elevated BMI", "contribution": bmi_score, "detail": f"BMI {bmi:.1f} (postmenopausal)"})

    # Lifestyle factors
    if smoking_history:
        score += 3
        risk_factors.append({"factor": "Smoking History", "contribution": 3, "detail": "Past or current smoking"})

    alcohol_scores = {"none": 0, "light": 2, "moderate": 4, "heavy": 6}
    alc_score = alcohol_scores.get(alcohol_consumption.lower(), 0)
    if alc_score > 0:
        score += alc_score
        risk_factors.append({"factor": "Alcohol Consumption", "contribution": alc_score, "detail": f"{alcohol_consumption.capitalize()} consumption"})

    # Reproductive factors
    if age_first_period < 12:
        score += 3
        risk_factors.append({"factor": "Early Menarche", "contribution": 3, "detail": f"First period at age {age_first_period}"})

    if age_first_birth > 30 or age_first_birth == 0:
        score += 4
        risk_factors.append({"factor": "Late/No First Birth", "contribution": 4, "detail": "First birth after 30 or nulliparous"})

    # Normalize to 0-100 scale
    max_possible = 124  # Maximum theoretical score
    normalized_score = min((score / max_possible) * 100, 100)

    # Determine risk category
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
        "assessment_details": {
            "model": "Modified Gail Model with Lifestyle Factors",
            "factors_evaluated": len(risk_factors),
            "note": "This is a screening tool and should not replace clinical judgment.",
        },
    }


@tool
def assess_risk(patient_data: str) -> dict[str, Any]:
    """
    Perform a comprehensive risk assessment for a patient.
    Accepts patient data as JSON string and returns risk evaluation.

    Args:
        patient_data: JSON string containing patient information with fields:
            - age (int): Patient age
            - family_history (bool): Family history of breast cancer
            - genetic_markers (str): Known genetic markers
            - previous_biopsies (int): Number of previous biopsies
            - breast_density (str): Breast density category
            - hormone_therapy (bool): HRT usage
            - bmi (float): Body Mass Index
            - smoking_history (bool): Smoking history
            - alcohol_consumption (str): Alcohol level

    Returns:
        Comprehensive risk assessment dictionary
    """
    try:
        data = json.loads(patient_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format for patient data"}

    # Extract fields with defaults
    risk_result = calculate_risk_score(
        age=data.get("age", 50),
        family_history=data.get("family_history", False),
        genetic_markers=data.get("genetic_markers", ""),
        previous_biopsies=data.get("previous_biopsies", 0),
        breast_density=data.get("breast_density", "scattered"),
        hormone_therapy=data.get("hormone_therapy", False),
        bmi=data.get("bmi", 25.0),
        smoking_history=data.get("smoking_history", False),
        alcohol_consumption=data.get("alcohol_consumption", "none"),
        age_first_period=data.get("age_first_period", 12),
        age_first_birth=data.get("age_first_birth", 25),
    )

    # Add screening recommendations based on risk
    screening_plan = _get_screening_recommendations(
        risk_result["risk_category"], data.get("age", 50)
    )

    risk_result["screening_recommendations"] = screening_plan
    risk_result["patient_summary"] = {
        "age": data.get("age", 50),
        "key_risk_factors": [f["factor"] for f in risk_result["risk_factors"][:5]],
    }

    return risk_result


def _get_screening_recommendations(risk_category: str, age: int) -> dict:
    """Generate screening recommendations based on risk category and age."""
    recommendations = {
        "very_high": {
            "mammogram_frequency": "Annual",
            "mri_recommended": True,
            "mri_frequency": "Annual (alternating with mammogram every 6 months)",
            "clinical_exam_frequency": "Every 6 months",
            "self_exam": "Monthly",
            "genetic_counseling": True,
            "start_age": max(25, age - 10) if age > 35 else 25,
            "additional": [
                "Consider risk-reducing medications (chemoprevention)",
                "Discuss prophylactic surgery options with specialist",
                "Annual breast MRI starting at age 25-30",
                "Consider clinical trial enrollment",
            ],
        },
        "high": {
            "mammogram_frequency": "Annual",
            "mri_recommended": True,
            "mri_frequency": "Annual",
            "clinical_exam_frequency": "Every 6-12 months",
            "self_exam": "Monthly",
            "genetic_counseling": True,
            "start_age": max(30, age) if age > 40 else 30,
            "additional": [
                "Supplemental screening with breast MRI",
                "Discuss risk-reducing strategies",
                "Consider genetic testing if not done",
            ],
        },
        "moderate": {
            "mammogram_frequency": "Annual" if age >= 40 else "Discuss with provider",
            "mri_recommended": False,
            "mri_frequency": "As needed based on mammogram findings",
            "clinical_exam_frequency": "Annual",
            "self_exam": "Monthly",
            "genetic_counseling": False,
            "start_age": 40,
            "additional": [
                "Maintain healthy lifestyle",
                "Regular clinical breast exams",
                "Be aware of breast changes",
            ],
        },
        "low": {
            "mammogram_frequency": "Biennial" if age >= 50 else "Discuss starting at 40",
            "mri_recommended": False,
            "mri_frequency": "Not typically recommended",
            "clinical_exam_frequency": "Annual",
            "self_exam": "Monthly awareness",
            "genetic_counseling": False,
            "start_age": 40 if age < 50 else 50,
            "additional": [
                "Follow USPSTF guidelines",
                "Maintain healthy lifestyle",
                "Annual wellness visits",
            ],
        },
    }

    return recommendations.get(risk_category, recommendations["moderate"])
