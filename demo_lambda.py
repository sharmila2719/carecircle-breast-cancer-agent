"""
CareCircle - AWS Lambda Serverless API Demo
Demonstrates all endpoints working on the live Lambda deployment.
"""

import httpx
import json

BASE_URL = "https://vnja2r5dx6.execute-api.us-east-1.amazonaws.com"


def main():
    print("=" * 70)
    print("   🩺 CARECIRCLE - AWS LAMBDA SERVERLESS DEMO")
    print("   Breast Cancer Screening & Care Coordination Agent")
    print("   Live URL:", BASE_URL)
    print("=" * 70)

    # Step 1: Health Check
    print("\n\n📡 [1/7] HEALTH CHECK")
    print("-" * 50)
    r = httpx.get(f"{BASE_URL}/health")
    data = r.json()
    print(f"  ✅ Status: {data['status']}")
    print(f"  ☁️  Runtime: {data['runtime']}")
    print(f"  📦 Version: {data['version']}")

    # Step 2: API Info
    print("\n\n🏠 [2/7] API ROOT INFO")
    print("-" * 50)
    r = httpx.get(f"{BASE_URL}/")
    data = r.json()
    print(f"  Name: {data['name']}")
    print(f"  Description: {data['description']}")
    print(f"  Deployment: {data['deployment']}")
    print(f"  Available Endpoints:")
    for key, val in data["endpoints"].items():
        print(f"    • {key}: {val}")

    # Step 3: Risk Assessment
    print("\n\n📊 [3/7] RISK ASSESSMENT")
    print("-" * 50)
    print("  Patient: 52-year-old female")
    print("  Family History: Yes (mother had breast cancer)")
    print("  Breast Density: Heterogeneous")
    print("  Previous Biopsies: 1")
    print("  BMI: 27.5")
    print("  Alcohol: Light")
    print()

    risk_payload = {
        "age": 52,
        "family_history": True,
        "genetic_markers": "",
        "previous_biopsies": 1,
        "breast_density": "heterogeneous",
        "hormone_therapy": False,
        "bmi": 27.5,
        "smoking_history": False,
        "alcohol_consumption": "light",
        "age_first_period": 11,
        "age_first_birth": 30,
    }

    r = httpx.post(f"{BASE_URL}/api/risk-assessment", json=risk_payload)
    data = r.json()
    assessment = data["assessment"]
    print(f"  🎯 RESULT:")
    print(f"     Risk Score: {assessment['risk_score']} / 100")
    print(f"     Category: {assessment['risk_category'].upper()}")
    print(f"     Recommendation: {assessment['recommendation']}")
    print(f"     Key Risk Factors:")
    for factor in assessment["risk_factors"]:
        print(f"       • {factor['factor']} (+{factor['contribution']} pts) - {factor['detail']}")

    # Step 4: Schedule Screening
    print("\n\n📅 [4/7] SCHEDULE SCREENING")
    print("-" * 50)
    screening_payload = {
        "patient_id": 1,
        "screening_type": "mammogram",
        "preferred_date": "2026-09-15",
        "facility": "City Breast Imaging Center",
        "provider": "Dr. Sarah Johnson",
        "notes": "Annual screening - high risk patient",
    }

    r = httpx.post(f"{BASE_URL}/api/screening/schedule", json=screening_payload)
    data = r.json()
    print(f"  ✅ Success: {data['success']}")
    print(f"  📋 Appointment:")
    print(f"     Type: Mammogram")
    print(f"     Date: 2026-09-15")
    print(f"     Facility: City Breast Imaging Center")
    print(f"     Provider: Dr. Sarah Johnson")
    print(f"  📝 Preparation:")
    prep = data.get("preparation", {})
    print(f"     {prep.get('title', 'N/A')}")
    print(f"     Duration: {prep.get('duration', 'N/A')}")
    for instr in prep.get("instructions", []):
        print(f"       ✓ {instr}")

    # Step 5: Generate Care Plan
    print("\n\n📋 [5/7] GENERATE CARE PLAN")
    print("-" * 50)
    care_plan_payload = {
        "patient_id": 1,
        "risk_category": "high",
        "age": 52,
        "risk_score": assessment["risk_score"],
        "risk_factors": json.dumps(assessment["risk_factors"]),
    }

    r = httpx.post(f"{BASE_URL}/api/care-plan/generate", json=care_plan_payload)
    data = r.json()
    plan = data["care_plan"]
    print(f"  ✅ Success: {data['success']}")
    print(f"  📋 {plan['title']}")
    print(f"     Risk Score: {plan['risk_score']}")
    print(f"     Genetic Counseling: {'✅ Recommended' if plan['genetic_counseling_recommended'] else '❌ Not needed'}")
    print(f"\n  🩺 Screening Schedule:")
    for modality, details in plan["screening_plan"].items():
        print(f"     • {modality.replace('_', ' ').title()}: {details['frequency']} (Next: {details['next_due']})")
    print(f"\n  ✅ Tasks ({len(plan['tasks'])} items):")
    for task in plan["tasks"]:
        print(f"     [{task['priority'].upper()}] {task['title']} (Due: {task['due']})")
    print(f"\n  🥗 Lifestyle Recommendations:")
    for rec in plan["lifestyle"]:
        print(f"     • {rec}")

    # Step 6: Education
    print("\n\n📚 [6/7] EDUCATION CONTENT")
    print("-" * 50)
    r = httpx.get(f"{BASE_URL}/api/education")
    topics = r.json()["topics"]
    print(f"  Available Topics ({len(topics)}):")
    for t in topics:
        print(f"    • {t['id']}: {t['title']}")

    print(f"\n  📖 Fetching 'early_detection' topic...")
    r = httpx.get(f"{BASE_URL}/api/education/early_detection")
    data = r.json()
    print(f"  Title: {data['title']}")
    print(f"  Summary: {data['summary']}")
    print(f"  Key Points:")
    for point in data["key_points"]:
        print(f"    ✅ {point}")

    # Step 7: Chat
    print("\n\n💬 [7/7] CHAT WITH AGENT")
    print("-" * 50)
    messages = [
        "Hello, I need help with breast cancer screening",
        "What is my risk of breast cancer?",
        "How do I schedule a mammogram?",
    ]

    for msg in messages:
        r = httpx.post(f"{BASE_URL}/api/chat", json={"message": msg})
        data = r.json()
        print(f"  👤 User: {msg}")
        print(f"  🩺 CareCircle: {data['response']}")
        print()

    # Summary
    print("\n" + "=" * 70)
    print("   ✅ DEMO COMPLETE - ALL 7 ENDPOINTS WORKING ON AWS LAMBDA")
    print("=" * 70)
    print(f"\n  🌐 Live API: {BASE_URL}")
    print(f"  📖 Swagger Docs: {BASE_URL}/docs")
    print(f"  🎨 Dashboard: https://carecircle-breast-cancer-agent.streamlit.app")
    print(f"  💻 GitHub: https://github.com/sharmila2719/carecircle-breast-cancer-agent")
    print(f"\n  Powered by: AWS Lambda + API Gateway (Serverless)")
    print(f"  Agent Framework: Strands Agents + AWS Bedrock")
    print()


if __name__ == "__main__":
    main()
