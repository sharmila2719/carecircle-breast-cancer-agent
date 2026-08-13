"""
CareCircle Streamlit Cloud Entry Point.
This file is the main entry point for Streamlit Community Cloud deployment.
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
        '<div class="sub-header">Breast Cancer Screening & Care Coordination Agent<br>'
        '<small>Powered by AWS Bedrock Strands Agents</small></div>',
        unsafe_allow_html=True,
    )

    # Sidebar navigation
    st.sidebar.title("🎀 CareCircle")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📊 Risk Assessment",
            "📅 Screening Scheduler",
            "📋 Care Plan",
            "📚 Education Center",
            "💬 Chat with Agent",
            "ℹ️ About",
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
    elif page == "ℹ️ About":
        show_about()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**CareCircle v1.0**")
    st.sidebar.markdown("☁️ Powered by AWS Bedrock")
    st.sidebar.markdown("⚠️ Not a substitute for medical advice")
    st.sidebar.markdown("[GitHub Repo](https://github.com/sharmila2719/carecircle-breast-cancer-agent)")


def show_dashboard():
    """Show the main dashboard."""
    st.header("Welcome to CareCircle")
    st.markdown(
        "Your personalized breast cancer screening and care coordination assistant. "
        "This AI-powered agent helps patients and providers coordinate screenings, "
        "assess risk, and manage care plans."
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
        st.subheader("📊 Patient Risk Distribution")
        risk_data = pd.DataFrame({
            "Category": ["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"],
            "Count": [45, 62, 35, 14],
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
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📅 Screening Compliance (2026)")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
        scheduled = [40, 45, 38, 50, 42, 48, 44, 46]
        completed = [35, 40, 36, 45, 38, 43, 41, 39]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Scheduled", x=months, y=scheduled, marker_color="#E91E8C"))
        fig.add_trace(go.Bar(name="Completed", x=months, y=completed, marker_color="#28a745"))
        fig.update_layout(barmode="group", height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Workflow Demo
    st.markdown("---")
    st.subheader("🚀 Quick Start - Try the Workflow")
    st.markdown("""
    1. **📊 Risk Assessment** → Enter patient details to calculate personalized risk score
    2. **📋 Care Plan** → Generate a care plan based on the risk assessment
    3. **📅 Screening Scheduler** → Schedule recommended screenings
    4. **📚 Education** → Access breast health educational materials
    """)

    # Recent activity
    st.subheader("📋 Recent Activity")
    activities = [
        {"time": "2 hours ago", "event": "✅ Risk assessment completed for Patient #142 - High Risk (43.5)", "type": "assessment"},
        {"time": "4 hours ago", "event": "📅 Mammogram scheduled for Patient #138 - Aug 25, 2026", "type": "screening"},
        {"time": "Yesterday", "event": "📋 Care plan generated for Patient #125 - Moderate Risk", "type": "care_plan"},
        {"time": "Yesterday", "event": "📚 Educational content delivered to 12 patients", "type": "education"},
        {"time": "2 days ago", "event": "🔔 Screening reminders sent to 8 patients", "type": "reminder"},
    ]

    for activity in activities:
        st.markdown(f"**{activity['time']}** — {activity['event']}")


def show_risk_assessment():
    """Show the risk assessment page."""
    st.header("📊 Breast Cancer Risk Assessment")
    st.markdown(
        "Complete the form below to calculate a personalized risk score based on "
        "evidence-based factors (Modified Gail Model with lifestyle factors)."
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
        marker_str = "" if genetic_markers == "None" else genetic_markers

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
        st.subheader("📋 Assessment Results")

        score = result["risk_score"]
        category = result["risk_category"]

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Risk Score", "font": {"size": 24}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1},
                    "bar": {"color": "#E91E8C"},
                    "steps": [
                        {"range": [0, 20], "color": "#d4edda"},
                        {"range": [20, 40], "color": "#fff3cd"},
                        {"range": [40, 60], "color": "#ffeeba"},
                        {"range": [60, 100], "color": "#f8d7da"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": score,
                    },
                },
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        category_colors = {
            "low": "🟢", "moderate": "🟡", "high": "🟠", "very_high": "🔴"
        }
        st.markdown(f"### {category_colors.get(category, '⚪')} Risk Category: **{category.replace('_', ' ').title()}**")
        st.info(f"**Recommendation:** {result['recommendation']}")

        # Risk factors breakdown
        st.subheader("📈 Risk Factors Breakdown")
        if result["risk_factors"]:
            factors_df = pd.DataFrame(result["risk_factors"])
            fig = px.bar(
                factors_df,
                x="contribution",
                y="factor",
                orientation="h",
                color="contribution",
                color_continuous_scale="RdYlGn_r",
                title="Individual Risk Factor Contributions",
            )
            fig.update_layout(height=max(300, len(result["risk_factors"]) * 50))
            st.plotly_chart(fig, use_container_width=True)

            # Details table
            with st.expander("📊 Detailed Factor Analysis"):
                for factor in result["risk_factors"]:
                    st.markdown(f"- **{factor['factor']}** (+{factor['contribution']} points): {factor['detail']}")

        # Store in session for care plan generation
        st.session_state["last_risk_result"] = result
        st.session_state["patient_age"] = age

        st.success("✅ Risk assessment complete! Go to **📋 Care Plan** to generate a personalized care plan.")


def show_screening_scheduler():
    """Show the screening scheduler page."""
    st.header("📅 Screening Scheduler")

    tab1, tab2 = st.tabs(["📝 Schedule New Screening", "📋 View Upcoming"])

    with tab1:
        st.subheader("Schedule a Screening Appointment")

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
                    value=datetime.now().date() + timedelta(days=14),
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

                prep = result.get("preparation_instructions", {})
                if prep:
                    with st.expander("📋 Preparation Instructions", expanded=True):
                        st.markdown(f"### {prep.get('title', '')}")
                        st.markdown(f"**Duration:** {prep.get('duration', 'N/A')}")
                        st.markdown("**Instructions:**")
                        for instruction in prep.get("instructions", []):
                            st.markdown(f"✓ {instruction}")
                        st.markdown(f"\n**What to expect:** {prep.get('what_to_expect', '')}")
            else:
                st.error(f"❌ {result.get('error', 'Scheduling failed')}")

    with tab2:
        st.subheader("Upcoming Screenings")
        col1, col2 = st.columns([1, 2])
        with col1:
            patient_id_view = st.number_input("Patient ID", min_value=1, value=1, key="view_patient")
            days = st.slider("Days ahead", 7, 365, 90)

        if st.button("🔍 Search Appointments"):
            result = get_upcoming_screenings(patient_id=patient_id_view, days_ahead=days)
            if result["upcoming_count"] > 0:
                for apt in result["appointments"]:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**🩺 {apt['screening_type'].replace('_', ' ').title()}**")
                            st.markdown(f"📍 {apt.get('facility', 'TBD')}")
                        with col2:
                            st.markdown(f"📅 {apt['scheduled_date']}")
                            st.markdown(f"⏳ In {apt.get('days_until', '?')} days")
                        with col3:
                            status_icons = {"scheduled": "🔵", "confirmed": "🟢", "completed": "✅"}
                            icon = status_icons.get(apt['status'], "⚪")
                            st.markdown(f"{icon} **{apt['status'].title()}**")
                    st.markdown("---")
            else:
                st.info(result["message"])


def show_care_plan():
    """Show the care plan page."""
    st.header("📋 Personalized Care Plan")

    if "last_risk_result" in st.session_state:
        risk_result = st.session_state["last_risk_result"]
        age = st.session_state.get("patient_age", 50)

        category_colors = {"low": "🟢", "moderate": "🟡", "high": "🟠", "very_high": "🔴"}
        icon = category_colors.get(risk_result['risk_category'], "⚪")

        st.info(
            f"Based on your recent risk assessment: "
            f"{icon} **{risk_result['risk_category'].replace('_', ' ').title()}** risk "
            f"(Score: {risk_result['risk_score']})"
        )

        if st.button("🎯 Generate Personalized Care Plan", use_container_width=True):
            with st.spinner("Generating your personalized care plan..."):
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

                st.subheader(f"📋 {plan['title']}")

                # Immediate actions
                st.markdown("### 🚨 Immediate Actions")
                for action in result.get("immediate_actions", []):
                    st.markdown(f"➡️ {action}")

                # Screening schedule
                with st.expander("🩺 Screening Schedule", expanded=True):
                    for modality, details in plan["screening_plan"].items():
                        if isinstance(details, dict):
                            st.markdown(f"**{modality.replace('_', ' ').title()}**")
                            for key, value in details.items():
                                if key != "education_provided":
                                    st.markdown(f"  • {key.replace('_', ' ').title()}: {value}")
                            st.markdown("")

                # Lifestyle recommendations
                with st.expander("🥗 Lifestyle Recommendations", expanded=True):
                    for rec in plan["lifestyle_recommendations"]:
                        priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        icon = priority_icons.get(rec["priority"], "⚪")
                        st.markdown(f"{icon} **{rec['category']}**: {rec['recommendation']}")
                        st.caption(f"   {rec['detail']}")

                # Care tasks
                with st.expander("✅ Action Items & Tasks", expanded=True):
                    for task in plan["care_tasks"]:
                        priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        p_icon = priority_icons.get(task["priority"], "⚪")
                        st.markdown(
                            f"⬜ **{task['title']}** {p_icon}\n"
                            f"   Type: {task['type'].title()} | Due: {task['due_date']}"
                        )

                # Genetic counseling
                gc = plan.get("genetic_counseling", {})
                if gc.get("recommended"):
                    with st.expander("🧬 Genetic Counseling", expanded=True):
                        st.warning(f"**Recommended**: {gc.get('reason', 'Based on risk profile')}")

                # Resources
                with st.expander("📚 Support Resources"):
                    for resource in plan["support_resources"]:
                        st.markdown(f"• **{resource['name']}** ({resource['type']})")
                        if resource.get("description"):
                            st.caption(f"  {resource['description']}")
                        if resource.get("url"):
                            st.markdown(f"  🔗 {resource['url']}")
    else:
        st.warning("⚠️ Please complete a **Risk Assessment** first to generate a personalized care plan.")
        st.markdown("Go to **📊 Risk Assessment** in the sidebar to get started.")


def show_education_center():
    """Show the education center page."""
    st.header("📚 Breast Health Education Center")
    st.markdown("Evidence-based educational content about breast cancer screening, prevention, and care.")

    topics = [
        ("breast_self_exam", "🤲 Breast Self-Exam", "Learn monthly self-examination technique"),
        ("mammogram_overview", "📷 Mammogram Guide", "What to expect during a mammogram"),
        ("risk_factors", "⚠️ Risk Factors", "Understanding what increases your risk"),
        ("screening_guidelines", "📋 Screening Guidelines", "When and how often to get screened"),
        ("genetic_testing", "🧬 Genetic Testing", "Should you get tested?"),
        ("dense_breasts", "🔬 Breast Density", "What density means for screening"),
        ("lifestyle_prevention", "🥗 Prevention", "Lifestyle changes that reduce risk"),
        ("early_detection", "🎯 Early Detection", "Why catching it early matters"),
        ("myths_facts", "❓ Myths vs Facts", "Separating fact from fiction"),
        ("support_resources", "💗 Support", "Resources for your journey"),
    ]

    # Topic selection
    selected = st.selectbox(
        "Choose a topic:",
        options=[t[0] for t in topics],
        format_func=lambda x: next(f"{t[1]} - {t[2]}" for t in topics if t[0] == x),
    )

    detail_level = st.radio("Detail level:", ["brief", "standard", "comprehensive"], index=1, horizontal=True)

    if selected:
        result = get_educational_content(topic=selected, detail_level=detail_level)

        if result.get("success"):
            st.markdown("---")
            st.subheader(f"📖 {result['topic']}")
            st.markdown(result["summary"])

            st.markdown("### ✅ Key Points")
            for point in result.get("key_points", []):
                st.markdown(f"• {point}")

            if result.get("detailed_content"):
                with st.expander("📖 Detailed Information", expanded=True):
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
                        st.markdown(f"• **{resource['name']}** ({resource.get('type', 'resource')})")

            if result.get("references"):
                with st.expander("📑 References"):
                    for ref in result["references"]:
                        st.caption(f"• {ref}")


def show_chat():
    """Show the agent chat interface with real AI responses."""
    st.header("💬 Chat with CareCircle Agent")
    st.markdown(
        "Ask questions about breast cancer screening, risk factors, or get help managing your care. "
        "**Powered by AWS Bedrock (Claude) with real-time AI responses.**"
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm **CareCircle**, your breast cancer screening and care coordination assistant. 🩺\n\n"
                    "I can help you with:\n"
                    "- 📊 **Risk assessments** — tell me your age, family history, and I'll calculate your risk\n"
                    "- 📅 **Screening scheduling** — I can schedule mammograms, MRIs, and more\n"
                    "- 📋 **Care plans** — personalized screening and lifestyle recommendations\n"
                    "- 📚 **Education** — ask me about any breast health topic\n"
                    "- 🔔 **Reminders** — I'll help you stay on track\n\n"
                    "**Try asking:** *'I'm 52 with a family history of breast cancer. What's my risk?'*"
                ),
            }
        ]

    # Initialize agent (once per session)
    if "care_agent" not in st.session_state:
        try:
            from src.agent.care_agent import create_agent
            st.session_state.care_agent = create_agent()
            st.session_state.agent_ready = True
        except Exception as e:
            st.session_state.care_agent = None
            st.session_state.agent_ready = False
            st.warning(f"⚠️ AI agent could not connect to AWS Bedrock. Using guided responses. ({type(e).__name__})")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask CareCircle anything about breast health..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🩺 CareCircle is analyzing your question..."):
                if st.session_state.get("agent_ready") and st.session_state.care_agent:
                    try:
                        response = st.session_state.care_agent.chat(prompt)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        response = _generate_demo_response(prompt)
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    response = _generate_demo_response(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})


def _generate_demo_response(prompt: str) -> str:
    """Generate a demo response based on keywords (when AWS credentials are not configured)."""
    prompt_lower = prompt.lower()

    if any(word in prompt_lower for word in ["risk", "assess", "score", "calculate"]):
        return (
            "I can help assess your breast cancer risk! 📊\n\n"
            "Please use the **📊 Risk Assessment** page in the sidebar to enter your health details. "
            "The tool evaluates 12+ factors including:\n"
            "- Age and family history\n"
            "- Genetic markers (BRCA1/BRCA2)\n"
            "- Breast density\n"
            "- Lifestyle factors\n\n"
            "Would you like to navigate there now?"
        )
    elif any(word in prompt_lower for word in ["schedule", "appointment", "mammogram", "screening", "book"]):
        return (
            "I can help schedule your screening! 📅\n\n"
            "Head to the **📅 Screening Scheduler** page to:\n"
            "- Book mammograms, MRIs, ultrasounds, or clinical exams\n"
            "- Get preparation instructions for your appointment\n"
            "- View upcoming scheduled screenings\n\n"
            "Regular screening is key to early detection — the 5-year survival rate for early-stage "
            "breast cancer is **99%**!"
        )
    elif any(word in prompt_lower for word in ["care plan", "plan", "recommendation"]):
        return (
            "I can generate a personalized care plan for you! 📋\n\n"
            "First, complete a **📊 Risk Assessment**, then visit the **📋 Care Plan** page. "
            "Your plan will include:\n"
            "- Personalized screening schedule\n"
            "- Lifestyle recommendations\n"
            "- Action items with due dates\n"
            "- Support resources\n\n"
            "Each plan is tailored to your individual risk profile."
        )
    elif any(word in prompt_lower for word in ["education", "learn", "information", "what is", "how"]):
        return (
            "Great question! 📚\n\n"
            "Visit the **📚 Education Center** for comprehensive information on:\n"
            "- Breast self-examination techniques\n"
            "- Understanding mammograms\n"
            "- Risk factors and prevention\n"
            "- Genetic testing\n"
            "- Screening guidelines by age\n"
            "- Myths vs. facts\n\n"
            "Knowledge is power when it comes to breast health!"
        )
    elif any(word in prompt_lower for word in ["hello", "hi", "hey", "help"]):
        return (
            "Hello! 👋 I'm here to help with your breast health journey.\n\n"
            "Here's what I recommend:\n"
            "1. Start with a **📊 Risk Assessment** to understand your risk level\n"
            "2. Get a **📋 Care Plan** tailored to your profile\n"
            "3. **📅 Schedule** your recommended screenings\n"
            "4. Visit the **📚 Education Center** to learn more\n\n"
            "What would you like to start with?"
        )
    else:
        return (
            "Thank you for your question! 🩺\n\n"
            "I'm CareCircle, focused on breast cancer screening coordination. "
            "I can help with:\n"
            "- **Risk assessment** — type 'assess my risk'\n"
            "- **Scheduling** — type 'schedule a mammogram'\n"
            "- **Care plans** — type 'create a care plan'\n"
            "- **Education** — type 'tell me about mammograms'\n\n"
            "For the full AI-powered experience with natural language understanding, "
            "AWS Bedrock credentials can be configured in the `.env` file.\n\n"
            "Try the interactive tools in the sidebar for immediate results! ➡️"
        )


def show_about():
    """Show the about page."""
    st.header("ℹ️ About CareCircle")

    st.markdown("""
    ## 🩺 What is CareCircle?

    CareCircle is an AI-powered breast cancer screening and care coordination agent built with 
    **AWS Bedrock Strands Agents**. It helps patients and healthcare providers manage breast cancer 
    screening through personalized risk assessment, intelligent scheduling, and evidence-based care plans.

    ## 🎯 The Problem We're Solving

    - **1 in 8 women** will be diagnosed with breast cancer in their lifetime
    - **33% of eligible women** are NOT up to date on mammography screening
    - Early detection improves 5-year survival from **28% → 99%**
    - Care coordination is fragmented across multiple providers

    ## 👥 Who It's For

    | User | Benefit |
    |------|---------|
    | **Patients** | Personalized risk understanding and screening guidance |
    | **Healthcare Providers** | Efficient screening program management |
    | **Care Coordinators** | Population health tracking and follow-up |
    | **Health Systems** | Improved early detection metrics |

    ## 🏗️ Technology Stack

    | Component | Technology |
    |-----------|-----------|
    | AI Framework | Strands Agents SDK |
    | LLM Provider | AWS Bedrock (Claude) |
    | Risk Model | Modified Gail Model (12+ factors) |
    | Frontend | Streamlit |
    | Backend API | FastAPI |
    | Database | SQLAlchemy + SQLite |
    | Deployment | Streamlit Cloud (Serverless) |

    ## 📊 Features

    - ✅ Personalized risk assessment with 12+ evidence-based factors
    - ✅ Intelligent screening scheduling with prep instructions
    - ✅ Automated care plan generation
    - ✅ Comprehensive patient education (10+ topics)
    - ✅ Multi-channel notifications
    - ✅ Interactive dashboard with visualizations
    - ✅ Conversational AI interface

    ## 🔗 Links

    - [GitHub Repository](https://github.com/sharmila2719/carecircle-breast-cancer-agent)
    - [Architecture Documentation](https://github.com/sharmila2719/carecircle-breast-cancer-agent/blob/master/docs/architecture.md)

    ---

    *Built for the [Agents for Humans Hackathon 2026](https://agentsforhumans.devpost.com/) • MIT License*
    """)


if __name__ == "__main__":
    main()
