# 🩺 CareCircle - Breast Cancer Screening & Care Coordination Agent

<p align="center">
  <img src="docs/images/carecircle-banner.png" alt="CareCircle Banner" width="600">
</p>

<p align="center">
  <strong>An AI-powered breast cancer screening coordination agent built with AWS Bedrock Strands Agents</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-license">License</a>
</p>

---

## 📋 Project Description

**CareCircle** is an intelligent breast cancer screening and care coordination agent that leverages AWS Bedrock's Strands Agents framework to provide personalized risk assessments, screening scheduling, care plan generation, and patient education. 

### What it does:
- **Risk Assessment**: Calculates personalized breast cancer risk scores using a modified Gail Model incorporating genetic, lifestyle, and medical history factors
- **Screening Coordination**: Schedules, tracks, and manages breast cancer screening appointments (mammograms, MRIs, ultrasounds, clinical exams)
- **Care Plan Generation**: Creates evidence-based, personalized care plans tailored to each patient's risk profile
- **Patient Education**: Delivers clear, empathetic educational content about breast health topics
- **Smart Notifications**: Manages reminders and communications to improve screening adherence
- **Conversational AI**: Natural language interface powered by AWS Bedrock for intuitive patient/provider interactions

### Who it's for:
- **Patients** seeking guidance on breast cancer screening schedules and risk factors
- **Healthcare Providers** coordinating screening programs and patient care
- **Care Coordinators** managing patient populations and ensuring screening compliance
- **Health Systems** looking to improve breast cancer early detection rates

### How it works:
CareCircle uses the **Strands Agents** framework with **AWS Bedrock** (Claude) as the reasoning engine. The agent orchestrates custom tools for risk calculation, scheduling, care planning, education, and notifications. Patients and providers interact through a Streamlit dashboard, REST API, or CLI chat interface.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Risk Assessment** | Modified Gail Model with 12+ factors for personalized risk scoring |
| 📅 **Screening Scheduler** | Intelligent scheduling with preparation instructions and reminders |
| 📋 **Care Plans** | Auto-generated plans with screenings, lifestyle recommendations, and tasks |
| 📚 **Education Center** | 10+ topics covering screening, prevention, genetics, and support |
| 💬 **AI Chat** | Natural language conversations powered by AWS Bedrock Claude |
| 🔔 **Notifications** | Automated reminders via email, SMS, and in-app notifications |
| 📈 **Dashboard** | Interactive Streamlit UI with charts and visualizations |
| 🌐 **REST API** | Full FastAPI with OpenAPI documentation |
| 🐳 **Docker Ready** | Containerized deployment with docker-compose |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CareCircle Platform                     │
│                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │
│  │ Streamlit  │  │  FastAPI   │  │  CLI Chat      │    │
│  │ Dashboard  │  │  REST API  │  │  Interface     │    │
│  └─────┬──────┘  └─────┬──────┘  └───────┬────────┘    │
│        └────────────────┼─────────────────┘              │
│                         │                                 │
│              ┌──────────▼──────────┐                     │
│              │   Strands Agent     │                     │
│              │   (Orchestrator)    │◄──── System Prompt  │
│              └──────────┬──────────┘                     │
│                         │                                 │
│    ┌────────┬───────────┼───────────┬──────────┐        │
│    │        │           │           │          │        │
│  ┌─▼──┐ ┌──▼───┐ ┌────▼────┐ ┌───▼────┐ ┌──▼───┐   │
│  │Risk│ │Sched-│ │Care Plan│ │Educat- │ │Notif-│   │
│  │Tool│ │uler  │ │Generator│ │ion     │ │ier   │   │
│  └────┘ └──────┘ └─────────┘ └────────┘ └──────┘   │
│                         │                                 │
│              ┌──────────▼──────────┐                     │
│              │   SQLite Database   │                     │
│              └─────────────────────┘                     │
└─────────────────────────────────────────────────────────┘
                          │
               ┌──────────▼──────────┐
               │    AWS Bedrock      │
               │    (Claude Model)   │
               └─────────────────────┘
```

For the full architecture diagram, see [docs/architecture.md](docs/architecture.md).

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- AWS Account with Bedrock access enabled
- AWS CLI configured (or environment variables set)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/carecircle-breast-cancer-agent.git
cd carecircle-breast-cancer-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
copy .env.example .env
# Edit .env with your AWS credentials and configuration
```

5. **Run the application**

```bash
# Demo mode (no AWS credentials needed - demonstrates all tools)
python main.py --mode demo

# CLI Chat mode (requires AWS credentials)
python main.py --mode cli

# API Server mode (requires AWS credentials)
python main.py --mode api

# Streamlit Dashboard
streamlit run src/ui/streamlit_app.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Dashboard: http://localhost:8501
```

