# CareCircle - AWS Architecture Diagram

## Full AWS Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              USERS / CLIENTS                                          │
│                                                                                       │
│     👩 Patient              👨‍⚕️ Provider            📱 Mobile App                       │
│     (Web Browser)           (EHR Integration)       (Future)                          │
│                                                                                       │
└──────────┬─────────────────────────┬───────────────────────┬────────────────────────┘
           │                         │                       │
           ▼                         ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           AWS CLOUD (us-east-1)                                       │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────┐  │
│  │                         PRESENTATION LAYER                                      │  │
│  │                                                                                  │  │
│  │   ┌─────────────────────┐         ┌──────────────────────────────────┐          │  │
│  │   │  Streamlit Cloud    │         │  Amazon API Gateway (HTTP API)   │          │  │
│  │   │  ┌───────────────┐  │         │  • HTTPS/TLS 1.3                 │          │  │
│  │   │  │ Dashboard UI  │  │         │  • CORS enabled                  │          │  │
│  │   │  │ • Risk Form   │  │         │  • Rate limiting                 │          │  │
│  │   │  │ • Charts      │  │         │  • Request validation            │          │  │
│  │   │  │ • Education   │  │         │                                  │          │  │
│  │   │  │ • AI Chat     │  │         │  Routes:                         │          │  │
│  │   │  └───────────────┘  │         │  GET  /                          │          │  │
│  │   │                     │         │  GET  /health                    │          │  │
│  │   │  URL: *.streamlit.app│        │  POST /api/risk-assessment       │          │  │
│  │   └─────────────────────┘         │  POST /api/screening/schedule   │          │  │
│  │                                    │  POST /api/care-plan/generate   │          │  │
│  │                                    │  GET  /api/education/{topic}    │          │  │
│  │                                    │  POST /api/chat                 │          │  │
│  │                                    │  GET  /docs (Swagger)           │          │  │
│  │                                    └──────────────┬───────────────────┘          │  │
│  └───────────────────────────────────────────────────┼─────────────────────────────┘  │
│                                                       │                                │
│  ┌───────────────────────────────────────────────────┼─────────────────────────────┐  │
│  │                         COMPUTE LAYER              │                              │  │
│  │                                                    ▼                              │  │
│  │   ┌──────────────────────────────────────────────────────────────────────────┐   │  │
│  │   │                    AWS Lambda Function                                    │   │  │
│  │   │                    (carecircle-api)                                       │   │  │
│  │   │                                                                           │   │  │
│  │   │   Runtime: Python 3.10 | Memory: 512MB | Timeout: 30s                    │   │  │
│  │   │                                                                           │   │  │
│  │   │   ┌─────────────────────────────────────────────────────────────────┐    │   │  │
│  │   │   │              Strands Agent (Orchestrator)                        │    │   │  │
│  │   │   │                                                                  │    │   │  │
│  │   │   │   • System Prompt (medical guidelines + safety guardrails)       │    │   │  │
│  │   │   │   • Tool Selection & Execution Loop                              │    │   │  │
│  │   │   │   • Conversation Management                                      │    │   │  │
│  │   │   │                                                                  │    │   │  │
│  │   │   │   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │    │   │  │
│  │   │   │   │ @tool      │ │ @tool      │ │ @tool      │ │ @tool      │  │    │   │  │
│  │   │   │   │ Risk       │ │ Screening  │ │ Care Plan  │ │ Education  │  │    │   │  │
│  │   │   │   │ Assessment │ │ Scheduler  │ │ Generator  │ │ Content    │  │    │   │  │
│  │   │   │   └────────────┘ └────────────┘ └────────────┘ └────────────┘  │    │   │  │
│  │   │   │                                                                  │    │   │  │
│  │   │   │   ┌────────────┐                                                │    │   │  │
│  │   │   │   │ @tool      │                                                │    │   │  │
│  │   │   │   │ Notifica-  │                                                │    │   │  │
│  │   │   │   │ tions      │                                                │    │   │  │
│  │   │   │   └────────────┘                                                │    │   │  │
│  │   │   └─────────────────────────────────────────────────────────────────┘    │   │  │
│  │   │                                                                           │   │  │
│  │   │   Wrapped with: Mangum (ASGI → Lambda adapter)                           │   │  │
│  │   │   Framework: FastAPI                                                      │   │  │
│  │   └──────────────────────────────────────────────────────────────────────────┘   │  │
│  │                                                                                   │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                           │                                             │
│  ┌────────────────────────────────────────┼──────────────────────────────────────────┐  │
│  │                         AI LAYER       │                                           │  │
│  │                                        ▼                                           │  │
│  │   ┌──────────────────────────────────────────────────────────────────────────┐    │  │
│  │   │                    Amazon Bedrock                                         │    │  │
│  │   │                                                                           │    │  │
│  │   │   Model: Claude Sonnet 4.6 (Anthropic)                                  │    │  │
│  │   │                                                                           │    │  │
│  │   │   Capabilities:                                                           │    │  │
│  │   │   • Natural language understanding                                        │    │  │
│  │   │   • Tool/function calling                                                 │    │  │
│  │   │   • Multi-turn conversation                                               │    │  │
│  │   │   • Reasoning about patient risk factors                                  │    │  │
│  │   │   • Empathetic health communication                                       │    │  │
│  │   │                                                                           │    │  │
│  │   │   API: ConverseStream (via Strands BedrockModel)                         │    │  │
│  │   └──────────────────────────────────────────────────────────────────────────┘    │  │
│  │                                                                                    │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                    AGENTCORE PRIMITIVES (Production Infrastructure)                  │  │
│  │                                                                                      │  │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │  │
│  │   │   Memory     │  │  Identity    │  │ Observability│  │     Policy       │      │  │
│  │   │              │  │              │  │              │  │                  │      │  │
│  │   │ • Session    │  │ • OAuth2     │  │ • OpenTele-  │  │ • No diagnosis   │      │  │
│  │   │   state      │  │   tokens     │  │   metry      │  │ • PII protection │      │  │
│  │   │ • Patient    │  │ • HIPAA      │  │ • CloudWatch │  │ • Topic restrict │      │  │
│  │   │   history    │  │   access     │  │ • Traces     │  │ • Content filter │      │  │
│  │   │ • Risk       │  │ • Credential │  │ • Metrics    │  │                  │      │  │
│  │   │   results    │  │   rotation   │  │              │  │                  │      │  │
│  │   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘      │  │
│  │                                                                                      │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                    INFRASTRUCTURE & DEVOPS                                           │  │
│  │                                                                                      │  │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │  │
│  │   │  AWS SAM     │  │    S3        │  │  CloudWatch  │  │  IAM             │      │  │
│  │   │  (IaC)       │  │  (Artifacts) │  │  (Logs)      │  │  (Permissions)   │      │  │
│  │   │              │  │              │  │              │  │                  │      │  │
│  │   │ • template   │  │ • Lambda     │  │ • Function   │  │ • bedrock:       │      │  │
│  │   │   .yaml      │  │   packages   │  │   logs       │  │   InvokeModel    │      │  │
│  │   │ • Auto       │  │ • Deploy     │  │ • API Gateway│  │ • lambda:        │      │  │
│  │   │   deploy     │  │   artifacts  │  │   access logs│  │   Invoke         │      │  │
│  │   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘      │  │
│  │                                                                                      │  │
│  └────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Simplified Data Flow Diagram

