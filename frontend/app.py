"""CASA — AI-Powered MSME Loan Origination System (Home Page)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from styles import page_config_dark, sidebar_status, format_inr

page_config_dark("Home", "🏦")

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

API = st.session_state.api_url

# ── Fetch stats ───────────────────────────────────────────────
try:
    import requests
    stats = requests.get(f"{API}/api/dashboard/stats", timeout=3).json()
    total     = stats.get("total_applications", 0)
    disbursed = stats.get("disbursed", 0)
    underwrit = stats.get("underwriting", 0)
    sanctioned= stats.get("sanctioned", 0)
    total_val = stats.get("total_loan_value", 0)
    avg_comp  = stats.get("avg_completion", 0)
    backend_ok = True
except Exception:
    total = disbursed = underwrit = sanctioned = 0
    total_val = avg_comp = 0
    backend_ok = False

# ── Hero ──────────────────────────────────────────────────────
_dot_label = "Backend Connected" if backend_ok else "Backend Offline"

hero_left, hero_right = st.columns([1.6, 1], gap="large")

with hero_left:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0C0F1E 0%,rgba(91,76,245,0.2) 60%,rgba(0,212,138,0.07) 100%);
                border:1px solid rgba(91,76,245,0.25);border-radius:20px;padding:2rem 2.2rem 1.8rem;
                position:relative;overflow:hidden;height:100%;">
      <div style="position:absolute;top:-50px;right:-50px;width:220px;height:220px;
                  background:radial-gradient(circle,rgba(91,76,245,0.3),transparent 70%);pointer-events:none;"></div>
      <div style="position:absolute;bottom:-60px;left:20%;width:240px;height:240px;
                  background:radial-gradient(circle,rgba(0,212,138,0.1),transparent 70%);pointer-events:none;"></div>
      <div style="font-size:0.68rem;color:#7B6BF8;text-transform:uppercase;letter-spacing:0.15em;
                  font-weight:700;margin-bottom:0.8rem;">AI-Powered · RBI Compliant · India MSME</div>
      <div style="font-size:3rem;font-weight:900;letter-spacing:-0.04em;line-height:1;
                  background:linear-gradient(135deg,#FFFFFF 30%,#A09BFF 70%,#00D48A 100%);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
                  margin-bottom:0.8rem;">CASA LOS</div>
      <div style="font-size:0.88rem;color:#8A8FA8;line-height:1.7;max-width:420px;margin-bottom:1.3rem;">
        Loan Origination System for MSME Secured Loans in India.<br>
        From lead to disbursement — fully automated, human-in-the-loop.
      </div>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
        <span style="background:rgba(0,212,138,0.12);color:#00D48A;border:1px solid rgba(0,212,138,0.3);
                     padding:0.28rem 0.8rem;border-radius:100px;font-size:0.72rem;font-weight:600;">15-Stage Pipeline</span>
        <span style="background:rgba(91,76,245,0.12);color:#A09BFF;border:1px solid rgba(91,76,245,0.3);
                     padding:0.28rem 0.8rem;border-radius:100px;font-size:0.72rem;font-weight:600;">PAN · Aadhaar · CIBIL</span>
        <span style="background:rgba(59,158,245,0.12);color:#3B9EF5;border:1px solid rgba(59,158,245,0.3);
                     padding:0.28rem 0.8rem;border-radius:100px;font-size:0.72rem;font-weight:600;">CAM Auto-Generation</span>
        <span style="background:rgba(245,166,35,0.12);color:#F5A623;border:1px solid rgba(245,166,35,0.3);
                     padding:0.28rem 0.8rem;border-radius:100px;font-size:0.72rem;font-weight:600;">RBI MSME Guidelines</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with hero_right:
    st.markdown("""
    <div style="font-size:0.63rem;color:#8A8FA8;text-transform:uppercase;
                letter-spacing:0.1em;font-weight:600;margin-bottom:0.6rem;">Live Pipeline</div>
    """, unsafe_allow_html=True)

    for lbl, val, clr in [
        ("Total Applications", str(total),           "#FFFFFF"),
        ("Loan Book Value",    format_inr(total_val), "#7B6BF8"),
        ("In Underwriting",   str(underwrit),         "#F5A623"),
        ("Disbursed",          str(disbursed),         "#00D48A"),
    ]:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                    border-radius:10px;padding:0.6rem 1rem;display:flex;
                    justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
          <span style="font-size:0.76rem;color:#8A8FA8;">{lbl}</span>
          <span style="font-size:0.92rem;font-weight:800;color:{clr};">{val}</span>
        </div>
        """, unsafe_allow_html=True)

    # Use native Streamlit to avoid HTML leaking for the status dot
    dot = "🟢" if backend_ok else "🔴"
    st.caption(f"{dot} {_dot_label}")

