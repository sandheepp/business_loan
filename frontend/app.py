"""CASA MVP — Streamlit main app (home page)."""
import streamlit as st

st.set_page_config(
    page_title="CASA — AI Loan Origination",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global API base URL
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

st.markdown("""
<style>
    .main-header { font-size: 3rem; font-weight: 800; color: #1B3A5C; margin-bottom: 0; }
    .sub-header { font-size: 1.3rem; color: #2E75B6; margin-top: -10px; }
    .metric-card {
        background: linear-gradient(135deg, #E8F0F8, #FFFFFF);
        border-left: 4px solid #2E75B6; padding: 1.2rem;
        border-radius: 8px; margin-bottom: 1rem;
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #1B3A5C; }
    .metric-label { font-size: 0.9rem; color: #666; }
    .agent-card {
        background: #FAFBFC; border: 1px solid #E1E8ED; border-radius: 10px;
        padding: 1.2rem; height: 100%;
    }
    .agent-name { font-weight: 700; color: #1B3A5C; font-size: 1.1rem; }
    .agent-model { font-size: 0.8rem; color: #2E75B6; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🏦 CASA</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Loan Origination System</p>', unsafe_allow_html=True)
st.markdown("---")

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div class="metric-card">
        <div class="metric-value">81%</div>
        <div class="metric-label">Application Completion Rate</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class="metric-card">
        <div class="metric-value">50%+</div>
        <div class="metric-label">Churn Reactivation Rate</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="metric-card">
        <div class="metric-value">24-48h</div>
        <div class="metric-label">Time to Completed File</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown("""<div class="metric-card">
        <div class="metric-value">10x</div>
        <div class="metric-label">More Loans Per Officer</div>
    </div>""", unsafe_allow_html=True)

st.markdown("## Agent Architecture")

agents = [
    ("🤖 Sarah", "Engagement Agent", "claude-sonnet-4-20250514",
     "Conversational AI, churn detection, applicant reactivation"),
    ("🛡️ Compliance", "Compliance Agent", "Rules + claude-sonnet-4-20250514",
     "KYB/KYC, watchlist screening, SBA SOP eligibility, SPSS scoring"),
    ("📊 Underwriting", "Underwriting Agent", "Deterministic + claude-sonnet-4-20250514",
     "Financial spreading, DSCR, credit policy scoring, memo generation"),
    ("📄 Document", "Document Intelligence", "claude-sonnet-4-20250514 (vision)",
     "OCR, classification, field extraction, cross-doc validation"),
    ("💰 Pricing", "Pricing Agent", "Deterministic + claude-haiku-4-5-20251001",
     "Risk-based rate calculation, term sheet generation"),
    ("⚙️ Orchestrator", "Orchestrator Agent", "No LLM (deterministic)",
     "State machine, agent coordination, escalation routing"),
]

cols = st.columns(3)
for i, (icon, name, model, desc) in enumerate(agents):
    with cols[i % 3]:
        st.markdown(f"""<div class="agent-card">
            <div class="agent-name">{icon} {name}</div>
            <div class="agent-model">{model}</div>
            <p style="font-size: 0.9rem; color: #555; margin-top: 8px;">{desc}</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("")

st.markdown("---")
st.markdown("### Quick Start")
st.markdown("""
Use the **sidebar** to navigate between pages:

1. **📋 Application** — Submit a new loan application (as a borrower)
2. **💬 Sarah Chat** — Talk to Sarah, the AI engagement agent
3. **📊 Dashboard** — Loan officer pipeline view with full audit trail
4. **📜 Audit Trail** — Browse the immutable agent action log
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**API Status**")
try:
    import requests
    r = requests.get(f"{st.session_state.api_url}/health", timeout=2)
    if r.status_code == 200:
        st.sidebar.success("Backend: Connected")
    else:
        st.sidebar.error("Backend: Error")
except Exception:
    st.sidebar.warning("Backend: Not running — start with `uvicorn backend.main:app`")
