"""Loan Officer Dashboard — Pipeline view and loan details."""
import streamlit as st
import requests
import pandas as pd

API = st.session_state.get("api_url", "http://localhost:8000")

st.set_page_config(page_title="CASA — Dashboard", page_icon="📊", layout="wide")
st.title("📊 Loan Officer Dashboard")

# ── Pipeline Stats ──
try:
    stats = requests.get(f"{API}/api/dashboard/stats").json()
except Exception:
    st.error("Cannot connect to backend. Start with: `uvicorn backend.main:app --port 8000`")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Applications", stats["total_applications"])
col2.metric("Draft", stats["draft"])
col3.metric("In Review", stats["in_review"])
col4.metric("Approved", stats["approved"])
col5.metric("Avg Completion", f"{stats['avg_completion']}%")

st.markdown("---")

# ── Application List ──
st.markdown("### Pipeline")
try:
    apps = requests.get(f"{API}/api/applications/").json()
except Exception:
    apps = []

if not apps:
    st.info("No applications yet. Go to the **Application** page to create one.")
    st.stop()

for app in apps:
    status_colors = {
        "draft": "🟡", "submitted": "🔵", "officer_review": "🟠",
        "approved": "🟢", "declined": "🔴",
    }
    icon = status_colors.get(app["status"], "⚪")

    with st.expander(
        f"{icon} {app['business_name'] or 'Unnamed'} — "
        f"${app['loan_amount']:,.0f} {app['loan_product']} — "
        f"Status: {app['status'].replace('_', ' ').title()}"
    ):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Applicant**")
            st.write(f"Name: {app['applicant_name']}")
            st.write(f"Email: {app['applicant_email']}")
        with col2:
            st.markdown("**Loan Details**")
            st.write(f"Amount: ${app['loan_amount']:,.0f}")
            st.write(f"Purpose: {app['loan_purpose']}")
            st.write(f"Product: {app['loan_product']}")
        with col3:
            st.markdown("**Scores**")
            st.write(f"Risk Score: {app['risk_score']}/100")
            st.write(f"DSCR: {app['dscr']}")
            st.write(f"Credit: {app['credit_score']}")
            st.write(f"Completion: {app['completion_pct']}%")

        # Action buttons
        bcol1, bcol2, bcol3 = st.columns(3)
        with bcol1:
            if app["status"] == "submitted":
                if st.button(f"🚀 Run Full Pipeline", key=f"pipe_{app['id']}"):
                    with st.spinner("Running compliance → underwriting → pricing..."):
                        r = requests.post(f"{API}/api/applications/{app['id']}/run-pipeline")
                        if r.status_code == 200:
                            result = r.json()
                            st.success("Pipeline complete! Refresh to see results.")
                            st.json(result)
                        else:
                            st.error("Pipeline failed.")
        with bcol2:
            if st.button(f"📜 View Audit Log", key=f"audit_{app['id']}"):
                r = requests.get(f"{API}/api/dashboard/audit/{app['id']}")
                if r.status_code == 200:
                    entries = r.json()
                    for e in entries:
                        st.markdown(
                            f"**{e['agent']}** — {e['action']}  \n"
                            f"_{e['created_at']}_"
                        )
                        if e["details"]:
                            st.json(e["details"])
        with bcol3:
            if st.button(f"💬 View Chat", key=f"chat_{app['id']}"):
                r = requests.get(f"{API}/api/chat/{app['id']}/history")
                if r.status_code == 200:
                    for m in r.json():
                        who = "🧑 Applicant" if m["role"] == "user" else "🤖 Sarah"
                        st.markdown(f"**{who}:** {m['content']}")