st.markdown("<div style='margin-bottom:1.2rem;'></div>", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────
kpis = [
    ("Total Applications", str(total),             "#FFFFFF", "📋", "rgba(255,255,255,0.06)", "rgba(255,255,255,0.1)"),
    ("Loan Book Value",    format_inr(total_val),  "#7B6BF8", "💰", "rgba(91,76,245,0.12)",  "rgba(91,76,245,0.3)"),
    ("In Underwriting",   str(underwrit),          "#F5A623", "📊", "rgba(245,166,35,0.12)", "rgba(245,166,35,0.3)"),
    ("Disbursed",          str(disbursed),          "#00D48A", "✅", "rgba(0,212,138,0.12)",  "rgba(0,212,138,0.3)"),
    ("Avg Completion",     f"{avg_comp:.0f}%",      "#3B9EF5", "📈", "rgba(59,158,245,0.12)", "rgba(59,158,245,0.3)"),
]

cols = st.columns(5)
for col, (label, val, color, icon, bg, border) in zip(cols, kpis):
    bg2 = bg.replace('0.12', '0.03')
    with col:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{bg},{bg2});
                    border:1px solid {border};border-radius:14px;padding:1rem 0.6rem;
                    text-align:center;margin-bottom:1.2rem;">
          <div style="font-size:1.1rem;margin-bottom:0.25rem;">{icon}</div>
          <div style="font-size:1.4rem;font-weight:900;letter-spacing:-0.03em;color:{color};
                      line-height:1.1;white-space:nowrap;overflow:hidden;
                      text-overflow:ellipsis;">{val}</div>
          <div style="font-size:0.62rem;color:#8A8FA8;text-transform:uppercase;
                      letter-spacing:0.06em;margin-top:0.35rem;line-height:1.3;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Main content: Pipeline + Agents ──────────────────────────
col_pipe, col_agents = st.columns([1, 1], gap="large")

