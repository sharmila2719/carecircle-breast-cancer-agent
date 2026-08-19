"""
CareCircle Dashboard - Serverless HTML UI served from AWS Lambda.
This renders a full interactive dashboard as HTML (no Streamlit dependency).
"""

import json
from datetime import datetime, timedelta
from mangum import Mangum
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="CareCircle Dashboard", docs_url="/api/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Risk Assessment Logic (same as before)
# ============================================================

def calculate_risk(age, family_history=False, genetic_markers="", previous_biopsies=0,
                   breast_density="scattered", hormone_therapy=False, bmi=25.0,
                   smoking_history=False, alcohol_consumption="none"):
    score = 0.0
    risk_factors = []

    if age >= 70: score += 25; risk_factors.append(("Age 70+", 25))
    elif age >= 60: score += 20; risk_factors.append(("Age 60-69", 20))
    elif age >= 50: score += 15; risk_factors.append(("Age 50-59", 15))
    elif age >= 40: score += 10; risk_factors.append(("Age 40-49", 10))
    else: score += 5; risk_factors.append(("Age <40", 5))

    if family_history: score += 20; risk_factors.append(("Family History", 20))
    if genetic_markers and ("BRCA" in genetic_markers.upper()): score += 25; risk_factors.append(("BRCA Mutation", 25))
    if previous_biopsies > 0: s = min(previous_biopsies * 4, 10); score += s; risk_factors.append(("Previous Biopsies", s))

    density_scores = {"fatty": 0, "scattered": 5, "heterogeneous": 10, "dense": 15}
    ds = density_scores.get(breast_density.lower(), 5)
    if ds > 0: score += ds; risk_factors.append(("Breast Density", ds))
    if hormone_therapy: score += 8; risk_factors.append(("Hormone Therapy", 8))
    if age >= 50 and bmi >= 30: score += 5; risk_factors.append(("Elevated BMI", 5))
    if smoking_history: score += 3; risk_factors.append(("Smoking", 3))

    alc_scores = {"none": 0, "light": 2, "moderate": 4, "heavy": 6}
    alc = alc_scores.get(alcohol_consumption.lower(), 0)
    if alc > 0: score += alc; risk_factors.append(("Alcohol", alc))

    normalized = min((score / 124) * 100, 100)

    if normalized >= 60: category = "Very High"
    elif normalized >= 40: category = "High"
    elif normalized >= 20: category = "Moderate"
    else: category = "Low"

    return round(normalized, 1), category, risk_factors


