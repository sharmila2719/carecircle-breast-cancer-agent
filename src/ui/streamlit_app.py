"""
CareCircle Streamlit Dashboard.
Interactive web UI for breast cancer screening coordination.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.risk_assessment import calculate_risk_score
from src.tools.screening_scheduler import schedule_screening, get_upcoming_screenings
from src.tools.care_plan_generator import generate_care_plan, get_care_plan
from src.tools.patient_education import get_educational_content
from src.tools.notification_manager import send_reminder


# Page configuration
st.set_page_config(
    page_title="CareCircle - Breast Cancer Screening Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E91E8C;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-low { color: #28a745; font-weight: bold; }
    .risk-moderate { color: #ffc107; font-weight: bold; }
    .risk-high { color: #fd7e14; font-weight: bold; }
    .risk-very-high { color: #dc3545; font-weight: bold; }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #E91E8C;
    }
    .stButton>button {
        background-color: #E91E8C;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #C4177A;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<div class="main-header">🩺 CareCircle</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Breast Cancer Screening & Care Coordination Agent</div>',
        unsafe_allow_html=True,
    )

    # Sidebar navigation
    st.sidebar.image("https://img.icons8.com/color/96/breast-cancer-ribbon.png", width=80)
    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Dashboard",
            "📊 Risk Assessment",
            "📅 Screening Scheduler",
            "📋 Care Plan",
            "📚 Education Center",
            "💬 Chat with Agent",
        ],
    )

    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 Risk Assessment":
        show_risk_assessment()
    elif page == "📅 Screening Scheduler":
        show_screening_scheduler()
    elif page == "📋 Care Plan":
        show_care_plan()
    elif page == "📚 Education Center":
        show_education_center()
    elif page == "💬 Chat with Agent":
        show_chat()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**CareCircle v1.0**")
    st.sidebar.markdown("Powered by AWS Bedrock")
    st.sidebar.markdown("⚠️ Not a substitute for medical advice")


def show_dashboard():
    """Show the main dashboard."""
    st.header("Welcome to CareCircle")
    st.markdown(
        "Your personalized breast cancer screening and care coordination assistant."
    )

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Patients", "156", "+12 this month")
    with col2:
        st.metric("Screenings This Month", "43", "+8 from last month")
    with col3:
        st.metric("Care Plans Active", "89", "+5 new")
    with col4:
        st.metric("Overdue Screenings", "7", "-3 from last week")

    st.markdown("---")

    # Quick actions
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Risk Distribution")
        # Sample data for visualization
        risk_data = pd.DataFrame({
            "Category": ["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"],
            "Count": [45, 62, 35, 14],
            "Color": ["#28a745", "#ffc107", "#fd7e14", "#dc3545"],
        })

        fig = px.pie(
            risk_data,
            values="Count",
            names="Category",
            color="Category",
            color_discrete_map={
                "Low Risk": "#28a745",
                "Moderate Risk": "#ffc107",
                "High Risk": "#fd7e14",
                "Very High Risk": "#dc3545",
            },
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📅 Screening Compliance")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        scheduled = [40, 45, 38, 50, 42, 48]
        completed = [35, 40, 36, 45, 38, 43]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Scheduled", x=months, y=scheduled, marker_color="#E91E8C"))
        fig.add_trace(go.Bar(name="Completed", x=months, y=completed, marker_color="#28a745"))
        fig.update_layout(barmode="group", height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Recent activity
    st.subheader("📋 Recent Activity")
    activities = [
        {"time": "2 hours ago", "event": "Risk assessment completed for Patient #142", "type": "assessment"},
        {"time": "4 hours ago", "event": "Mammogram scheduled for Patient #138", "type": "screening"},
        {"time": "Yesterday", "event": "Care plan updated for Patient #125", "type": "care_plan"},
        {"time": "Yesterday", "event": "Educational content sent to 12 patients", "type": "education"},
        {"time": "2 days ago", "event": "Screening reminder sent to 8 patients", "type": "reminder"},
    ]

    for activity in activities:
        st.markdown(f"**{activity['time']}** - {activity['event']}")


def show_risk_assessment():
    """Show the risk assessment page."""
    st.header("📊 Breast Cancer Risk Assessment")
    st.markdown(
        "Complete the form below to calculate a personalized risk score based on "
        "evidence-based factors."
    )

    with st.form("risk_assessment_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Demographics")
            age = st.number_input("Age", min_value=18, max_value=120, value=50)
            bmi = st.number_input("BMI", min_value=10.0, max_value=80.0, value=25.0, step=0.1)

            st.subheader("Medical History")
            family_history = st.checkbox("Family history of breast cancer (first-degree relative)")
            genetic_markers = st.selectbox(
                "Known genetic markers",
                ["None", "BRCA1", "BRCA2", "BRCA1 and BRCA2", "PALB2", "Other"],
            )
            previous_biopsies = st.number_input("Previous breast biopsies", min_value=0, max_value=10, value=0)

        with col2:
            st.subheader("Breast Characteristics")
            breast_density = st.selectbox(
                "Breast density",
                ["fatty", "scattered", "heterogeneous", "dense"],
                index=1,
            )

            st.subheader("Lifestyle Factors")
            hormone_therapy = st.checkbox("History of hormone replacement therapy")
            smoking_history = st.checkbox("Smoking history")
            alcohol_consumption = st.selectbox(
                "Alcohol consumption",
                ["none", "light", "moderate", "heavy"],
            )

            st.subheader("Reproductive History")
            age_first_period = st.number_input("Age at first period", min_value=8, max_value=20, value=12)
            age_first_birth = st.number_input(
                "Age at first live birth (0 if none)", min_value=0, max_value=55, value=25
            )

        submitted = st.form_submit_button("🔬 Calculate Risk Score", use_container_width=True)

    if submitted:
        # Map genetic markers selection
        marker_str = "" if genetic_markers == "None" else genetic_markers

        # Calculate risk
        result = calculate_risk_score(
            age=age,
            family_history=family_history,
            genetic_markers=marker_str,
            previous_biopsies=previous_biopsies,
            breast_density=breast_density,
            hormone_therapy=hormone_therapy,
            bmi=bmi,
            smoking_history=smoking_history,
            alcohol_consumption=alcohol_consumption,
            age_first_period=age_first_period,
            age_first_birth=age_first_birth,
        )

        st.markdown("---")
        st.subheader("Results")

        # Risk score display
        score = result["risk_score"]
        category = result["risk_category"]

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Gauge chart for risk score
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                title={"text": "Risk Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#E91E8C"},
                    "steps": [
                        {"range": [0, 20], "color": "#d4edda"},
                        {"range": [20, 40], "color": "#fff3cd"},
                        {"range": [40, 60], "color": "#ffeeba"},
                        {"range": [60, 100], "color": "#f8d7da"},
                    ],
                },
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Category and recommendation
        category_colors = {
            "low": "🟢", "moderate": "🟡", "high": "🟠", "very_high": "🔴"
        }
        st.markdown(f"### {category_colors.get(category, '⚪')} Risk Category: **{category.replace('_', ' ').title()}**")
        st.info(f"**Recommendation:** {result['recommendation']}")

        # Risk factors breakdown
        st.subheader("Risk Factors Breakdown")
        if result["risk_factors"]:
            factors_df = pd.DataFrame(result["risk_factors"])
            fig = px.bar(
                factors_df,
                x="contribution",
                y="factor",
                orientation="h",
                color="contribution",
                color_continuous_scale="RdYlGn_r",
                title="Risk Factor Contributions",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Store in session for care plan generation
        st.session_state["last_risk_result"] = result
        st.session_state["patient_age"] = age


def show_screening_scheduler():
    """Show the screening scheduler page."""
    st.header("📅 Screening Scheduler")

    tab1, tab2 = st.tabs(["Schedule New", "Upcoming Screenings"])

    with tab1:
        st.subheader("Schedule a Screening")

        with st.form("scheduling_form"):
            col1, col2 = st.columns(2)

            with col1:
                patient_id = st.number_input("Patient ID", min_value=1, value=1)
                screening_type = st.selectbox(
                    "Screening Type",
                    ["mammogram", "3d_mammogram", "mri", "ultrasound", "clinical_exam", "biopsy"],
                )
                preferred_date = st.date_input(
                    "Preferred Date",
                    min_value=datetime.now().date(),
                    value=datetime.now().date() + timedelta(days=7),
                )

            with col2:
                facility = st.text_input("Facility", "Community Breast Health Center")
                provider = st.text_input("Provider (optional)", "")
                notes = st.text_area("Notes (optional)", "")

            submitted = st.form_submit_button("📅 Schedule Screening", use_container_width=True)

        if submitted:
            result = schedule_screening(
                patient_id=patient_id,
                screening_type=screening_type,
                preferred_date=preferred_date.strftime("%Y-%m-%d"),
                facility=facility,
                provider=provider,
                notes=notes,
            )

            if result.get("success"):
                st.success(f"✅ {result['message']}")

                # Show preparation instructions
                prep = result.get("preparation_instructions", {})
                if prep:
                    with st.expander("📋 Preparation Instructions"):
                        st.markdown(f"### {prep.get('title', '')}")
                        st.markdown(f"**Duration:** {prep.get('duration', 'N/A')}")
                        st.markdown("**Instructions:**")
                        for instruction in prep.get("instructions", []):
                            st.markdown(f"- {instruction}")
                        st.markdown(f"**What to expect:** {prep.get('what_to_expect', '')}")
            else:
                st.error(f"❌ {result.get('error', 'Scheduling failed')}")

    with tab2:
        st.subheader("View Upcoming Screenings")
        patient_id_view = st.number_input("Patient ID", min_value=1, value=1, key="view_patient")
        days = st.slider("Days ahead", 7, 365, 90)

        if st.button("🔍 Search"):
            result = get_upcoming_screenings(patient_id=patient_id_view, days_ahead=days)
            if result["upcoming_count"] > 0:
                for apt in result["appointments"]:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{apt['screening_type'].replace('_', ' ').title()}**")
                            st.markdown(f"📍 {apt.get('facility', 'TBD')}")
                        with col2:
                            st.markdown(f"📅 {apt['scheduled_date']}")
                            st.markdown(f"⏳ In {apt.get('days_until', '?')} days")
                        with col3:
                            st.markdown(f"Status: **{apt['status'].title()}**")
                    st.markdown("---")
            else:
                st.info(result["message"])


def show_care_plan():
    """Show the care plan page."""
    st.header("📋 Personalized Care Plan")

    # Check if we have a recent risk assessment
    if "last_risk_result" in st.session_state:
        risk_result = st.session_state["last_risk_result"]
        age = st.session_state.get("patient_age", 50)

        st.info(
            f"Based on your recent risk assessment: "
            f"**{risk_result['risk_category'].replace('_', ' ').title()}** risk "
            f"(Score: {risk_result['risk_score']})"
        )

        if st.button("🎯 Generate Care Plan"):
            result = generate_care_plan(
                patient_id=1,
                risk_category=risk_result["risk_category"],
                age=age,
                risk_score=risk_result["risk_score"],
                risk_factors=json.dumps(risk_result.get("risk_factors", [])),
            )

            if result.get("success"):
                plan = result["care_plan"]
                st.success("✅ Care plan generated successfully!")

                # Display care plan sections
                st.subheader(plan["title"])

                # Screening schedule
                with st.expander("🩺 Screening Schedule", expanded=True):
                    for modality, details in plan["screening_plan"].items():
                        if isinstance(details, dict):
                            st.markdown(f"**{modality.replace('_', ' ').title()}**")
                            for key, value in details.items():
                                st.markdown(f"  - {key.replace('_', ' ').title()}: {value}")
                            st.markdown("")

                # Lifestyle recommendations
                with st.expander("🥗 Lifestyle Recommendations", expanded=True):
                    for rec in plan["lifestyle_recommendations"]:
                        priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        icon = priority_icons.get(rec["priority"], "⚪")
                        st.markdown(f"{icon} **{rec['category']}**: {rec['recommendation']}")
                        st.markdown(f"   *{rec['detail']}*")

                # Care tasks
                with st.expander("✅ Action Items", expanded=True):
                    for task in plan["care_tasks"]:
                        status_icon = "⬜" if task["status"] == "pending" else "✅"
                        st.markdown(
                            f"{status_icon} **{task['title']}** "
                            f"(Due: {task['due_date']}, Priority: {task['priority'].title()})"
                        )

                # Resources
                with st.expander("📚 Support Resources"):
                    for resource in plan["support_resources"]:
                        st.markdown(f"- **{resource['name']}** ({resource['type']})")
                        st.markdown(f"  {resource.get('description', '')}")
    else:
        st.warning("Please complete a Risk Assessment first to generate a personalized care plan.")
        if st.button("Go to Risk Assessment"):
            st.session_state["page"] = "📊 Risk Assessment"
            st.rerun()


def show_education_center():
    """Show the education center page."""
    st.header("📚 Education Center")
    st.markdown("Learn about breast cancer screening, prevention, and care.")

    topics = [
        ("breast_self_exam", "🤲 Breast Self-Exam", "Learn how to perform monthly self-exams"),
        ("mammogram_overview", "📷 Mammogram Guide", "What to expect during a mammogram"),
        ("risk_factors", "⚠️ Risk Factors", "Understanding breast cancer risk factors"),
        ("screening_guidelines", "📋 Screening Guidelines", "When and how often to get screened"),
        ("genetic_testing", "🧬 Genetic Testing", "Understanding genetic testing options"),
        ("dense_breasts", "🔬 Breast Density", "What breast density means for you"),
        ("lifestyle_prevention", "🥗 Prevention", "Lifestyle changes that reduce risk"),
        ("early_detection", "🎯 Early Detection", "Why early detection saves lives"),
        ("myths_facts", "❓ Myths vs Facts", "Separating fact from fiction"),
        ("support_resources", "💗 Support", "Resources for your journey"),
    ]

    # Topic grid
    cols = st.columns(2)
    for i, (topic_id, title, description) in enumerate(topics):
        with cols[i % 2]:
            with st.container():
                if st.button(f"{title}", key=f"topic_{topic_id}", use_container_width=True):
                    st.session_state["selected_topic"] = topic_id
                st.caption(description)

    # Show selected topic content
    if "selected_topic" in st.session_state:
        st.markdown("---")
        result = get_educational_content(
            topic=st.session_state["selected_topic"], detail_level="comprehensive"
        )

        if result.get("success"):
            st.subheader(result["topic"])
            st.markdown(result["summary"])

            st.markdown("### Key Points")
            for point in result.get("key_points", []):
                st.markdown(f"✅ {point}")

            if result.get("detailed_content"):
                with st.expander("📖 Detailed Information"):
                    st.markdown(result["detailed_content"])

            if result.get("faqs"):
                with st.expander("❓ Frequently Asked Questions"):
                    for faq in result["faqs"]:
                        st.markdown(f"**Q: {faq['q']}**")
                        st.markdown(f"A: {faq['a']}")
                        st.markdown("")

            if result.get("resources"):
                with st.expander("📚 Additional Resources"):
                    for resource in result["resources"]:
                        st.markdown(f"- {resource['name']} ({resource['type']})")


def show_chat():
    """Show the agent chat interface."""
    st.header("💬 Chat with CareCircle Agent")
    st.markdown(
        "Ask questions about breast cancer screening, risk factors, "
        "or get help with your care plan."
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm CareCircle, your breast cancer screening and care coordination assistant. "
                    "I can help you with:\n\n"
                    "- 📊 Risk assessments\n"
                    "- 📅 Screening scheduling\n"
                    "- 📋 Care plan management\n"
                    "- 📚 Educational information\n\n"
                    "How can I help you today?"
                ),
            }
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask CareCircle..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    from src.agent.care_agent import create_agent
                    agent = create_agent()
                    response = agent.chat(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = (
                        f"I'm having trouble connecting to the AI service. "
                        f"Please ensure your AWS credentials are configured. Error: {str(e)}"
                    )
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


if __name__ == "__main__":
    main()