```
                    ┌───────────────────────┐
                    │      User Input       │
                    │  "I'm 55 with family  │
                    │   history. My risk?"  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Amazon API Gateway  │
                    │   (HTTPS endpoint)    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     AWS Lambda        │
                    │   ┌───────────────┐   │
                    │   │ Strands Agent │   │
                    │   └───────┬───────┘   │
                    └───────────┼───────────┘
                                │
                    ┌───────────┼───────────┐
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐   ┌───────────────────┐
        │  Amazon Bedrock   │   │  Custom Tools     │
        │  (Claude LLM)     │   │                   │
        │                   │   │  • Risk Calculator│
        │  Reasons about    │   │  • Scheduler      │
        │  the question     │   │  • Care Planner   │
        │  Selects tools    │   │  • Education      │
        │  Generates reply  │   │  • Notifications  │
        └───────────────────┘   └───────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Personalized        │
                    │   Response            │
                    │                       │
                    │  "Your risk score is  │
                    │   43.5 (HIGH). You    │
                    │   need annual mammo-  │
                    │   gram + MRI..."      │
                    └───────────────────────┘
```

---

## AWS Services Used

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS SERVICES MAP                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│   COMPUTE          AI/ML              NETWORKING              │
│   ┌──────────┐    ┌──────────────┐   ┌────────────────┐     │
│   │ Lambda   │    │ Bedrock      │   │ API Gateway    │     │
│   │          │    │ (Claude)     │   │ (HTTP API)     │     │
│   └──────────┘    └──────────────┘   └────────────────┘     │
│                                                               │
│   STORAGE          SECURITY           MANAGEMENT             │
│   ┌──────────┐    ┌──────────────┐   ┌────────────────┐     │
│   │ S3       │    │ IAM          │   │ CloudFormation │     │
│   │(Deploys) │    │ (Roles)      │   │ (SAM/IaC)     │     │
│   └──────────┘    └──────────────┘   └────────────────┘     │
│                                                               │
│   MONITORING       AGENTCORE                                  │
│   ┌──────────┐    ┌──────────────┐                           │
│   │CloudWatch│    │ Memory       │                           │
│   │ (Logs)   │    │ Identity     │                           │
│   └──────────┘    │ Observability│                           │
│                    │ Policy       │                           │
│                    └──────────────┘                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│            GitHub Repository                 │
│  github.com/sharmila2719/carecircle-...     │
└──────────┬──────────────────┬───────────────┘
           │                  │
     (auto-deploy)      (sam deploy)
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌──────────────────────────────┐
│ Streamlit Cloud  │  │  AWS CloudFormation Stack     │
│                  │  │                                │
│ • Dashboard UI   │  │  ┌────────────────────────┐  │
│ • Risk Forms     │  │  │  API Gateway (HTTP)    │  │
│ • Charts         │  │  └───────────┬────────────┘  │
│ • AI Chat        │  │              │                │
│                  │  │  ┌───────────▼────────────┐  │
│ Port: 443 (HTTPS)│  │  │  Lambda Function       │  │
│                  │  │  │  (carecircle-api)       │  │
│ Auto-redeploy   │  │  └───────────┬────────────┘  │
│ on git push     │  │              │                │
└──────────────────┘  │  ┌───────────▼────────────┐  │
                      │  │  Amazon Bedrock         │  │
                      │  │  (Claude Sonnet 4.6)    │  │
                      │  └────────────────────────┘  │
                      │                                │
                      │  Region: us-east-1             │
                      └──────────────────────────────────┘
```
