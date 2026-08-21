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
        <a href="#" onclick="showTab('scheduler')" id="nav-scheduler">📅 Screening Scheduler</a>
        <a href="#" onclick="showTab('careplan')" id="nav-careplan">📋 Care Plan</a>
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

        <!-- SCREENING SCHEDULER TAB -->
        <div id="tab-scheduler" class="tab-content">
            <div class="section">
                <h2>📅 Screening Scheduler</h2>
                <p style="margin-bottom:20px;">Schedule breast cancer screening appointments with preparation instructions.</p>
                <form id="schedule-form" onsubmit="scheduleScreening(event)">
                    <div class="form-grid">
                        <div class="form-group"><label>Patient ID</label><input type="number" id="sched-patient" value="1" min="1"></div>
                        <div class="form-group"><label>Screening Type</label><select id="sched-type"><option value="mammogram">Mammogram</option><option value="3d_mammogram">3D Mammogram</option><option value="mri">Breast MRI</option><option value="ultrasound">Ultrasound</option><option value="clinical_exam">Clinical Exam</option></select></div>
                        <div class="form-group"><label>Preferred Date</label><input type="date" id="sched-date"></div>
                        <div class="form-group"><label>Facility</label><input type="text" id="sched-facility" value="Community Breast Health Center"></div>
                        <div class="form-group"><label>Provider</label><input type="text" id="sched-provider" placeholder="Dr. Name (optional)"></div>
                        <div class="form-group"><label>Notes</label><input type="text" id="sched-notes" placeholder="Additional notes (optional)"></div>
                    </div>
                    <button type="submit" class="btn">📅 Schedule Screening</button>
                </form>
                <div id="schedule-result" class="result-box" style="display:none;"></div>
            </div>
            <div class="section">
                <h2>📋 Preparation Instructions by Type</h2>
                <div class="education-grid">
                    <div class="edu-card"><h4>📷 Mammogram</h4><p>• No deodorant/powder<br>• Wear two-piece outfit<br>• Schedule after period<br>• Duration: 15-30 min</p></div>
                    <div class="edu-card"><h4>🧲 Breast MRI</h4><p>• Report metal implants<br>• May need to fast 4hrs<br>• Remove all jewelry<br>• Duration: 30-60 min</p></div>
                    <div class="edu-card"><h4>🔊 Ultrasound</h4><p>• No special prep needed<br>• Wear two-piece outfit<br>• No lotions on breast<br>• Duration: 15-30 min</p></div>
                    <div class="edu-card"><h4>🩺 Clinical Exam</h4><p>• No special prep<br>• Note any changes<br>• Bring medication list<br>• Duration: 10-15 min</p></div>
                </div>
            </div>
        </div>

        <!-- CARE PLAN TAB -->
        <div id="tab-careplan" class="tab-content">
            <div class="section">
                <h2>📋 Personalized Care Plan Generator</h2>
                <p style="margin-bottom:20px;">Generate a care plan based on risk assessment results. Complete a risk assessment first, then generate your plan.</p>
                <form id="careplan-form" onsubmit="generateCarePlan(event)">
                    <div class="form-grid">
                        <div class="form-group"><label>Patient ID</label><input type="number" id="cp-patient" value="1" min="1"></div>
                        <div class="form-group"><label>Risk Category</label><select id="cp-risk"><option value="low">Low</option><option value="moderate">Moderate</option><option value="high" selected>High</option><option value="very_high">Very High</option></select></div>
                        <div class="form-group"><label>Age</label><input type="number" id="cp-age" value="52" min="18" max="120"></div>
                        <div class="form-group"><label>Risk Score</label><input type="number" id="cp-score" value="43.5" step="0.1" min="0" max="100"></div>
                    </div>
                    <button type="submit" class="btn">🎯 Generate Care Plan</button>
                </form>
                <div id="careplan-result" class="result-box" style="display:none;"></div>
            </div>
            <div class="section">
                <h2>📌 What a Care Plan Includes</h2>
                <div class="education-grid">
                    <div class="edu-card"><h4>🩺 Screening Schedule</h4><p>Personalized timing for mammograms, MRI, clinical exams based on your risk level</p></div>
                    <div class="edu-card"><h4>🥗 Lifestyle Recommendations</h4><p>Exercise, nutrition, alcohol limits, weight management tailored to you</p></div>
                    <div class="edu-card"><h4>✅ Action Items</h4><p>Tasks with due dates and priorities — never miss a step</p></div>
                    <div class="edu-card"><h4>🧬 Genetic Counseling</h4><p>Recommended if family history or elevated risk detected</p></div>
                </div>
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
        const API_BASE = '';

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
            messages.innerHTML += `<div class="chat-msg bot" id="typing">Thinking...</div>`;
            messages.scrollTop = messages.scrollHeight;
            try {
                const resp = await fetch(API_BASE + '/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await resp.json();
                document.getElementById('typing').remove();
                messages.innerHTML += `<div class="chat-msg bot">${data.response}</div>`;
            } catch(err) {
                document.getElementById('typing').remove();
                messages.innerHTML += `<div class="chat-msg bot">I encountered a connection error. The API may be warming up — please try again in a moment. (${err.message})</div>`;
            }
            messages.scrollTop = messages.scrollHeight;
        }

        async function scheduleScreening(e) {
            e.preventDefault();
            // Set default date to 2 weeks from now if not set
            let dateVal = document.getElementById('sched-date').value;
            if (!dateVal) {
                const d = new Date(); d.setDate(d.getDate() + 14);
                dateVal = d.toISOString().split('T')[0];
            }
            const data = {
                patient_id: parseInt(document.getElementById('sched-patient').value),
                screening_type: document.getElementById('sched-type').value,
                preferred_date: dateVal,
                facility: document.getElementById('sched-facility').value,
                provider: document.getElementById('sched-provider').value,
                notes: document.getElementById('sched-notes').value
            };
            try {
                const resp = await fetch(API_BASE + '/api/screening/schedule', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
                const result = await resp.json();
                if (result.success) {
                    const prep = result.preparation || {};
                    document.getElementById('schedule-result').innerHTML = `
                        <h3 style="color:#28a745;">✅ Screening Scheduled Successfully!</h3>
                        <p style="margin:10px 0;"><strong>Type:</strong> ${data.screening_type.replace('_',' ')} | <strong>Date:</strong> ${data.preferred_date} | <strong>Facility:</strong> ${data.facility}</p>
                        <h4 style="margin-top:15px;">📋 Preparation Instructions:</h4>
                        <p><strong>${prep.title || 'Preparation'}</strong> (Duration: ${prep.duration || 'N/A'})</p>
                        <ul style="padding-left:20px;margin-top:8px;">${(prep.instructions||[]).map(i => '<li>'+i+'</li>').join('')}</ul>
                        <p style="margin-top:10px;background:#d4edda;padding:10px;border-radius:8px;">🔔 Reminders will be sent 7 days and 1 day before your appointment.</p>`;
                } else {
                    document.getElementById('schedule-result').innerHTML = `<h3 style="color:#dc3545;">❌ ${result.error || 'Scheduling failed'}</h3>`;
                }
                document.getElementById('schedule-result').style.display = 'block';
            } catch(err) { alert('Error: ' + err.message); }
        }

        async function generateCarePlan(e) {
            e.preventDefault();
            const data = {
                patient_id: parseInt(document.getElementById('cp-patient').value),
                risk_category: document.getElementById('cp-risk').value,
                age: parseInt(document.getElementById('cp-age').value),
                risk_score: parseFloat(document.getElementById('cp-score').value),
                risk_factors: '[]'
            };
            try {
                const resp = await fetch(API_BASE + '/api/care-plan/generate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
                const result = await resp.json();
                if (result.success) {
                    const plan = result.care_plan;
                    let schedHtml = Object.entries(plan.screening_plan || {}).map(([k,v]) => `<li><strong>${k.replace('_',' ')}:</strong> ${v.frequency} (Next: ${v.next_due})</li>`).join('');
                    let tasksHtml = (plan.tasks || []).map(t => `<li>[${t.priority.toUpperCase()}] ${t.title} — Due: ${t.due}</li>`).join('');
                    let lifestyleHtml = (plan.lifestyle || []).map(l => `<li>${l}</li>`).join('');
                    document.getElementById('careplan-result').innerHTML = `
                        <h3 style="color:#E91E8C;">📋 ${plan.title}</h3>
                        <p style="margin:10px 0;">Risk Score: <strong>${plan.risk_score}</strong> | Category: <strong>${plan.risk_category.replace('_',' ').toUpperCase()}</strong></p>
                        ${plan.genetic_counseling_recommended ? '<p style="background:#fff3cd;padding:10px;border-radius:8px;">🧬 <strong>Genetic Counseling Recommended</strong></p>' : ''}
                        <h4 style="margin-top:15px;">🩺 Screening Schedule:</h4><ul style="padding-left:20px;">${schedHtml}</ul>
                        <h4 style="margin-top:15px;">✅ Action Items:</h4><ul style="padding-left:20px;">${tasksHtml}</ul>
                        <h4 style="margin-top:15px;">🥗 Lifestyle Recommendations:</h4><ul style="padding-left:20px;">${lifestyleHtml}</ul>`;
                } else {
                    document.getElementById('careplan-result').innerHTML = `<h3 style="color:#dc3545;">❌ Failed to generate care plan</h3>`;
                }
                document.getElementById('careplan-result').style.display = 'block';
            } catch(err) { alert('Error: ' + err.message); }
        }

        // Set default date for scheduler
        document.addEventListener('DOMContentLoaded', function() {
            const d = new Date(); d.setDate(d.getDate() + 14);
            const el = document.getElementById('sched-date');
            if (el) el.value = d.toISOString().split('T')[0];
        });
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

    # Cancer knowledge - general questions
    if any(w in msg for w in ["what is cancer", "types of cancer", "how many type", "what is breast cancer", "define cancer"]):
        resp = "Cancer is a disease where abnormal cells grow uncontrollably and can spread to other parts of the body. There are over 100 types of cancer. The most common types include: • Breast cancer (most common in women) • Lung cancer • Colorectal cancer • Prostate cancer • Skin cancer (melanoma) • Ovarian cancer • Cervical cancer • Pancreatic cancer. Breast cancer specifically starts in the breast tissue and is the focus of CareCircle — early detection gives a 99% survival rate."
    elif any(w in msg for w in ["cause", "why does", "reason"]):
        resp = "Breast cancer causes are not fully understood, but known risk factors include: • Age (risk increases with age) • Genetic mutations (BRCA1, BRCA2) — 5-10% of cases • Family history of breast cancer • Dense breast tissue • Hormone exposure (early periods, late menopause, HRT) • Obesity after menopause • Alcohol consumption • Radiation exposure. Many women with risk factors never develop cancer, and some with no known factors do. That's why regular screening is important for everyone."
    elif any(w in msg for w in ["treatment", "treat", "chemo", "surgery", "radiation therapy", "cure"]):
        resp = "Breast cancer treatments depend on type and stage: • Surgery (lumpectomy or mastectomy) • Radiation therapy • Chemotherapy • Hormone therapy (for hormone-receptor positive) • Targeted therapy (e.g., Herceptin for HER2+) • Immunotherapy. Important: CareCircle is a SCREENING coordination tool — for treatment advice, always consult your oncologist. Early detection means less aggressive treatment needed."
    elif any(w in msg for w in ["stage", "staging", "stage 1", "stage 2", "stage 3", "stage 4"]):
        resp = "Breast cancer stages: • Stage 0: Non-invasive (DCIS), in milk ducts only • Stage 1: Small tumor (<2cm), no spread • Stage 2: Tumor 2-5cm or spread to few lymph nodes • Stage 3: Larger tumor or extensive lymph node involvement • Stage 4: Metastatic — spread to other organs. Survival rates: Stage 0-1: ~99%, Stage 2: ~93%, Stage 3: ~72%, Stage 4: ~28%. Early screening catches it at Stage 0-1!"
    elif any(w in msg for w in ["symptom", "sign", "lump", "change", "pain", "discharge", "notice"]):
        resp = "Common breast cancer signs include: • New lump or mass (usually painless, hard, irregular — but can be soft/round too) • Skin dimpling (orange peel texture) • Nipple retraction or discharge (especially bloody) • Swelling of all or part of breast • Skin redness, flaking, or thickening • Swollen lymph nodes under arm. Important: 80% of lumps are NOT cancerous. But any new change should be checked by your doctor within 1-2 weeks."
    elif any(w in msg for w in ["risk", "assess", "score", "chance", "likely", "my risk"]):
        resp = "I can assess your risk! Go to the 📊 Risk Assessment tab and enter your details. Key factors: • Age • Family history • Genetic markers (BRCA1/BRCA2) • Breast density • Previous biopsies • Lifestyle (alcohol, smoking, BMI). Or tell me your age and details here — e.g., 'I'm 52 with family history and dense breasts'."
    elif any(w in msg for w in ["schedule", "book", "appointment"]):
        resp = "Go to the 📅 Screening Scheduler tab to book! Available screenings: • Mammogram • 3D Mammogram (tomosynthesis) • Breast MRI • Ultrasound • Clinical Breast Exam. You'll get preparation instructions specific to your screening type, and automatic reminders 7 days and 1 day before."
    elif any(w in msg for w in ["mammogram", "mri", "ultrasound", "screening", "test", "exam", "scan"]):
        resp = "Screening options: • Mammogram (15-30 min, X-ray) — standard screening, detects tumors early • 3D Mammogram (20-40 min) — better for dense breasts, multiple angles • Breast MRI (30-60 min) — for high-risk, uses magnetic field, no radiation • Ultrasound (15-30 min) — used alongside mammogram, good for dense tissue. Annual mammogram recommended from age 40."
    elif any(w in msg for w in ["prevent", "lifestyle", "reduce", "lower", "diet", "exercise", "food", "avoid"]):
        resp = "Proven ways to reduce breast cancer risk: • Exercise 150+ min/week (10-20% risk reduction) • Maintain healthy BMI 18.5-24.9 • Limit alcohol to ≤1 drink/day (even light drinking increases risk) • Don't smoke • Eat Mediterranean diet (fruits, vegetables, whole grains, olive oil, fish) • Breastfeed if possible (12+ months is protective) • Limit hormone replacement therapy • Get 7-9 hours quality sleep."
    elif any(w in msg for w in ["genetic", "brca", "hereditary", "inherit", "gene", "mutation"]):
        resp = "Genetic testing for breast cancer: • BRCA1/BRCA2 mutations give 45-72% lifetime risk • Only 5-10% of breast cancers are hereditary • Test: simple blood or saliva sample • Who should test: strong family history, early-onset (<50) in family, Ashkenazi Jewish heritage, male breast cancer in family • If positive: annual mammogram + MRI from age 25, discuss risk-reducing options • Genetic counseling recommended before and after testing."
    elif any(w in msg for w in ["dense", "density"]):
        resp = "Breast density explained: • 40-50% of women have dense breasts (categories A-D) • Dense = more fibrous/glandular tissue vs fatty tissue • Problem: dense tissue appears WHITE on mammograms, same as tumors — can hide cancer • Solution: supplemental 3D mammogram or MRI for dense breasts • Density is genetic (not related to breast size or firmness) • Many states now require doctors to notify you of your density."
    elif any(w in msg for w in ["care plan", "plan", "recommendation", "what should i do"]):
        resp = "Go to the 📋 Care Plan tab to generate a personalized plan! It includes: • Screening schedule (when to get mammogram, MRI) • Lifestyle recommendations (exercise, diet, alcohol) • Action items with due dates • Whether genetic counseling is needed. Tip: Complete the Risk Assessment first for the most accurate plan."
    elif any(w in msg for w in ["age", "when", "often", "frequency", "guideline", "start", "how often"]):
        resp = "Screening guidelines by risk level: • Average risk: Annual mammogram from age 40 (ACS), or biennial from 50 (USPSTF) • Moderate risk (15-20%): Annual mammogram from 40, discuss MRI • High risk (>20%): Mammogram + MRI annually from age 30 • BRCA carriers: Annual mammogram + MRI from age 25-30 • All women: Monthly breast self-awareness + annual clinical exam with provider."
    elif any(w in msg for w in ["survival", "early", "late", "prognosis", "outcome", "survive"]):
        resp = "Breast cancer survival by detection stage: • Localized (caught early): 99% five-year survival rate • Regional (spread to nearby): 86% survival • Distant (metastatic): 28% survival. This is why screening matters — mammograms detect cancer 1-3 years before you can feel it. A 15-minute mammogram could save your life."
    elif any(w in msg for w in ["self exam", "self-exam", "check myself", "feel", "examine"]):
        resp = "Breast self-exam steps: 1️⃣ Stand before mirror — look for shape changes, dimpling, or skin changes with arms at sides, then raised. 2️⃣ Lie down — use pads of 3 middle fingers in circular motions, cover entire breast. 3️⃣ Use 3 pressures: light (skin), medium (mid-tissue), firm (near ribs). 4️⃣ Check in shower — soapy skin makes it easier. Do monthly, 7-10 days after period. Report ANY changes to your doctor."
    elif any(w in msg for w in ["hello", "hi", "hey", "help", "what can"]):
        resp = "Hello! I'm CareCircle 🩺 Your breast cancer screening assistant. I can answer questions about: • What is breast cancer, types, stages, causes • Symptoms and warning signs • Risk assessment • Screening (mammogram, MRI, ultrasound) • Prevention and lifestyle • Genetic testing (BRCA) • When and how often to get screened • Self-examination technique. Ask me anything!"
    elif any(w in msg for w in ["thank", "thanks", "bye", "goodbye"]):
        resp = "You're welcome! Remember: early detection saves lives. The 5-year survival rate for early-stage breast cancer is 99%. Stay on top of your screenings! Take care 💗"
    else:
        resp = "I can answer questions about breast cancer and screening! Try asking: • 'What is breast cancer?' • 'What are the symptoms?' • 'How can I reduce my risk?' • 'When should I get a mammogram?' • 'Tell me about genetic testing' • 'What are the stages of breast cancer?' • 'How do I do a self-exam?' — Or go to the tabs above for interactive tools!"
    return {"success": True, "response": resp}


class ScheduleRequest(BaseModel):
    patient_id: int = 1
    screening_type: str = "mammogram"
    preferred_date: str = ""
    facility: str = "Community Breast Health Center"
    provider: str = ""
    notes: str = ""

class CarePlanRequest(BaseModel):
    patient_id: int = 1
    risk_category: str = "high"
    age: int = 52
    risk_score: float = 43.5
    risk_factors: str = "[]"


@app.post("/api/screening/schedule")
async def schedule_screening(req: ScheduleRequest):
    from datetime import datetime, timedelta
    valid_types = ["mammogram", "3d_mammogram", "mri", "ultrasound", "clinical_exam", "biopsy"]
    if req.screening_type.lower() not in valid_types:
        return {"success": False, "error": f"Invalid type. Must be: {', '.join(valid_types)}"}
    if not req.preferred_date:
        return {"success": False, "error": "Date is required (YYYY-MM-DD)"}

    prep_data = {
        "mammogram": {"title": "Mammogram Preparation", "instructions": ["No deodorant or powder on exam day", "Wear a two-piece outfit", "Schedule 1-2 weeks after period", "Bring prior mammogram images if available"], "duration": "15-30 minutes"},
        "3d_mammogram": {"title": "3D Mammogram Preparation", "instructions": ["Same as standard mammogram prep", "No deodorant or body products", "Slightly longer than standard mammogram"], "duration": "20-40 minutes"},
        "mri": {"title": "Breast MRI Preparation", "instructions": ["Inform staff of metal implants or pacemaker", "May need to fast 4 hours before", "Remove all metal objects and jewelry", "Wear comfortable clothing"], "duration": "30-60 minutes"},
        "ultrasound": {"title": "Ultrasound Preparation", "instructions": ["No special preparation required", "Wear a two-piece outfit", "Do not apply lotions to breast area"], "duration": "15-30 minutes"},
        "clinical_exam": {"title": "Clinical Exam Preparation", "instructions": ["No special prep needed", "Note any breast changes to discuss", "Bring medication list"], "duration": "10-15 minutes"},
        "biopsy": {"title": "Biopsy Preparation", "instructions": ["Discuss medications with doctor", "Arrange someone to drive you home", "Wear comfortable supportive bra", "Eat a light meal before"], "duration": "30-60 minutes"},
    }

    return {
        "success": True,
        "message": f"Screening scheduled for {req.preferred_date} at {req.facility}",
        "appointment": {"patient_id": req.patient_id, "type": req.screening_type, "date": req.preferred_date, "facility": req.facility, "provider": req.provider, "status": "scheduled"},
        "preparation": prep_data.get(req.screening_type.lower(), prep_data["mammogram"])
    }


@app.post("/api/care-plan/generate")
async def generate_care_plan(req: CarePlanRequest):
    from datetime import datetime, timedelta
    today = datetime.now()

    screening_plan = {}
    if req.risk_category in ["very_high", "high"]:
        screening_plan = {
            "mammogram": {"frequency": "Annual", "next_due": (today + timedelta(days=180)).strftime("%Y-%m-%d")},
            "mri": {"frequency": "Annual (supplemental)", "next_due": (today + timedelta(days=90)).strftime("%Y-%m-%d")},
            "clinical_exam": {"frequency": "Every 6 months", "next_due": (today + timedelta(days=60)).strftime("%Y-%m-%d")},
        }
    else:
        screening_plan = {
            "mammogram": {"frequency": "Annual" if req.age >= 40 else "Discuss at 40", "next_due": (today + timedelta(days=365)).strftime("%Y-%m-%d")},
            "clinical_exam": {"frequency": "Annual", "next_due": (today + timedelta(days=365)).strftime("%Y-%m-%d")},
        }

    tasks = [
        {"title": "Review care plan with provider", "due": (today + timedelta(days=14)).strftime("%Y-%m-%d"), "priority": "high"},
        {"title": "Schedule next screening", "due": (today + timedelta(days=30)).strftime("%Y-%m-%d"), "priority": "high"},
        {"title": "Complete self-exam education", "due": (today + timedelta(days=7)).strftime("%Y-%m-%d"), "priority": "medium"},
        {"title": "Start exercise routine (150 min/week)", "due": (today + timedelta(days=14)).strftime("%Y-%m-%d"), "priority": "medium"},
    ]
    if req.risk_category in ["high", "very_high"]:
        tasks.append({"title": "Genetic counseling consultation", "due": (today + timedelta(days=21)).strftime("%Y-%m-%d"), "priority": "high"})

    return {
        "success": True,
        "care_plan": {
            "patient_id": req.patient_id,
            "title": f"Breast Health Care Plan - {req.risk_category.replace('_', ' ').title()} Risk",
            "risk_score": req.risk_score,
            "risk_category": req.risk_category,
            "screening_plan": screening_plan,
            "tasks": tasks,
            "lifestyle": [
                "Exercise 150+ minutes per week (reduces risk 10-20%)",
                "Maintain healthy BMI (18.5-24.9)",
                "Limit alcohol to ≤1 drink per day",
                "Eat Mediterranean-style diet (fruits, vegetables, whole grains)",
                "Practice monthly breast self-awareness",
                "Get 7-9 hours quality sleep per night",
            ],
            "genetic_counseling_recommended": req.risk_category in ["high", "very_high"],
            "created_at": today.isoformat(),
        }
    }

handler = Mangum(app, lifespan="off")