# ── Pipeline ──────────────────────────────────────────────────
with col_pipe:
    st.markdown('<div class="rv-section-title">15-STAGE LOS PIPELINE</div>', unsafe_allow_html=True)

    stages = [
        ("01", "Lead Creation",        "Borrower inquiry, RM assignment, duplicate check",     "done"),
        ("02", "Borrower Application", "Promoter KYC, business details, collateral info",      "done"),
        ("03", "KYC Verification",     "PAN · Aadhaar · CKYC · Watchlist screening",           "active"),
        ("04", "Document Collection",  "Identity, Business, Financial, Collateral docs",        "pending"),
        ("05", "Data Extraction",      "OCR · Bank statement parsing · ITR parsing",           "pending"),
        ("06", "External Enrichment",  "CIBIL · GSTN · MCA · Bank aggregation",               "pending"),
        ("07", "Financial Analysis",   "DSCR · Debt/Equity · Revenue growth · Margins",        "pending"),
        ("08", "Collateral Assessment","LTV · Legal title · Encumbrance check",                "pending"),
        ("09", "Credit Underwriting",  "Risk scoring · Anomaly detection · Credit policy",     "pending"),
        ("10", "Credit Memo (CAM)",    "AI-generated CAM draft · Analyst review",              "pending"),
        ("11", "Approval Workflow",    "BCM / RCH / Credit Committee routing",                 "pending"),
        ("12", "Sanction Letter",      "Auto-generated · Digital signature",                   "pending"),
        ("13", "Legal Documentation",  "Loan agreement · Mortgage deed · Guarantee",           "pending"),
        ("14", "Disbursement",         "CBS integration · Funds transfer",                     "pending"),
        ("15", "Post-Disbursement",    "GST filing · EMI behavior · Revenue tracking",         "pending"),
    ]

    stage_cfg = {
        "done":    ("#00D48A", "rgba(0,212,138,0.08)",  "rgba(0,212,138,0.22)",  "✓"),
        "active":  ("#7B6BF8", "rgba(91,76,245,0.13)",  "rgba(91,76,245,0.4)",   "●"),
        "pending": ("#4A4E6A", "transparent",            "rgba(255,255,255,0.06)",""),
    }

    # Group into done / active / pending sections visually
    for num, name, desc, state in stages:
        color, bg, border, icon = stage_cfg[state]
        text_color = "#FFFFFF" if state in ("done", "active") else "#6B6F8A"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.8rem;padding:0.55rem 0.9rem;
                    border:1px solid {border};border-radius:10px;background:{bg};
                    margin-bottom:0.3rem;transition:all 0.2s;">
          <div style="width:24px;height:24px;border-radius:6px;flex-shrink:0;
                      background:{'linear-gradient(135deg,#00D48A22,#00D48A08)' if state=='done' else 'rgba(91,76,245,0.2)' if state=='active' else 'rgba(255,255,255,0.04)'};
                      border:1px solid {border};display:flex;align-items:center;justify-content:center;">
            <span style="font-size:0.6rem;font-weight:800;color:{color};">{icon if icon else num}</span>
          </div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:0.82rem;font-weight:700;color:{text_color};white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;">{name}</div>
            <div style="font-size:0.7rem;color:#4A4E6A;margin-top:1px;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;">{desc}</div>
          </div>
          <div style="font-size:0.65rem;color:{color};font-weight:700;flex-shrink:0;">
            {'DONE' if state=='done' else 'ACTIVE' if state=='active' else f'{num}'}
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Agents + Navigation ───────────────────────────────────────
with col_agents:
    st.markdown('<div class="rv-section-title">AI AGENT ARCHITECTURE</div>', unsafe_allow_html=True)

    agents = [
        ("💬", "Sarah",        "Engagement Agent",     "claude-sonnet-4-6",               "#7B6BF8", "rgba(91,76,245,0.15)",  "Borrower engagement, churn prevention, application guidance"),
        ("🛡️", "KYC Agent",   "Compliance",           "Deterministic + AI",              "#3B9EF5", "rgba(59,158,245,0.12)", "PAN / Aadhaar / CKYC validation, CIBIL, MSME eligibility"),
        ("📄", "Document AI",  "Document Intelligence","claude-sonnet-4-6 Vision",        "#F5A623", "rgba(245,166,35,0.12)", "OCR extraction, categorisation, cross-document validation"),
        ("📊", "Underwriting", "Credit Analysis",      "Deterministic + claude-sonnet-4-6","#00D48A","rgba(0,212,138,0.12)",  "DSCR, LTV, Debt/Equity, risk rating, CAM generation"),
        ("💰", "Pricing",      "Pricing Agent",        "Deterministic",                   "#FF6B8A", "rgba(255,59,87,0.1)",   "Risk-based rate pricing, EMI calculation, term sheet"),
        ("⚙️", "Orchestrator","Workflow Engine",       "State Machine",                   "#8A8FA8", "rgba(255,255,255,0.05)","15-stage routing, approval hierarchy, immutable audit trail"),
    ]

    for icon, name, role, model, color, bg, desc in agents:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{bg},rgba(0,0,0,0));
                    border:1px solid {color}33;border-radius:12px;padding:0.9rem 1.1rem;
                    margin-bottom:0.5rem;display:flex;gap:0.9rem;align-items:flex-start;">
          <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
                      background:{color}22;border:1px solid {color}44;
                      display:flex;align-items:center;justify-content:center;font-size:1.1rem;">
            {icon}
          </div>
          <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:baseline;gap:0.5rem;margin-bottom:0.15rem;">
              <span style="font-size:0.88rem;font-weight:700;color:#FFFFFF;">{name}</span>
              <span style="font-size:0.7rem;color:#8A8FA8;">{role}</span>
            </div>
            <div style="font-size:0.68rem;color:{color};font-family:monospace;font-weight:600;
                        margin-bottom:0.25rem;">{model}</div>
            <div style="font-size:0.75rem;color:#6B6F8A;line-height:1.4;">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="rv-section-title" style="margin-top:1.2rem;">QUICK NAVIGATION</div>', unsafe_allow_html=True)

    nav_items = [
        ("📋", "Application",  "Submit new MSME loan",       "#7B6BF8", "rgba(91,76,245,0.12)"),
        ("💬", "Sarah Chat",   "AI borrower guidance",       "#3B9EF5", "rgba(59,158,245,0.1)"),
        ("📊", "Dashboard",    "Pipeline & analytics",       "#F5A623", "rgba(245,166,35,0.1)"),
        ("🏦", "Underwriting", "Credit analysis & CAM",      "#00D48A", "rgba(0,212,138,0.1)"),
        ("✅", "Approvals",    "BCM / RCH / CC decisions",   "#A09BFF", "rgba(160,155,255,0.1)"),
        ("📜", "Audit Trail",  "Immutable compliance log",   "#8A8FA8", "rgba(255,255,255,0.05)"),
    ]

    nav_cols = st.columns(2)
    for i, (icon, name, desc, color, bg) in enumerate(nav_items):
        with nav_cols[i % 2]:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {color}33;border-radius:10px;
                        padding:0.7rem 0.9rem;margin-bottom:0.4rem;cursor:pointer;">
              <div style="display:flex;align-items:center;gap:0.5rem;">
                <span style="font-size:1rem;">{icon}</span>
                <div>
                  <div style="font-size:0.82rem;font-weight:700;color:{color};">{name}</div>
                  <div style="font-size:0.7rem;color:#6B6F8A;">{desc}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="margin:0.5rem 0 1.2rem;padding:1rem 1rem 1rem;
            background:linear-gradient(135deg,rgba(91,76,245,0.18),rgba(0,212,138,0.05));
            border:1px solid rgba(91,76,245,0.28);border-radius:14px;
            position:relative;overflow:hidden;">
  <div style="position:absolute;top:-20px;right:-20px;width:80px;height:80px;
              background:radial-gradient(circle,rgba(91,76,245,0.35),transparent 70%);
              pointer-events:none;"></div>
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem;">
    <div style="width:32px;height:32px;border-radius:8px;flex-shrink:0;
                background:linear-gradient(135deg,#5B4CF5,#8B7FF8);
                display:flex;align-items:center;justify-content:center;
                font-size:1rem;box-shadow:0 4px 12px rgba(91,76,245,0.4);">🏦</div>
    <div style="font-size:1.25rem;font-weight:900;letter-spacing:-0.04em;
                background:linear-gradient(135deg,#FFFFFF 30%,#A09BFF);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;line-height:1;">CASA</div>
  </div>
  <div style="font-size:0.72rem;color:#8A8FA8;font-weight:500;letter-spacing:0.01em;
              padding-left:2px;">MSME Loan Origination System</div>
  <div style="display:flex;gap:0.35rem;margin-top:0.7rem;flex-wrap:wrap;">
    <span style="font-size:0.62rem;font-weight:600;color:#00D48A;
                 background:rgba(0,212,138,0.1);border:1px solid rgba(0,212,138,0.25);
                 padding:0.15rem 0.5rem;border-radius:100px;">RBI Compliant</span>
    <span style="font-size:0.62rem;font-weight:600;color:#A09BFF;
                 background:rgba(91,76,245,0.1);border:1px solid rgba(91,76,245,0.25);
                 padding:0.15rem 0.5rem;border-radius:100px;">15-Stage LOS</span>
  </div>
</div>
""", unsafe_allow_html=True)
sidebar_status()