---

## 🎬 Demo

### Running the Demo (No AWS Credentials Required)

```bash
python main.py --mode demo
```

This runs a complete workflow demonstration:
1. ✅ Risk assessment for a sample patient
2. ✅ Screening appointment scheduling
3. ✅ Care plan generation
4. ✅ Educational content delivery
5. ✅ Notification/reminder sending

### Demo Video

📺 [Watch the 5-minute demo video](docs/demo-video-link.md)

The demo covers:
- **Problem**: Breast cancer screening gaps and care coordination challenges
- **Solution**: AI agent that personalizes screening plans and coordinates care
- **Audience**: Patients, providers, and health systems
- **Technical**: AWS Bedrock + Strands Agents architecture walkthrough
- **Live Demo**: Complete screening workflow from risk assessment to care plan

---

## 🔌 API Reference

### Base URL: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Chat with the CareCircle agent |
| `/api/risk-assessment` | POST | Perform risk assessment |
| `/api/screening/schedule` | POST | Schedule a screening |
| `/api/screening/upcoming/{id}` | GET | Get upcoming screenings |
| `/api/screening/status` | PUT | Update screening status |
| `/api/care-plan/generate` | POST | Generate care plan |
| `/api/care-plan/{id}` | GET | Get care plan |
| `/api/education/{topic}` | GET | Get educational content |
| `/api/education` | GET | List education topics |
| `/api/notifications/send` | POST | Send notification |
| `/api/notifications/{id}` | GET | Get notifications |

Full interactive docs at: `http://localhost:8000/docs`

### Example: Risk Assessment

```bash
curl -X POST http://localhost:8000/api/risk-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "age": 52,
    "family_history": true,
    "genetic_markers": "",
    "previous_biopsies": 1,
    "breast_density": "heterogeneous",
    "hormone_therapy": false,
    "bmi": 27.5,
    "smoking_history": false,
    "alcohol_consumption": "light"
  }'
```

---

## 🧪 Technology Stack

| Component | Technology |
|-----------|-----------|
| **AI Framework** | [Strands Agents](https://github.com/strands-agents/sdk-python) |
| **LLM Provider** | AWS Bedrock (Claude Sonnet) |
| **Backend API** | FastAPI + Uvicorn |
| **Frontend** | Streamlit |
| **Database** | SQLAlchemy + SQLite (async) |
| **Visualization** | Plotly |
| **Containerization** | Docker + Docker Compose |
| **Language** | Python 3.10+ |

---

## 📁 Project Structure

```
carecircle/
├── main.py                     # Main entry point (API/CLI/Demo modes)
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Multi-service orchestration
├── .env.example              # Environment variable template
├── LICENSE                   # MIT License
├── README.md                 # This file
│
├── src/
│   ├── __init__.py
│   ├── config.py             # Application configuration
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   └── care_agent.py     # Strands Agent implementation
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── risk_assessment.py      # Risk calculation tool
│   │   ├── screening_scheduler.py  # Screening management tool
│   │   ├── care_plan_generator.py  # Care plan creation tool
│   │   ├── patient_education.py    # Educational content tool
│   │   └── notification_manager.py # Notification tool
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py       # Database configuration
│   │   ├── patient.py        # Patient model
│   │   ├── screening.py      # Screening models
│   │   ├── care_plan.py      # Care plan models
│   │   └── notification.py   # Notification model
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py           # FastAPI application
│   │   └── routes.py        # API route handlers
│   │
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py  # Streamlit dashboard
│
├── tests/
│   ├── __init__.py
│   ├── test_risk_assessment.py
│   ├── test_screening_scheduler.py
│   └── test_care_plan.py
│
└── docs/
    ├── architecture.md        # Architecture documentation
    └── images/               # Documentation images
```

---

## 🔒 AWS Configuration

### Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        }
    ]
}
```

### Enable Bedrock Model Access

1. Go to AWS Console → Amazon Bedrock
2. Navigate to Model Access
3. Request access to Anthropic Claude models
4. Wait for access approval (usually instant)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ⚠️ Disclaimer

CareCircle is a **screening coordination tool** and is NOT intended to:
- Provide medical diagnoses
- Replace professional medical advice
- Serve as a substitute for clinical judgment
- Make treatment decisions

Always consult with qualified healthcare professionals for medical decisions.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Foundation model service
- [Strands Agents](https://github.com/strands-agents/sdk-python) - Agent framework
- [National Breast Cancer Foundation](https://www.nationalbreastcancer.org) - Educational guidelines
- [American Cancer Society](https://www.cancer.org) - Screening recommendations
- [USPSTF](https://www.uspreventiveservicestaskforce.org) - Screening guidelines

---

<p align="center">
  Made with 💗 for early detection and better outcomes
</p>
