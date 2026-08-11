"""
CareCircle - Main Entry Point
Breast Cancer Screening & Care Coordination Agent

This is the main entry point for running the CareCircle application.
It can run in different modes: API server, CLI chat, or Streamlit UI.
"""

import sys
import argparse
import uvicorn


def run_api():
    """Run the FastAPI server."""
    from src.config import settings
    print("🩺 Starting CareCircle API Server...")
    print(f"📡 API docs available at http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    uvicorn.run(
        "src.api.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
    )


def run_cli():
    """Run the CLI chat interface."""
    from src.agent.care_agent import create_agent

    print("🩺 CareCircle - Breast Cancer Screening & Care Coordination Agent")
    print("=" * 60)
    print("I can help you with:")
    print("  📊 Risk assessments")
    print("  📅 Screening scheduling")
    print("  📋 Care plan management")
    print("  📚 Educational information")
    print("")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("=" * 60)

    agent = create_agent()

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\n🩺 CareCircle: Take care! Remember to stay on top of your screenings. 💗")
                break

            print("\n🩺 CareCircle: ", end="")
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\n🩺 CareCircle: Goodbye! Stay healthy! 💗")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please check your AWS credentials and try again.")


def run_demo():
    """Run a demonstration of the tools without requiring AWS credentials."""
    import json
    from src.tools.risk_assessment import calculate_risk_score
    from src.tools.screening_scheduler import schedule_screening, get_upcoming_screenings
    from src.tools.care_plan_generator import generate_care_plan
    from src.tools.patient_education import get_educational_content
    from src.tools.notification_manager import send_reminder

    print("🩺 CareCircle - Tool Demonstration")
    print("=" * 60)
    print("Running a complete workflow demonstration...\n")

    # Step 1: Risk Assessment
    print("📊 STEP 1: Risk Assessment")
    print("-" * 40)
    risk_result = calculate_risk_score(
        age=52,
        family_history=True,
        genetic_markers="",
        previous_biopsies=1,
        breast_density="heterogeneous",
        hormone_therapy=False,
        bmi=27.5,
        smoking_history=False,
        alcohol_consumption="light",
        age_first_period=11,
        age_first_birth=30,
    )
    print(f"  Risk Score: {risk_result['risk_score']}")
    print(f"  Risk Category: {risk_result['risk_category']}")
    print(f"  Recommendation: {risk_result['recommendation']}")
    print(f"  Key Factors: {[f['factor'] for f in risk_result['risk_factors']]}")

    # Step 2: Schedule Screening
    print(f"\n📅 STEP 2: Schedule Screening")
    print("-" * 40)
    from datetime import datetime, timedelta
    future_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    screening_result = schedule_screening(
        patient_id=1,
        screening_type="mammogram",
        preferred_date=future_date,
        facility="City Breast Imaging Center",
        provider="Dr. Sarah Johnson",
        notes="Annual screening - family history of breast cancer",
    )
    print(f"  Scheduled: {screening_result['success']}")
    print(f"  Date: {future_date}")
    print(f"  Type: Mammogram")
    print(f"  Facility: City Breast Imaging Center")

    # Step 3: Generate Care Plan
    print(f"\n📋 STEP 3: Generate Care Plan")
    print("-" * 40)
    care_plan_result = generate_care_plan(
        patient_id=1,
        risk_category=risk_result["risk_category"],
        age=52,
        risk_score=risk_result["risk_score"],
        risk_factors=json.dumps(risk_result["risk_factors"]),
    )
    plan = care_plan_result["care_plan"]
    print(f"  Plan: {plan['title']}")
    print(f"  Tasks: {len(plan['care_tasks'])} action items")
    print(f"  Recommendations: {len(plan['lifestyle_recommendations'])} lifestyle changes")
    print(f"  Genetic Counseling: {'Recommended' if plan['genetic_counseling']['recommended'] else 'Not required'}")

    # Step 4: Education
    print(f"\n📚 STEP 4: Patient Education")
    print("-" * 40)
    edu_result = get_educational_content(topic="mammogram_overview", detail_level="brief")
    print(f"  Topic: {edu_result['topic']}")
    print(f"  Summary: {edu_result['summary'][:100]}...")

    # Step 5: Send Reminder
    print(f"\n🔔 STEP 5: Send Reminder")
    print("-" * 40)
    reminder_result = send_reminder(
        patient_id=1,
        notification_type="email",
        category="screening_reminder",
        message=f"Your mammogram is scheduled for {future_date} at City Breast Imaging Center. Please review the preparation instructions.",
        subject="Upcoming Mammogram Reminder",
    )
    print(f"  Sent: {reminder_result['success']}")
    print(f"  Type: Email")
    print(f"  Category: Screening Reminder")

    print(f"\n{'=' * 60}")
    print("✅ Demonstration complete!")
    print("💡 To use the full agent with AI capabilities, configure your AWS credentials.")
    print("   See .env.example for required environment variables.")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="CareCircle - Breast Cancer Screening & Care Coordination Agent"
    )
    parser.add_argument(
        "--mode",
        choices=["api", "cli", "demo"],
        default="demo",
        help="Run mode: api (REST API server), cli (interactive chat), demo (tool demonstration)",
    )

    args = parser.parse_args()

    if args.mode == "api":
        run_api()
    elif args.mode == "cli":
        run_cli()
    elif args.mode == "demo":
        run_demo()


if __name__ == "__main__":
    main()