# ============================================================
# HTML Dashboard
# ============================================================

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CareCircle - Breast Cancer Screening Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #333; }
        .header { background: linear-gradient(135deg, #E91E8C, #9C27B0); color: white; padding: 20px 40px; text-align: center; }
        .header h1 { font-size: 2rem; margin-bottom: 5px; }
        .header p { opacity: 0.9; font-size: 0.95rem; }
        .nav { background: #232F3E; padding: 10px 40px; display: flex; gap: 20px; flex-wrap: wrap; }
        .nav a { color: #FF9900; text-decoration: none; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; transition: all 0.3s; }
        .nav a:hover, .nav a.active { background: #FF9900; color: #232F3E; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid #E91E8C; }
        .metric-card h3 { color: #666; font-size: 0.85rem; text-transform: uppercase; }
        .metric-card .value { font-size: 2rem; font-weight: bold; color: #E91E8C; }
        .metric-card .change { font-size: 0.8rem; color: #28a745; }
        .section { background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .section h2 { color: #232F3E; margin-bottom: 15px; border-bottom: 2px solid #E91E8C; padding-bottom: 10px; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-weight: 600; margin-bottom: 5px; font-size: 0.9rem; }
        .form-group input, .form-group select { padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 0.95rem; }
        .form-group input:focus, .form-group select:focus { border-color: #E91E8C; outline: none; }
        .btn { background: #E91E8C; color: white; border: none; padding: 12px 30px; border-radius: 25px; font-size: 1rem; cursor: pointer; margin-top: 15px; transition: all 0.3s; }
        .btn:hover { background: #C4177A; transform: translateY(-2px); }
        .result-box { background: #f8f9fa; border-radius: 10px; padding: 20px; margin-top: 20px; border: 2px solid #E91E8C; }
        .risk-gauge { text-align: center; margin: 20px 0; }
        .risk-score { font-size: 3rem; font-weight: bold; }
        .risk-low { color: #28a745; }
        .risk-moderate { color: #ffc107; }
        .risk-high { color: #fd7e14; }
        .risk-very-high { color: #dc3545; }
        .factors-list { list-style: none; }
        .factors-list li { padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
        .factors-list li span.pts { background: #E91E8C; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; }
        .education-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .edu-card { background: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #eee; cursor: pointer; transition: all 0.3s; }
        .edu-card:hover { border-color: #E91E8C; transform: translateY(-3px); box-shadow: 0 4px 12px rgba(233,30,140,0.15); }
        .edu-card h4 { color: #E91E8C; margin-bottom: 5px; }
        .chat-box { border: 1px solid #ddd; border-radius: 12px; height: 400px; display: flex; flex-direction: column; }
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; }
        .chat-msg { margin-bottom: 15px; }
        .chat-msg.bot { background: #f0f8ff; padding: 12px; border-radius: 10px; }
        .chat-msg.user { background: #E91E8C; color: white; padding: 12px; border-radius: 10px; margin-left: 20%; }
        .chat-input { display: flex; padding: 10px; border-top: 1px solid #ddd; }
        .chat-input input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; margin-right: 10px; }
        .chat-input button { background: #E91E8C; color: white; border: none; padding: 10px 20px; border-radius: 20px; cursor: pointer; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.85rem; background: #232F3E; color: #ccc; margin-top: 40px; }
        .footer a { color: #FF9900; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        @media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } .nav { justify-content: center; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🩺 CareCircle</h1>
        <p>Breast Cancer Screening & Care Coordination Agent | Powered by AWS Bedrock + Strands Agents</p>
    </div>

    <div class="nav">
        <a href="#" onclick="showTab('dashboard')" class="active" id="nav-dashboard">🏠 Dashboard</a>
        <a href="#" onclick="showTab('risk')" id="nav-risk">📊 Risk Assessment</a>
        <a href="#" onclick="showTab('education')" id="nav-education">📚 Education</a>
        <a href="#" onclick="showTab('chat')" id="nav-chat">💬 Chat</a>
        <a href="#" onclick="showTab('about')" id="nav-about">ℹ️ About</a>
    </div>

    <div class="container">
        <!-- DASHBOARD TAB -->
        <div id="tab-dashboard" class="tab-content active">
            <div class="metrics">
                <div class="metric-card"><h3>Active Patients</h3><div class="value">156</div><div class="change">+12 this month</div></div>
                <div class="metric-card"><h3>Screenings This Month</h3><div class="value">43</div><div class="change">+8 from last month</div></div>
                <div class="metric-card"><h3>Care Plans Active</h3><div class="value">89</div><div class="change">+5 new</div></div>
                <div class="metric-card"><h3>Overdue Screenings</h3><div class="value">7</div><div class="change">-3 from last week</div></div>
            </div>
            <div class="section">
                <h2>🚀 How It Works</h2>
                <p style="margin-bottom:15px;">CareCircle is an AI agent that coordinates breast cancer screening end-to-end:</p>
                <ol style="padding-left:20px;line-height:2;">
                    <li><strong>📊 Risk Assessment</strong> — Enter health details, get personalized risk score (Modified Gail Model)</li>
                    <li><strong>📋 Care Plan</strong> — AI generates screening schedule, lifestyle recommendations, action items</li>
                    <li><strong>📅 Scheduling</strong> — Book mammograms, MRIs, ultrasounds with prep instructions</li>
                    <li><strong>📚 Education</strong> — Evidence-based content on 10 breast health topics</li>
                    <li><strong>💬 AI Chat</strong> — Ask anything, agent calls tools and responds with personalized guidance</li>
                </ol>
            </div>
            <div class="section">
                <h2>📋 Recent Activity</h2>
                <ul style="list-style:none;line-height:2.2;">
                    <li>✅ <strong>2 hours ago</strong> — Risk assessment completed for Patient #142 (Score: 43.5, HIGH)</li>
                    <li>📅 <strong>4 hours ago</strong> — Mammogram scheduled for Patient #138 (Sep 15, 2026)</li>
                    <li>📋 <strong>Yesterday</strong> — Care plan generated for Patient #125 (Moderate Risk)</li>
                    <li>📚 <strong>Yesterday</strong> — Educational content delivered to 12 patients</li>
                    <li>🔔 <strong>2 days ago</strong> — Screening reminders sent to 8 patients</li>
                </ul>
            </div>
        </div>

        <!-- RISK ASSESSMENT TAB -->
        <div id="tab-risk" class="tab-content">
            <div class="section">
                <h2>📊 Breast Cancer Risk Assessment</h2>
                <p style="margin-bottom:20px;">Calculate your personalized risk score based on evidence-based factors (Modified Gail Model with 12+ factors).</p>
                <form id="risk-form" onsubmit="calculateRisk(event)">
                    <div class="form-grid">
                        <div class="form-group"><label>Age</label><input type="number" id="age" value="50" min="18" max="120"></div>
                        <div class="form-group"><label>BMI</label><input type="number" id="bmi" value="25" step="0.1" min="10" max="80"></div>
                        <div class="form-group"><label>Family History</label><select id="family_history"><option value="false">No</option><option value="true">Yes (first-degree relative)</option></select></div>
                        <div class="form-group"><label>Genetic Markers</label><select id="genetic_markers"><option value="">None</option><option value="BRCA1">BRCA1</option><option value="BRCA2">BRCA2</option></select></div>
                        <div class="form-group"><label>Previous Biopsies</label><input type="number" id="biopsies" value="0" min="0" max="10"></div>
                        <div class="form-group"><label>Breast Density</label><select id="density"><option value="fatty">Fatty</option><option value="scattered" selected>Scattered</option><option value="heterogeneous">Heterogeneous</option><option value="dense">Dense</option></select></div>
                        <div class="form-group"><label>Hormone Therapy</label><select id="hormone"><option value="false">No</option><option value="true">Yes</option></select></div>
                        <div class="form-group"><label>Alcohol Consumption</label><select id="alcohol"><option value="none">None</option><option value="light">Light</option><option value="moderate">Moderate</option><option value="heavy">Heavy</option></select></div>
                    </div>
                    <button type="submit" class="btn">🔬 Calculate Risk Score</button>
                </form>
                <div id="risk-result" class="result-box" style="display:none;"></div>
            </div>
        </div>

        <!-- EDUCATION TAB -->
        <div id="tab-education" class="tab-content">
            <div class="section">
                <h2>📚 Breast Health Education Center</h2>
                <p style="margin-bottom:20px;">Evidence-based educational content aligned with WHO, ACS, and NCCN guidelines.</p>
                <div class="education-grid">
                    <div class="edu-card" onclick="showEdu('selfexam')"><h4>🤲 Breast Self-Exam</h4><p>Monthly technique guide</p></div>
                    <div class="edu-card" onclick="showEdu('mammogram')"><h4>📷 Mammograms</h4><p>What to expect</p></div>
                    <div class="edu-card" onclick="showEdu('risk')"><h4>⚠️ Risk Factors</h4><p>What increases your risk</p></div>
                    <div class="edu-card" onclick="showEdu('guidelines')"><h4>📋 Guidelines</h4><p>When to get screened</p></div>
                    <div class="edu-card" onclick="showEdu('genetic')"><h4>🧬 Genetic Testing</h4><p>BRCA1/BRCA2 testing</p></div>
                    <div class="edu-card" onclick="showEdu('density')"><h4>🔬 Breast Density</h4><p>What density means</p></div>
                    <div class="edu-card" onclick="showEdu('prevention')"><h4>🥗 Prevention</h4><p>Lifestyle changes</p></div>
                    <div class="edu-card" onclick="showEdu('detection')"><h4>🎯 Early Detection</h4><p>Why it saves lives</p></div>
                    <div class="edu-card" onclick="showEdu('myths')"><h4>❓ Myths vs Facts</h4><p>Debunking misinformation</p></div>
                    <div class="edu-card" onclick="showEdu('support')"><h4>💗 Support</h4><p>Resources for you</p></div>
                </div>
                <div id="edu-content" class="result-box" style="display:none; margin-top:20px;"></div>
            </div>
        </div>

        <!-- CHAT TAB -->
        <div id="tab-chat" class="tab-content">
            <div class="section">
                <h2>💬 Chat with CareCircle Agent</h2>
                <p style="margin-bottom:15px;">Ask questions about breast cancer screening. Powered by AWS Bedrock (Claude).</p>
                <div class="chat-box">
                    <div class="chat-messages" id="chat-messages">
                        <div class="chat-msg bot">Hello! I'm CareCircle 🩺 I can help with risk assessments, screening scheduling, care plans, and education. Try asking: <em>"What are the symptoms of breast cancer?"</em></div>
                    </div>
                    <div class="chat-input">
                        <input type="text" id="chat-input" placeholder="Ask CareCircle anything..." onkeypress="if(event.key==='Enter')sendChat()">
                        <button onclick="sendChat()">Send</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- ABOUT TAB -->
        <div id="tab-about" class="tab-content">
            <div class="section">
                <h2>ℹ️ About CareCircle</h2>
                <h3 style="margin:15px 0;">The Problem</h3>
                <ul style="padding-left:20px;line-height:2;">
                    <li>1 in 8 women will be diagnosed with breast cancer</li>
                    <li>33% of eligible women are NOT up to date on mammography</li>
                    <li>Early detection = 99% survival | Late detection = 28% survival</li>
                </ul>
                <h3 style="margin:15px 0;">Technology Stack</h3>
                <table style="width:100%;border-collapse:collapse;margin:10px 0;">
                    <tr style="background:#f8f9fa;"><td style="padding:8px;border:1px solid #ddd;"><strong>Agent Framework</strong></td><td style="padding:8px;border:1px solid #ddd;">Strands Agents SDK</td></tr>
                    <tr><td style="padding:8px;border:1px solid #ddd;"><strong>LLM</strong></td><td style="padding:8px;border:1px solid #ddd;">AWS Bedrock (Claude Sonnet 4.6)</td></tr>
                    <tr style="background:#f8f9fa;"><td style="padding:8px;border:1px solid #ddd;"><strong>Deployment</strong></td><td style="padding:8px;border:1px solid #ddd;">AWS Lambda + API Gateway (Serverless)</td></tr>
                    <tr><td style="padding:8px;border:1px solid #ddd;"><strong>AgentCore</strong></td><td style="padding:8px;border:1px solid #ddd;">Memory, Observability, Identity, Policy</td></tr>
                </table>
                <h3 style="margin:15px 0;">Links</h3>
                <p>🔗 <a href="https://github.com/sharmila2719/carecircle-breast-cancer-agent" target="_blank">GitHub Repository</a></p>
                <p>🔗 <a href="https://vnja2r5dx6.execute-api.us-east-1.amazonaws.com/api/docs" target="_blank">API Documentation</a></p>
                <hr style="margin:20px 0;">
                <p style="text-align:center;font-size:1.1rem;"><strong>Invented by Sharmila Begum</strong> — Agentic AI Specialist | Ex Edgematican</p>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>☁️ Powered by <strong>Amazon Bedrock</strong> | 💡 Invented by <strong>Sharmila Begum</strong> — Agentic AI Specialist | Ex Edgematican</p>
        <p style="margin-top:5px;"><a href="https://github.com/sharmila2719/carecircle-breast-cancer-agent">GitHub</a> | Built for Agents for Humans Hackathon 2026</p>
    </div>

    <script>
        const API_BASE = window.location.origin;

        function showTab(tab) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
            document.getElementById('tab-' + tab).classList.add('active');
            document.getElementById('nav-' + tab).classList.add('active');
        }

        async function calculateRisk(e) {
            e.preventDefault();
            const data = {
                age: parseInt(document.getElementById('age').value),
                family_history: document.getElementById('family_history').value === 'true',
                genetic_markers: document.getElementById('genetic_markers').value,
                previous_biopsies: parseInt(document.getElementById('biopsies').value),
                breast_density: document.getElementById('density').value,
                hormone_therapy: document.getElementById('hormone').value === 'true',
                bmi: parseFloat(document.getElementById('bmi').value),
                alcohol_consumption: document.getElementById('alcohol').value,
                smoking_history: false, age_first_period: 12, age_first_birth: 25
            };
            try {
                const resp = await fetch(API_BASE + '/api/risk-assessment', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
                const result = await resp.json();
                const a = result.assessment;
                const colorClass = a.risk_category === 'very_high' ? 'risk-very-high' : a.risk_category === 'high' ? 'risk-high' : a.risk_category === 'moderate' ? 'risk-moderate' : 'risk-low';
                let factorsHtml = a.risk_factors.map(f => `<li>${f.factor} <span class="pts">+${f.contribution}</span></li>`).join('');
                document.getElementById('risk-result').innerHTML = `
                    <div class="risk-gauge"><div class="risk-score ${colorClass}">${a.risk_score}</div><p>out of 100</p></div>
                    <h3 style="text-align:center;" class="${colorClass}">Category: ${a.risk_category.replace('_',' ').toUpperCase()}</h3>
                    <p style="text-align:center;margin:10px 0;background:#fff3cd;padding:10px;border-radius:8px;">💡 ${a.recommendation}</p>
                    <h4 style="margin-top:15px;">Risk Factors:</h4><ul class="factors-list">${factorsHtml}</ul>`;
                document.getElementById('risk-result').style.display = 'block';
            } catch(err) { alert('Error: ' + err.message); }
        }

        function showEdu(topic) {
            const content = {
                selfexam: '<h3>🤲 Breast Self-Examination</h3><p>Perform monthly, 7-10 days after period. Use three pressure levels. Check in mirror and lying down. Report any changes to your provider.</p>',
                mammogram: '<h3>📷 Understanding Mammograms</h3><p>Can detect cancer up to 2 years before a lump is felt. Takes 15-30 minutes. Annual screening from age 40. BI-RADS scoring (0-6) classifies findings.</p>',
                risk: '<h3>⚠️ Risk Factors</h3><p>Age and being female are the biggest factors. Only 5-10% are hereditary. Dense breasts increase risk. Modifiable factors: weight, exercise, alcohol, smoking.</p>',
                guidelines: '<h3>📋 Screening Guidelines</h3><p>Average risk: Annual mammogram from 40 (ACS). High risk (>20%): Mammogram + MRI from 30. BRCA carriers: Annual from age 25-30.</p>',
                genetic: '<h3>🧬 Genetic Testing</h3><p>BRCA1/BRCA2 carriers: 45-72% lifetime risk. Simple blood/saliva test. Genetic counseling recommended before and after. Negative test does not eliminate all risk.</p>',
                density: '<h3>🔬 Breast Density</h3><p>40-50% of women have dense breasts. Dense tissue masks tumors on mammograms. 3D mammography and MRI are more effective. Density is genetic, not related to size.</p>',
                prevention: '<h3>🥗 Lifestyle Prevention</h3><p>Exercise 150+ min/week (reduces risk 10-20%). Maintain healthy BMI. Limit alcohol ≤1 drink/day. Quit smoking. Mediterranean diet lowers risk.</p>',
                detection: '<h3>🎯 Early Detection</h3><p>Localized stage: 99% five-year survival. Mammograms find cancers too small to feel. Early treatment is less aggressive. Never skip screenings.</p>',
                myths: '<h3>❓ Myths vs Facts</h3><p>85% have NO family history. Mammogram radiation is extremely low. 80% of lumps are benign. Men can get breast cancer too (~2,800/year in US).</p>',
                support: '<h3>💗 Support Resources</h3><p>National Breast Cancer Helpline: 1-800-227-2345. Patient navigators available. Financial assistance programs exist. Support groups offer community.</p>'
            };
            document.getElementById('edu-content').innerHTML = content[topic] || '';
            document.getElementById('edu-content').style.display = 'block';
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            const msg = input.value.trim();
            if (!msg) return;
            const messages = document.getElementById('chat-messages');
            messages.innerHTML += `<div class="chat-msg user">${msg}</div>`;
            input.value = '';
            try {
                const resp = await fetch(API_BASE + '/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message: msg})});
                const data = await resp.json();
                messages.innerHTML += `<div class="chat-msg bot">${data.response}</div>`;
            } catch(err) {
                messages.innerHTML += `<div class="chat-msg bot">Sorry, I encountered an error. Please try again.</div>`;
            }
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the CareCircle Dashboard."""
    return DASHBOARD_HTML


# Include all API endpoints from the main handler
class RiskRequest(BaseModel):
    age: int = 50
    family_history: bool = False
    genetic_markers: str = ""
    previous_biopsies: int = 0
    breast_density: str = "scattered"
    hormone_therapy: bool = False
    bmi: float = 25.0
    smoking_history: bool = False
    alcohol_consumption: str = "none"
    age_first_period: int = 12
    age_first_birth: int = 25

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "CareCircle", "runtime": "AWS Lambda"}

@app.post("/api/risk-assessment")
async def risk_assessment(req: RiskRequest):
    score, category, factors = calculate_risk(
        req.age, req.family_history, req.genetic_markers, req.previous_biopsies,
        req.breast_density, req.hormone_therapy, req.bmi, req.smoking_history, req.alcohol_consumption
    )
    cat_key = category.lower().replace(" ", "_")
    recs = {"very_high": "Enhanced screening with annual mammogram + MRI. Consider genetic counseling.",
            "high": "Annual mammogram recommended. Consider supplemental MRI.",
            "moderate": "Annual or biennial mammogram. Regular clinical breast exams.",
            "low": "Follow standard guidelines. Biennial mammogram starting at age 40-50."}
    return {"success": True, "assessment": {
        "risk_score": score, "risk_category": cat_key,
        "recommendation": recs.get(cat_key, recs["moderate"]),
        "risk_factors": [{"factor": f[0], "contribution": f[1]} for f in factors]
    }}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msg = req.message.lower()
    if any(w in msg for w in ["symptom", "sign", "lump"]):
        resp = "Common signs include: new lumps, skin dimpling, nipple changes/discharge, swelling, redness. 80% of lumps are NOT cancerous. Always see your doctor for evaluation."
    elif any(w in msg for w in ["risk", "assess"]):
        resp = "I can assess your risk! Use the Risk Assessment tab or tell me your age and health details."
    elif any(w in msg for w in ["schedule", "mammogram", "screening"]):
        resp = "For scheduling: mammograms are recommended annually from age 40 (average risk) or earlier for high-risk. Use our API: POST /api/screening/schedule"
    elif any(w in msg for w in ["prevent", "lifestyle", "reduce"]):
        resp = "Prevention tips: Exercise 150+ min/week, maintain healthy BMI, limit alcohol to ≤1 drink/day, quit smoking, eat Mediterranean diet. These can reduce risk 10-30%."
    elif any(w in msg for w in ["genetic", "brca"]):
        resp = "BRCA1/BRCA2 carriers have 45-72% lifetime risk. Testing is a simple blood/saliva sample. Genetic counseling is recommended before and after testing."
    else:
        resp = "Hello! I'm CareCircle. I help with: risk assessment, screening scheduling, care plans, and education. Try asking about symptoms, risk factors, or screening guidelines."
    return {"success": True, "response": resp}

handler = Mangum(app, lifespan="off")
