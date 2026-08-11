# CareCircle - Pitch Deck Content

## Slide 1: Title
**CareCircle**
Breast Cancer Screening & Care Coordination Agent
Powered by AWS Bedrock Strands Agents

---

## Slide 2: The Problem
### Breast Cancer Screening Gaps

- **1 in 8 women** will be diagnosed with breast cancer in their lifetime
- **33% of eligible women** are NOT up to date on mammography
- **Early detection** improves 5-year survival from 28% → 99%
- Care coordination is **fragmented** across multiple providers
- Patients struggle to understand their **personal risk** and appropriate screening schedule
- Healthcare providers lack tools for **personalized screening recommendations**

---

## Slide 3: Who It's For

### Primary Users:
1. **Patients** - Women seeking guidance on screening schedules and risk factors
2. **Healthcare Providers** - Managing screening programs and patient care
3. **Care Coordinators** - Ensuring compliance and follow-up
4. **Health Systems** - Improving early detection metrics

### Scale of Impact:
- 42 million women ages 40-74 in the US alone
- Over 280,000 new breast cancer cases annually
- $30B+ annual cost of breast cancer treatment in the US

---

## Slide 4: Why It Matters

### Every Missed Screening is a Missed Chance

| Detection Stage | 5-Year Survival | Treatment Complexity |
|----------------|-----------------|---------------------|
| Localized (early) | 99% | Minimal |
| Regional (spread) | 86% | Moderate |
| Distant (late) | 28% | Extensive |

**AI-powered coordination can:**
- Personalize screening plans based on individual risk
- Reduce barriers to scheduling
- Improve adherence through intelligent reminders
- Ensure no patient falls through the cracks

---

## Slide 5: Solution - CareCircle

### An AI Agent That:
1. 📊 **Assesses Risk** - Personalized scoring using 12+ evidence-based factors
2. 📅 **Coordinates Screening** - Intelligent scheduling with prep instructions
3. 📋 **Creates Care Plans** - Tailored to individual risk profiles
4. 📚 **Educates Patients** - Clear, empathetic health information
5. 🔔 **Manages Follow-ups** - Automated reminders and tracking

### Built With:
- **AWS Bedrock** (Claude) for natural language reasoning
- **Strands Agents** framework for tool orchestration
- **Evidence-based** risk models (modified Gail Model)

---

## Slide 6: Architecture

```
User (Patient/Provider)
        │
   ┌────▼────┐
   │ UI/API  │  (Streamlit / FastAPI / CLI)
   └────┬────┘
        │
   ┌────▼──────────┐
   │ Strands Agent │  ← System Prompt (care guidelines)
   └────┬──────────┘
        │
   ┌────▼──────────┐
   │ AWS Bedrock   │  (Claude - reasoning engine)
   └────┬──────────┘
        │
   ┌────▼──────────────────────────┐
   │ Custom Tools                   │
   │ • Risk Assessment             │
   │ • Screening Scheduler         │
   │ • Care Plan Generator         │
   │ • Patient Education           │
   │ • Notification Manager        │
   └───────────────────────────────┘
```

---

## Slide 7: Demo Highlights

1. **Risk Assessment** → Score: 45/100 (High Risk)
2. **Smart Scheduling** → Auto-recommends mammogram + MRI
3. **Care Plan** → Personalized tasks, timeline, lifestyle guidance
4. **Education** → Tailored content delivery
5. **Conversational** → Natural language interaction

---

## Slide 8: Technical Implementation

| Component | Technology |
|-----------|-----------|
| Agent Framework | Strands Agents SDK |
| LLM | AWS Bedrock (Claude Sonnet) |
| Backend | FastAPI (Python) |
| Frontend | Streamlit |
| Risk Model | Modified Gail Model |
| Database | SQLAlchemy + SQLite |
| Deployment | Docker + AWS ECS |
| CI/CD | GitHub Actions |

---

## Slide 9: Impact & Next Steps

### Current Capabilities:
✅ Personalized risk assessment (12+ factors)
✅ Intelligent screening scheduling
✅ Automated care plan generation
✅ Comprehensive patient education (10+ topics)
✅ Multi-channel notifications
✅ Conversational AI interface

### Future Roadmap:
- EHR integration (FHIR)
- Multi-language support
- Mobile companion app
- Population health analytics
- Clinical trial matching
- Insurance navigation

---

## Slide 10: Call to Action

**CareCircle**: AI-powered care coordination that doesn't replace your doctor — it helps you get to them on time.

🔗 GitHub: [Repository Link]
📄 License: MIT (Open Source)
🏗️ Built for: Agents for Humans Hackathon 2026
☁️ Powered by: AWS Bedrock + Strands Agents

---

*"Early detection saves lives. CareCircle makes early detection easier."*
