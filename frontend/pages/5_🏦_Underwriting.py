"""Credit Underwriting & CAM Dashboard — Stages 7-10 of India MSME LOS."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
from styles import page_config_dark, sidebar_status, format_inr, status_badge

page_config_dark("Underwriting", "🏦")

API = st.session_state.get("api_url", "http://localhost:8000")

st.sidebar.markdown("""
<div style="padding:0.5rem 0 1rem;">
  <div style="font-size:1.3rem;font-weight:800;color:#FFFFFF;">Underwriting</div>
  <div style="font-size:0.75rem;color:#8A8FA8;">Credit Analysis & CAM</div>
</div>
""", unsafe_allow_html=True)
sidebar_status()

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:800;letter-spacing:-0.03em;color:#FFFFFF;">Credit Underwriting</div>
  <div style="font-size:0.85rem;color:#8A8FA8;">Stages 7–10 · Financial Analysis · Collateral Assessment · Risk Scoring · CAM</div>
</div>
""", unsafe_allow_html=True)

# ── Application selector ──────────────────────────────────────
try:
    apps = requests.get(f"{API}/api/applications/", timeout=3).json()
    eligible = [a for a in apps if a.get("status") not in ("lead_created", "application_draft", "declined", "withdrawn")]
except Exception:
    eligible = []

