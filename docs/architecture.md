# CareCircle Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CareCircle Platform                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐    ┌──────────────────┐    ┌────────────────────────┐     │
│  │   Streamlit  │    │    FastAPI        │    │    CLI Interface       │     │
│  │   Dashboard  │    │    REST API       │    │    (Interactive Chat)  │     │
│  │   (Port 8501)│    │    (Port 8000)    │    │                        │     │
│  └──────┬───────┘    └────────┬─────────┘    └───────────┬────────────┘     │
│         │                      │                          │                   │
│         └──────────────────────┼──────────────────────────┘                   │
│                                │                                              │
│                    ┌───────────▼───────────┐                                 │
│                    │    Strands Agent      │                                 │
│                    │    Orchestrator       │                                 │
│                    │    (Agent Core)       │                                 │
│                    └───────────┬───────────┘                                 │
│                                │                                              │
│              ┌─────────────────┼─────────────────┐                           │
│              │                 │                   │                           │
│    ┌─────────▼──────┐  ┌─────▼──────┐  ┌────────▼─────────┐                │
│    │  AWS Bedrock   │  │   Tool     │  │   System Prompt   │                │
│    │  LLM Model     │  │   Registry │  │   & Guidelines    │                │
│    │  (Claude)      │  │            │  │                   │                │
│    └────────────────┘  └─────┬──────┘  └───────────────────┘                │
│                              │                                                │
│         ┌────────────────────┼────────────────────────┐                      │
│         │                    │                         │                      │
│  ┌──────▼──────┐  ┌────────▼────────┐  ┌────────────▼──────────┐           │
│  │    Risk     │  │   Screening     │  │    Care Plan           │           │
│  │  Assessment │  │   Scheduler     │  │    Generator           │           │
│  │    Tool     │  │    Tool         │  │     Tool               │           │
│  └─────────────┘  └────────────────┘   └───────────────────────┘           │
│         │                    │                         │                      │
│  ┌──────▼──────┐  ┌────────▼────────┐  ┌────────────▼──────────┐           │
│  │  Patient    │  │  Notification   │  │    Education           │           │
│  │  Education  │  │   Manager       │  │    Content             │           │
│  │    Tool     │  │    Tool         │  │    Library             │           │
│  └─────────────┘  └────────────────┘   └───────────────────────┘           │
│                                                                               │
│                    ┌───────────────────────┐                                 │
│                    │    SQLite Database    │                                 │
│                    │    (Patient Records,  │                                 │
│                    │     Screenings,       │                                 │
│                    │     Care Plans)       │                                 │
│                    └───────────────────────┘                                 │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              │
                    ┌─────────▼─────────┐
                    │   AWS Bedrock     │
                    │   (Claude Model)  │
                    │   us-east-1       │
                    └───────────────────┘
```

## Data Flow

```
Patient/Provider Input
        │
        ▼
┌───────────────────┐     ┌─────────────────────┐
│  User Interface   │────▶│  Strands Agent       │
│  (UI/API/CLI)     │     │  (Orchestrator)      │
└───────────────────┘     └──────────┬────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │   AWS Bedrock LLM   │
                          │   (Reasoning &      │
                          │    Tool Selection)  │
                          └──────────┬──────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                  │
             ┌──────▼──────┐  ┌─────▼─────┐  ┌───────▼──────┐
             │ Risk Tool   │  │Scheduler  │  │Care Plan     │
             │(Assessment) │  │(Booking)  │  │(Generation)  │
             └──────┬──────┘  └─────┬─────┘  └───────┬──────┘
                    │                │                  │
                    └────────────────┼──────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │   Response to User  │
                          │   (with Actions &   │
                          │    Recommendations) │
                          └─────────────────────┘
```

## Component Details

### 1. Strands Agent Core
- **Framework**: AWS Strands Agents SDK
- **Model**: AWS Bedrock (Claude Sonnet)
- **Role**: Orchestrates tool usage, maintains conversation context, provides empathetic responses

### 2. Custom Tools
| Tool | Purpose |
|------|---------|
| `calculate_risk_score` | Calculates personalized risk using modified Gail Model |
| `assess_risk` | Comprehensive risk assessment with recommendations |
| `schedule_screening` | Books screening appointments |
| `get_upcoming_screenings` | Retrieves scheduled screenings |
| `update_screening_status` | Updates appointment outcomes |
| `generate_care_plan` | Creates personalized care plans |
| `get_care_plan` | Retrieves existing care plans |
| `get_educational_content` | Delivers patient education |
| `send_reminder` | Sends notifications/reminders |
| `get_notifications` | Retrieves notification history |

### 3. Interfaces
- **Streamlit Dashboard**: Interactive web UI with visualizations
- **FastAPI REST API**: Programmatic access with OpenAPI docs
- **CLI Chat**: Terminal-based conversational interface

### 4. Data Layer
- **SQLAlchemy ORM**: Async database operations
- **SQLite**: Local development database
- **Models**: Patient, ScreeningRecord, ScreeningSchedule, CarePlan, CareTask, Notification
