"""Loan Officer Dashboard — India MSME LOS Pipeline View."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import pandas as pd
from styles import page_config_dark, sidebar_status, format_inr, status_badge

page_config_dark("Dashboard", "📊")

API = st.session_state.get("api_url", "http://localhost:8000")

st.sidebar.markdown("""
<div style="padding:0.5rem 0 1rem;">
  <div style="font-size:1.3rem;font-weight:800;color:#FFFFFF;">Dashboard</div>
  <div style="font-size:0.75rem;color:#8A8FA8;">Loan Officer Pipeline View</div>
</div>
""", unsafe_allow_html=True)
sidebar_status()

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem;">
  <div>
    <div style="font-size:1.8rem;font-weight:800;letter-spacing:-0.03em;color:#FFFFFF;">Loan Pipeline</div>
    <div style="font-size:0.85rem;color:#8A8FA8;">MSME Secured Loan Origination — All Applications</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Stats ────────────────────────────────────────────────
try:
    stats = requests.get(f"{API}/api/dashboard/stats", timeout=3).json()
except Exception:
    st.error("Cannot connect to backend. Start with: `uvicorn backend.main:app --port 8000`")
    st.stop()

col1, col2, col3, col4, col5, col6 = st.columns(6)
kpis = [
    (col1, stats.get("total_applications", 0), "Total", None),
    (col2, stats.get("kyc_pending", 0), "KYC Pending", "#F5A623"),
    (col3, stats.get("underwriting", 0), "Underwriting", "#5B4CF5"),
    (col4, stats.get("sanctioned", 0), "Sanctioned", "#00D48A"),
    (col5, stats.get("disbursed", 0), "Disbursed", "#00D48A"),
    (col6, stats.get("declined", 0), "Declined", "#FF3B57"),
]
for col, val, label, color in kpis:
    with col:
        clr = color or "#FFFFFF"
        st.markdown(f"""
        <div class="rv-card" style="text-align:center;padding:1rem 0.5rem;">
          <div style="font-size:1.8rem;font-weight:800;color:{clr};">{val}</div>
          <div style="font-size:0.72rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.06em;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

total_val = stats.get("total_loan_value", 0)
avg_comp = stats.get("avg_completion", 0)