if not eligible:
    st.markdown("""
    <div class="rv-card" style="text-align:center;padding:3rem;color:#8A8FA8;">
      <div style="font-size:2rem;margin-bottom:0.8rem;">🏦</div>
      <div style="font-weight:600;">No applications in underwriting pipeline</div>
      <div style="font-size:0.85rem;margin-top:0.3rem;">Submit an application and run the AI pipeline to see underwriting results here.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

options = {
    f"{a['id']} — {a.get('business_name') or a.get('applicant_name','—')} — {format_inr(a['loan_amount'])}": a["id"]
    for a in eligible
}
selected_label = st.selectbox("Select Application", list(options.keys()), label_visibility="collapsed")
app_id = options[selected_label]

try:
    app = requests.get(f"{API}/api/applications/{app_id}", timeout=3).json()
except Exception:
    st.error("Cannot fetch application.")
    st.stop()

# ── Status Banner ─────────────────────────────────────────────
st.markdown(
    f'<div style="margin-bottom:1rem;">{status_badge(app.get("status",""))}</div>',
    unsafe_allow_html=True
)

# ── Key Credit Metrics ─────────────────────────────────────────
dscr = app.get("dscr", 0)
ltv = app.get("ltv_ratio", 0)
cibil = app.get("cibil_score", 0)
risk = app.get("risk_score", 0)
constitution = app.get("business_constitution", "—")
loan_amount = app.get("loan_amount", 0)
col_val = app.get("collateral_estimated_value", 0)

dscr_color = "#00D48A" if dscr >= 1.25 else "#FF3B57" if dscr > 0 else "#8A8FA8"
dscr_status = "✓ Above Minimum (1.25)" if dscr >= 1.25 else "✗ Below Minimum" if dscr > 0 else "—"
ltv_color = "#00D48A" if 0 < ltv <= 60 else "#F5A623" if ltv <= 70 else "#FF3B57" if ltv > 0 else "#8A8FA8"
ltv_status = "✓ Within 60% Limit" if 0 < ltv <= 60 else "⚠ Above 60%" if ltv > 0 else "—"
cibil_color = "#00D48A" if cibil >= 700 else "#F5A623" if cibil >= 650 else "#FF3B57" if cibil > 0 else "#8A8FA8"
cibil_status = "Good" if cibil >= 750 else "Fair" if cibil >= 650 else "Poor" if cibil > 0 else "—"

st.markdown('<div class="rv-section-title">CREDIT SCORECARD</div>', unsafe_allow_html=True)

mc1, mc2, mc3, mc4 = st.columns(4)

for col, val, label, sub, color in [
    (mc1, f"{dscr:.2f}" if dscr else "—", "DSCR", dscr_status, dscr_color),
    (mc2, f"{ltv:.1f}%" if ltv else "—", "LTV Ratio", ltv_status, ltv_color),
    (mc3, str(cibil) if cibil else "—", "CIBIL Score", cibil_status, cibil_color),
    (mc4, f"{risk:.0f}/100" if risk else "—", "Risk Score", app.get("risk_rating") or "—", "#7B6BF8"),
]:
    with col:
        st.markdown(f"""
        <div class="rv-card" style="padding:1.2rem;text-align:center;">
          <div style="font-size:2rem;font-weight:800;color:{color};letter-spacing:-0.04em;">{val}</div>
          <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;margin-top:0.3rem;">{label}</div>
          <div style="font-size:0.75rem;color:{color};margin-top:0.3rem;">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Financial Analysis ─────────────────────────────────────────
col_fin, col_col = st.columns(2)

with col_fin:
    st.markdown('<div class="rv-section-title">FINANCIAL ANALYSIS (STAGE 7)</div>', unsafe_allow_html=True)
    cashflow = app.get("avg_monthly_cashflow", 0)
    revenue = app.get("annual_revenue_reported", app.get("business_annual_revenue", 0))
    net_profit = app.get("net_profit", 0)
    existing_emi = app.get("existing_emi_obligations", 0)
    de_ratio = app.get("debt_equity_ratio", 0)
    rev_growth = app.get("revenue_growth_pct", 0)
    op_margin = app.get("operating_margin_pct", 0)

    st.markdown(f"""
    <div class="rv-card" style="padding:1.2rem;">
      <div class="rv-stat-row">
        <span class="rv-stat-label">Annual Revenue</span>
        <span class="rv-stat-value">{format_inr(revenue)}</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Net Profit</span>
        <span class="rv-stat-value" style="color:#00D48A;">{format_inr(net_profit)}</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Avg Monthly Cashflow</span>
        <span class="rv-stat-value">{format_inr(cashflow)}</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Existing EMI Obligations</span>
        <span class="rv-stat-value">{format_inr(existing_emi)}/mo</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Debt / Equity</span>
        <span style="font-weight:700;color:{'#00D48A' if de_ratio < 2 else '#F5A623' if de_ratio < 3 else '#FF3B57'};">{de_ratio:.2f}x</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Revenue Growth (YoY)</span>
        <span style="font-weight:700;color:{'#00D48A' if rev_growth > 0 else '#FF3B57'};">{rev_growth:+.1f}%</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Operating Margin</span>
        <span style="font-weight:700;color:#3B9EF5;">{op_margin:.1f}%</span>
      </div>
    </div>

    <div style="margin-top:0.8rem;">
      <div style="font-size:0.75rem;color:#8A8FA8;margin-bottom:0.3rem;">DSCR Breakdown</div>
      <div style="background:#1A1E35;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:0.8rem 1rem;">
        <div style="font-size:0.8rem;color:#8A8FA8;">Monthly Cashflow ÷ (Existing EMI + Proposed EMI)</div>
        <div style="font-size:1rem;font-weight:700;color:{dscr_color};margin-top:0.4rem;">
          {format_inr(cashflow)} ÷ ({format_inr(existing_emi)} + proposed) = {dscr:.2f}
        </div>
        <div style="font-size:0.75rem;color:#8A8FA8;margin-top:0.2rem;">RBI MSME guideline: DSCR ≥ 1.25</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_col:
    st.markdown('<div class="rv-section-title">COLLATERAL ASSESSMENT (STAGE 8)</div>', unsafe_allow_html=True)
    col_type = app.get("collateral_type", "—")
    col_est = app.get("collateral_estimated_value", 0)
    col_market = app.get("collateral_market_value", col_est)
    col_distress = col_market * 0.7 if col_market else 0
    max_loan = col_market * 0.6 if col_market else 0
    legal_status = app.get("collateral_legal_status", "pending")
    encumbrance = app.get("encumbrance_status", "pending")

    legal_color = {"clear": "#00D48A", "encumbered": "#FF3B57", "pending": "#F5A623"}.get(legal_status, "#8A8FA8")
    enc_color = {"pending": "#F5A623", "clear": "#00D48A", "encumbered": "#FF3B57"}.get(encumbrance, "#8A8FA8")

    st.markdown(f"""
    <div class="rv-card" style="padding:1.2rem;">
      <div class="rv-stat-row"><span class="rv-stat-label">Property Type</span><span class="rv-stat-value" style="font-size:0.85rem;">{col_type}</span></div>
      <div class="rv-stat-row"><span class="rv-stat-label">Borrower Estimate</span><span class="rv-stat-value">{format_inr(col_est)}</span></div>
      <div class="rv-stat-row"><span class="rv-stat-label">Valuer Assessment</span><span class="rv-stat-value">{format_inr(col_market) if col_market else '—'}</span></div>
      <div class="rv-stat-row"><span class="rv-stat-label">Distress Value (70%)</span><span class="rv-stat-value">{format_inr(col_distress) if col_distress else '—'}</span></div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Max Eligible Loan (60%)</span>
        <span style="font-weight:700;color:#00D48A;">{format_inr(max_loan) if max_loan else '—'}</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">LTV Ratio</span>
        <span style="font-weight:700;color:{ltv_color};">{f'{ltv:.1f}%' if ltv else '—'}</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Legal Title Status</span>
        <span style="font-weight:700;color:{legal_color};">{legal_status.title()}</span>
      </div>
      <div class="rv-stat-row">
        <span class="rv-stat-label">Encumbrance Check</span>
        <span style="font-weight:700;color:{enc_color};">{encumbrance.title()}</span>
      </div>
    </div>

    <div style="margin-top:0.8rem;">
      <div style="font-size:0.75rem;color:#8A8FA8;margin-bottom:0.3rem;">LTV GAUGE</div>
      <div style="background:#1A1E35;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:0.8rem 1rem;">
        <div style="background:#0C0F1E;border-radius:6px;height:10px;overflow:hidden;">
          <div style="height:100%;width:{min(ltv, 100):.0f}%;background:{ltv_color};border-radius:6px;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:0.4rem;">
          <span style="font-size:0.72rem;color:#8A8FA8;">0%</span>
          <span style="font-size:0.72rem;color:#F5A623;">60% limit</span>
          <span style="font-size:0.72rem;color:#8A8FA8;">100%</span>
        </div>
        <div style="font-size:0.8rem;color:{ltv_color};margin-top:0.3rem;font-weight:600;">
          Current LTV: {f'{ltv:.1f}%' if ltv else 'Not calculated'}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Credit Memo (CAM) ──────────────────────────────────────────
st.markdown('<div class="rv-section-title">CREDIT APPRAISAL MEMORANDUM — CAM (STAGE 10)</div>', unsafe_allow_html=True)

cam = app.get("cam_draft") or app.get("underwriting_memo") or ""
analyst_notes = app.get("cam_analyst_notes", "")

if cam:
    col_cam, col_notes = st.columns([3, 1])
    with col_cam:
        import html as _html
        import re as _re

        def _md_to_html(text: str) -> str:
            """Minimal markdown → HTML for CAM display."""
            lines = text.split("\n")
            out = []
            for line in lines:
                # Headers
                if line.startswith("### "):
                    out.append(f'<h3 style="font-size:0.95rem;color:#A09BFF;font-weight:700;margin:1rem 0 0.3rem;">{_html.escape(line[4:])}</h3>')
                elif line.startswith("## "):
                    out.append(f'<h2 style="font-size:1.05rem;color:#FFFFFF;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:0.3rem;margin:1.2rem 0 0.4rem;">{_html.escape(line[3:])}</h2>')
                elif line.startswith("# "):
                    out.append(f'<h1 style="font-size:1.15rem;color:#FFFFFF;font-weight:800;margin:0.5rem 0 0.8rem;">{_html.escape(line[2:])}</h1>')
                elif line.startswith("---") and line.strip("- ") == "":
                    out.append('<hr style="border-color:rgba(255,255,255,0.08);margin:0.8rem 0;">')
                elif line.startswith("- ") or line.startswith("* "):
                    item = _re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#FFFFFF;">\1</strong>',
                             _re.sub(r'\*(.+?)\*', r'<em style="color:#C5C8D8;font-style:normal;">\1</em>',
                             _html.escape(line[2:])))
                    out.append(f'<li style="color:#C5C8D8;font-size:0.87rem;line-height:1.7;margin-bottom:0.2rem;">{item}</li>')
                elif line.strip() == "":
                    out.append('<br>')
                else:
                    p = _re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#FFFFFF;">\1</strong>',
                        _re.sub(r'\*(.+?)\*', r'<em style="color:#C5C8D8;font-style:normal;">\1</em>',
                        _html.escape(line)))
                    out.append(f'<p style="color:#C5C8D8;font-size:0.87rem;line-height:1.75;margin:0 0 0.5rem;">{p}</p>')
            return "\n".join(out)

        cam_html = _md_to_html(cam)
        st.markdown(f"""
        <div style="background:#1A1E35;border:1px solid rgba(255,255,255,0.07);
                    border-radius:14px;padding:1.5rem 1.8rem;max-height:520px;overflow-y:auto;">
          {cam_html}
        </div>
        """, unsafe_allow_html=True)

    with col_notes:
        st.markdown("""
        <div class="rv-card" style="padding:1.2rem;">
          <div class="rv-section-title">ANALYST NOTES</div>
        </div>
        """, unsafe_allow_html=True)
        notes = st.text_area(
            "Add notes", value=analyst_notes,
            placeholder="Analyst observations, qualitative factors, override reasons...",
            height=200,
            label_visibility="collapsed",
        )
        if st.button("Save Notes", use_container_width=True):
            try:
                requests.patch(f"{API}/api/applications/{app_id}", json={
                    "cam_analyst_notes": notes
                })
                st.success("Notes saved.")
            except Exception:
                st.error("Cannot save.")

        st.markdown("""
        <div style="margin-top:1rem;">
          <div class="rv-section-title">RECOMMENDATION</div>
        </div>
        """, unsafe_allow_html=True)

        dscr_ok = dscr >= 1.25
        ltv_ok = ltv <= 60
        cibil_ok = cibil >= 650

        if dscr_ok and ltv_ok and cibil_ok:
            rec_color, rec_text, rec_detail = "#00D48A", "APPROVE", "All criteria met"
        elif not cibil_ok or (dscr > 0 and dscr < 1.0):
            rec_color, rec_text, rec_detail = "#FF3B57", "DECLINE", "Critical criterion failed"
        else:
            rec_color, rec_text, rec_detail = "#F5A623", "REVIEW", "Manual review needed"

        _rgba = {"#00D48A": "0,212,138", "#FF3B57": "255,59,87", "#F5A623": "245,166,35"}.get(rec_color, "128,128,128")
        st.markdown(f"""
        <div style="background:rgba({_rgba},0.1);
                    border:1px solid {rec_color}44;border-radius:10px;padding:0.8rem 1rem;margin-top:0.5rem;text-align:center;">
          <div style="font-size:1.2rem;font-weight:800;color:{rec_color};">{rec_text}</div>
          <div style="font-size:0.75rem;color:{rec_color};margin-top:0.2rem;">{rec_detail}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="rv-card" style="text-align:center;padding:2.5rem;color:#8A8FA8;">
      <div style="font-size:1.8rem;margin-bottom:0.5rem;">📋</div>
      <div style="font-weight:600;">CAM not generated yet</div>
      <div style="font-size:0.85rem;margin-top:0.3rem;">Run the AI pipeline from the Dashboard to generate the Credit Appraisal Memorandum.</div>
    </div>
    """, unsafe_allow_html=True)

# ── Trigger pipeline if not run ─────────────────────────────────
if not cam and app.get("status") == "application_submitted":
    st.markdown("---")
    if st.button("⚡ Run Full AI Pipeline Now", type="primary"):
        with st.spinner("Running KYC → Underwriting → CAM generation..."):
            try:
                r = requests.post(f"{API}/api/applications/{app_id}/run-pipeline", timeout=90)
                if r.status_code == 200:
                    st.success("Pipeline complete! Refresh the page to view results.")
                    st.rerun()
                else:
                    st.error(f"Pipeline error: {r.text}")
            except Exception as e:
                st.error(f"Error: {e}")