st.markdown(f"""
<div style="display:flex;gap:1rem;margin-bottom:1.5rem;">
  <div class="rv-card" style="flex:1;padding:1rem 1.2rem;">
    <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;">Total Loan Book</div>
    <div style="font-size:1.5rem;font-weight:800;color:#7B6BF8;">{format_inr(total_val)}</div>
  </div>
  <div class="rv-card" style="flex:1;padding:1rem 1.2rem;">
    <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;">Avg Completion</div>
    <div style="font-size:1.5rem;font-weight:800;color:#3B9EF5;">{avg_comp:.1f}%</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Application List ──────────────────────────────────────────
col_filter1, col_filter2 = st.columns([2, 1])
with col_filter1:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#FFFFFF;margin-bottom:0.8rem;">All Applications</div>', unsafe_allow_html=True)
with col_filter2:
    filter_status = st.selectbox(
        "Filter by Status", ["All"] + [
            "lead_created", "application_submitted", "kyc_pending", "kyc_verified",
            "document_collection", "underwriting", "pending_bcm", "pending_rch",
            "pending_cc", "sanctioned", "disbursed", "declined"
        ],
        label_visibility="collapsed", key="status_filter"
    )

try:
    url = f"{API}/api/applications/"
    if filter_status and filter_status != "All":
        url += f"?status={filter_status}"
    apps = requests.get(url, timeout=3).json()
except Exception:
    apps = []

if not apps:
    st.markdown("""
    <div class="rv-card" style="text-align:center;padding:3rem;color:#8A8FA8;">
      <div style="font-size:2rem;margin-bottom:0.8rem;">📭</div>
      <div style="font-weight:600;">No applications yet</div>
      <div style="font-size:0.85rem;margin-top:0.3rem;">Go to <strong>Application</strong> page to create the first lead.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

for app in apps:
    bid = app["id"]
    biz = app.get("business_name") or app.get("applicant_name") or "—"
    amount = app.get("loan_amount", 0)
    status = app.get("status", "")
    dscr = app.get("dscr", 0)
    risk = app.get("risk_score", 0)
    cibil = app.get("cibil_score", 0)
    comp = app.get("completion_pct", 0)
    ltv = app.get("ltv_ratio", 0)
    constitution = app.get("business_constitution", "")

    with st.expander(f"  {biz}  ·  {format_inr(amount)}  ·  {status.replace('_',' ').title()}"):
        st.markdown(status_badge(status), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        r1c1, r1c2, r1c3 = st.columns(3)

        with r1c1:
            st.markdown(f"""
            <div class="rv-card" style="padding:1rem;">
              <div class="rv-section-title">APPLICANT</div>
              <div class="rv-stat-row"><span class="rv-stat-label">Name</span><span class="rv-stat-value">{app.get('applicant_name','—')}</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">Email</span><span class="rv-stat-value" style="font-size:0.8rem;">{app.get('applicant_email','—')}</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">Mobile</span><span class="rv-stat-value">{app.get('applicant_phone','—')}</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">City</span><span class="rv-stat-value">{app.get('city','—')}</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">Constitution</span><span class="rv-stat-value">{constitution or '—'}</span></div>
            </div>
            """, unsafe_allow_html=True)

        with r1c2:
            st.markdown(f"""
            <div class="rv-card" style="padding:1rem;">
              <div class="rv-section-title">LOAN DETAILS</div>
              <div class="rv-stat-row"><span class="rv-stat-label">Amount</span><span class="rv-stat-value" style="color:#7B6BF8;">{format_inr(amount)}</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">Purpose</span><span class="rv-stat-value" style="font-size:0.8rem;">{app.get('loan_purpose','—')}</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">Tenure</span><span class="rv-stat-value">{app.get('loan_tenure_months',0)} months</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">Collateral</span><span class="rv-stat-value" style="font-size:0.8rem;">{app.get('collateral_type','—')}</span></div>
              <div class="rv-stat-row"><span class="rv-stat-label">Completion</span><span class="rv-stat-value">{comp}%</span></div>
            </div>
            """, unsafe_allow_html=True)

        with r1c3:
            dscr_color = "#00D48A" if dscr >= 1.25 else "#FF3B57" if dscr > 0 else "#8A8FA8"
            ltv_color = "#00D48A" if 0 < ltv <= 60 else "#FF3B57" if ltv > 60 else "#8A8FA8"
            cibil_color = "#00D48A" if cibil >= 700 else "#F5A623" if cibil >= 650 else "#FF3B57" if cibil > 0 else "#8A8FA8"
            risk_color = "#00D48A" if risk >= 70 else "#F5A623" if risk >= 50 else "#FF3B57" if risk > 0 else "#8A8FA8"
            dscr_str = f"{dscr:.2f}" if dscr else "—"
            ltv_str = f"{ltv:.1f}%" if ltv else "—"
            cibil_str = str(cibil) if cibil else "—"

            st.markdown(f"""
            <div class="rv-card" style="padding:1rem;">
              <div class="rv-section-title">CREDIT METRICS</div>
              <div class="rv-stat-row">
                <span class="rv-stat-label">DSCR</span>
                <span style="font-weight:700;color:{dscr_color};">{dscr_str}</span>
              </div>
              <div class="rv-stat-row">
                <span class="rv-stat-label">LTV</span>
                <span style="font-weight:700;color:{ltv_color};">{ltv_str}</span>
              </div>
              <div class="rv-stat-row">
                <span class="rv-stat-label">CIBIL</span>
                <span style="font-weight:700;color:{cibil_color};">{cibil_str}</span>
              </div>
              <div class="rv-stat-row">
                <span class="rv-stat-label">Risk Score</span>
                <span style="font-weight:700;color:{risk_color};">{f'{risk:.0f}/100' if risk else '—'}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Action Buttons ────────────────────────────────────
        b1, b2, b3, b4 = st.columns(4)

        with b1:
            if app["status"] == "application_submitted":
                if st.button("⚡ Run AI Pipeline", key=f"pipe_{bid}"):
                    with st.spinner("Running pipeline — KYC → Underwriting → CAM..."):
                        try:
                            r = requests.post(f"{API}/api/applications/{bid}/run-pipeline", timeout=90)
                            if r.status_code == 200:
                                st.success("Pipeline complete! Refresh to see updated scores.")
                            else:
                                st.error(f"Pipeline error: {r.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")

        with b2:
            if st.button("📜 Audit Log", key=f"audit_{bid}"):
                r = requests.get(f"{API}/api/dashboard/audit/{bid}")
                if r.status_code == 200:
                    entries = r.json()
                    for e in entries[-5:]:
                        agent_icons = {
                            "kyc": "🛡️", "document": "📄", "underwriting": "📊",
                            "pricing": "💰", "orchestrator": "⚙️", "sarah": "💬",
                        }
                        icon = agent_icons.get(e["agent"], "❓")
                        st.markdown(
                            f'<div style="font-size:0.8rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                            f'{icon} <strong>{e["agent"]}</strong> — {e["action"]}'
                            f'<span style="color:#8A8FA8;margin-left:0.5rem;">{e["created_at"][:19]}</span></div>',
                            unsafe_allow_html=True,
                        )

        with b3:
            if app["status"] in ("pending_bcm", "pending_rch", "pending_cc"):
                if st.button("✅ Approve", key=f"approve_{bid}"):
                    r = requests.post(f"{API}/api/applications/{bid}/approve", json={
                        "approved_by": "Loan Officer",
                        "conditions": ["Collateral registration within 30 days"],
                    })
                    if r.status_code == 200:
                        st.success("Loan Sanctioned!")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")

        with b4:
            if app["status"] in ("pending_bcm", "pending_rch", "pending_cc"):
                if st.button("❌ Decline", key=f"decline_{bid}"):
                    r = requests.post(f"{API}/api/applications/{bid}/decline", json={
                        "declined_by": "Loan Officer",
                        "reason": "Does not meet credit criteria",
                    })
                    if r.status_code == 200:
                        st.error("Application Declined")
                        st.rerun()
