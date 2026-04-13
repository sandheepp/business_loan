"""Approval Workflow — Stages 11-14 of India MSME LOS."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
from styles import format_inr, status_badge


API = st.session_state.get("api_url", "http://localhost:8000")


# ── Header ─────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:800;letter-spacing:-0.03em;color:#FFFFFF;">Approval Workflow</div>
  <div style="font-size:0.85rem;color:#8A8FA8;">Stages 11–14 · BCM / RCH / Credit Committee · Sanction · Legal · Disbursement</div>
</div>
""", unsafe_allow_html=True)

# ── Fetch apps pending approval or in post-approval stages ──────
try:
    all_apps = requests.get(f"{API}/api/applications/", timeout=3).json()
except Exception:
    all_apps = []

APPROVAL_STATUSES = [
    "pending_bcm", "pending_rch", "pending_cc",
    "sanctioned", "sanction_accepted", "legal_docs", "legal_verified",
    "disbursement_pending", "disbursed",
]

apps = [a for a in all_apps if a.get("status") in APPROVAL_STATUSES]
declined = [a for a in all_apps if a.get("status") == "declined"]

# ── Approval Tabs ──────────────────────────────────────────────
tab_pending, tab_sanctioned, tab_disbursed, tab_declined = st.tabs([
    f"⏳ Pending Approval ({len([a for a in apps if a['status'] in ('pending_bcm','pending_rch','pending_cc')])})",
    f"✓ Sanctioned ({len([a for a in apps if a['status'] in ('sanctioned','sanction_accepted','legal_docs','legal_verified','disbursement_pending')])})",
    f"✅ Disbursed ({len([a for a in apps if a['status'] == 'disbursed'])})",
    f"✗ Declined ({len(declined)})",
])

# ── PENDING APPROVAL ───────────────────────────────────────────
with tab_pending:
    pending_apps = [a for a in apps if a.get("status") in ("pending_bcm", "pending_rch", "pending_cc")]
    if not pending_apps:
        st.markdown("""
        <div class="rv-card" style="text-align:center;padding:2.5rem;color:#8A8FA8;">
          <div style="font-size:1.5rem;margin-bottom:0.5rem;">✓</div>
          <div style="font-weight:600;">No applications pending approval</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for app in pending_apps:
            bid = app["id"]
            status = app.get("status", "")
            approval_level = {
                "pending_bcm": ("Branch Credit Manager", "< ₹50 Lakhs", "#3B9EF5"),
                "pending_rch": ("Regional Credit Head", "₹50L – ₹2 Cr", "#F5A623"),
                "pending_cc": ("Credit Committee", "> ₹2 Crore", "#FF3B57"),
            }.get(status, ("Unknown", "", "#8A8FA8"))

            loan_amount = app.get("loan_amount", 0)
            dscr = app.get("dscr", 0)
            ltv = app.get("ltv_ratio", 0)
            cibil = app.get("cibil_score", 0)
            risk = app.get("risk_score", 0)
            risk_rating = app.get("risk_rating", "")
            dscr_str = f"{dscr:.2f}" if dscr else "—"
            ltv_str = f"{ltv:.1f}%" if ltv else "—"
            risk_str = f"{risk:.0f}/100" if risk else "—"
            dscr_col = '#00D48A' if dscr >= 1.25 else '#FF3B57'
            ltv_col = '#00D48A' if 0 < ltv <= 60 else '#FF3B57'
            cibil_col = '#00D48A' if cibil >= 700 else '#F5A623' if cibil >= 650 else '#FF3B57'

            st.markdown(f"""
            <div class="rv-card" style="padding:1.5rem;border-left:3px solid {approval_level[2]};margin-bottom:1rem;">
              <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1rem;">
                <div>
                  <div style="font-size:1rem;font-weight:700;color:#FFFFFF;">{app.get('business_name') or app.get('applicant_name','—')}</div>
                  <div style="font-size:0.8rem;color:#8A8FA8;">{app.get('applicant_email','—')} · {app.get('city','—')}</div>
                  <div style="font-size:0.75rem;font-family:monospace;color:#7B6BF8;margin-top:0.2rem;">{bid}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:1.5rem;font-weight:800;color:#7B6BF8;">{format_inr(loan_amount)}</div>
                  <div style="font-size:0.75rem;color:{approval_level[2]};margin-top:0.2rem;">→ {approval_level[0]}</div>
                  <div style="font-size:0.7rem;color:#8A8FA8;">{approval_level[1]}</div>
                </div>
              </div>
              <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-bottom:1rem;">
                <div><span style="font-size:0.7rem;color:#8A8FA8;">DSCR</span><br>
                  <span style="font-weight:700;color:{dscr_col};">{dscr_str}</span></div>
                <div><span style="font-size:0.7rem;color:#8A8FA8;">LTV</span><br>
                  <span style="font-weight:700;color:{ltv_col};">{ltv_str}</span></div>
                <div><span style="font-size:0.7rem;color:#8A8FA8;">CIBIL</span><br>
                  <span style="font-weight:700;color:{cibil_col};">{cibil or '—'}</span></div>
                <div><span style="font-size:0.7rem;color:#8A8FA8;">Risk</span><br>
                  <span style="font-weight:700;color:#7B6BF8;">{risk_rating or '—'} ({risk_str})</span></div>
                <div><span style="font-size:0.7rem;color:#8A8FA8;">Purpose</span><br>
                  <span style="font-size:0.82rem;color:#C5C8D8;">{app.get('loan_purpose','—')[:30]}</span></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Approval form
            with st.expander(f"📋 Review & Decide — {bid}"):
                col_approve, col_decline = st.columns(2)

                with col_approve:
                    st.markdown('<div class="rv-section-title">APPROVE LOAN</div>', unsafe_allow_html=True)
                    approved_by = st.text_input("Approver Name", key=f"approver_{bid}",
                                                 placeholder="e.g. Priya Mehta — BCM Mumbai")
                    conditions = st.text_area(
                        "Conditions Precedent (one per line)",
                        key=f"conditions_{bid}",
                        placeholder="1. Collateral registration within 30 days\n2. Insurance policy assignment\n3. Guarantor agreement",
                        height=100,
                    )

                    if st.button("✅ Sanction Loan", type="primary", key=f"approve_btn_{bid}", use_container_width=True):
                        if not approved_by:
                            st.error("Enter approver name.")
                        else:
                            cond_list = [c.strip() for c in conditions.split("\n") if c.strip()]
                            r = requests.post(f"{API}/api/applications/{bid}/approve", json={
                                "approved_by": approved_by,
                                "conditions": cond_list,
                            })
                            if r.status_code == 200:
                                st.success("✓ Loan Sanctioned! Sanction letter will be generated.")
                                st.rerun()
                            else:
                                st.error(f"Error: {r.text}")

                with col_decline:
                    st.markdown('<div class="rv-section-title">DECLINE APPLICATION</div>', unsafe_allow_html=True)
                    declined_by = st.text_input("Declined By", key=f"dec_by_{bid}",
                                                 placeholder="Approver name")
                    decline_reason = st.selectbox(
                        "Decline Reason",
                        [
                            "DSCR below minimum threshold",
                            "LTV exceeds 60% limit",
                            "CIBIL score below minimum (650)",
                            "Collateral title defect",
                            "Business vintage insufficient",
                            "High existing debt obligations",
                            "Industry risk — ineligible sector",
                            "Negative net worth",
                            "Other",
                        ],
                        key=f"dec_reason_{bid}",
                    )

                    if st.button("✗ Decline Application", key=f"decline_btn_{bid}", use_container_width=True):
                        r = requests.post(f"{API}/api/applications/{bid}/decline", json={
                            "declined_by": declined_by or "Loan Officer",
                            "reason": decline_reason,
                        })
                        if r.status_code == 200:
                            st.error("Application declined.")
                            st.rerun()
                        else:
                            st.error(f"Error: {r.text}")

# ── SANCTIONED ─────────────────────────────────────────────────
with tab_sanctioned:
    sanc_apps = [a for a in apps if a["status"] in (
        "sanctioned", "sanction_accepted", "legal_docs", "legal_verified", "disbursement_pending"
    )]

    if not sanc_apps:
        st.markdown("""
        <div class="rv-card" style="text-align:center;padding:2.5rem;color:#8A8FA8;">
          <div style="font-size:1.5rem;margin-bottom:0.5rem;">📋</div>
          <div style="font-weight:600;">No sanctioned applications yet</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for app in sanc_apps:
            bid = app["id"]
            status = app.get("status", "")
            loan_amount = app.get("loan_amount", 0)
            sanc_amount = app.get("sanction_amount", loan_amount)
            rate = app.get("sanction_interest_rate", 12.5)
            tenure = app.get("sanction_tenure_months", 60)
            emi = app.get("sanction_emi", 0)

            # Stage progress
            stage_steps = [
                ("Sanctioned", "sanctioned", status == "sanctioned"),
                ("Sanction Accepted", "sanction_accepted", status == "sanction_accepted"),
                ("Legal Docs", "legal_docs", status == "legal_docs"),
                ("Legal Verified", "legal_verified", status == "legal_verified"),
                ("Disbursement Pending", "disbursement_pending", status == "disbursement_pending"),
            ]

            st.markdown(f"""
            <div class="rv-card" style="padding:1.5rem;border-left:3px solid #00D48A;margin-bottom:1rem;">
              <div style="display:flex;justify-content:space-between;margin-bottom:1rem;">
                <div>
                  <div style="font-size:1rem;font-weight:700;color:#FFFFFF;">{app.get('business_name') or app.get('applicant_name','—')}</div>
                  <div style="font-size:0.75rem;font-family:monospace;color:#7B6BF8;">{bid}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:1.5rem;font-weight:800;color:#00D48A;">{format_inr(sanc_amount)}</div>
                  <div style="font-size:0.75rem;color:#8A8FA8;">{rate}% · {tenure}m · EMI {format_inr(emi)}</div>
                </div>
              </div>
              <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
            """, unsafe_allow_html=True)

            for stage_label, stage_val, is_current in stage_steps:
                idx = [s[1] for s in stage_steps].index(stage_val)
                current_idx = [s[1] for s in stage_steps].index(status) if status in [s[1] for s in stage_steps] else -1
                if idx < current_idx:
                    badge_css = "rv-badge-green"
                elif idx == current_idx:
                    badge_css = "rv-badge-accent"
                else:
                    badge_css = "rv-badge-muted"
                st.markdown(f'<span class="rv-badge {badge_css}">{stage_label}</span>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            if status == "disbursement_pending":
                with st.expander(f"💸 Trigger Disbursement — {bid}"):
                    st.markdown("""
                    <div class="rv-card" style="padding:1rem;margin-bottom:1rem;">
                      <div class="rv-section-title">PRE-DISBURSEMENT CHECKLIST</div>
                      <div class="rv-stat-row"><span class="rv-stat-label">KYC Verified</span><span class="rv-badge rv-badge-green">✓</span></div>
                      <div class="rv-stat-row"><span class="rv-stat-label">Collateral Registered</span><span class="rv-badge rv-badge-amber">Pending</span></div>
                      <div class="rv-stat-row"><span class="rv-stat-label">Agreements Signed</span><span class="rv-badge rv-badge-amber">Pending</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                    acc_num = st.text_input("Beneficiary Account Number", key=f"acc_{bid}")
                    ifsc = st.text_input("IFSC Code", key=f"ifsc_{bid}")
                    if st.button("💸 Disburse Loan", type="primary", key=f"disburse_{bid}"):
                        r = requests.post(f"{API}/api/applications/{bid}/disburse", json={
                            "account_number": acc_num,
                            "ifsc_code": ifsc,
                            "amount": sanc_amount,
                        })
                        if r.status_code == 200:
                            st.success(f"✓ Disbursed! Reference: {r.json().get('reference','')}")
                            st.rerun()
                        else:
                            st.error(f"Error: {r.text}")

# ── DISBURSED ─────────────────────────────────────────────────
with tab_disbursed:
    disb_apps = [a for a in apps if a["status"] == "disbursed"]

    if not disb_apps:
        st.markdown("""
        <div class="rv-card" style="text-align:center;padding:2.5rem;color:#8A8FA8;">
          <div style="font-size:1.5rem;margin-bottom:0.5rem;">💸</div>
          <div style="font-weight:600;">No disbursed loans yet</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_disbursed = sum(a.get("disbursed_amount", 0) for a in disb_apps)
        st.markdown(f"""
        <div class="rv-card rv-card-green" style="padding:1.2rem;margin-bottom:1.5rem;">
          <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;">Total Disbursed</div>
          <div style="font-size:2rem;font-weight:800;color:#00D48A;">{format_inr(total_disbursed)}</div>
          <div style="font-size:0.8rem;color:#8A8FA8;">{len(disb_apps)} loan{'s' if len(disb_apps)>1 else ''} disbursed</div>
        </div>
        """, unsafe_allow_html=True)

        for app in disb_apps:
            bid = app["id"]
            st.markdown(f"""
            <div class="rv-card" style="padding:1.2rem;border-left:3px solid #00D48A;margin-bottom:0.8rem;">
              <div style="display:flex;justify-content:space-between;">
                <div>
                  <div style="font-size:0.95rem;font-weight:700;color:#FFFFFF;">{app.get('business_name') or app.get('applicant_name','—')}</div>
                  <div style="font-size:0.75rem;font-family:monospace;color:#7B6BF8;">{bid}</div>
                  <div style="font-size:0.78rem;color:#8A8FA8;margin-top:0.2rem;">
                    Ref: {app.get('disbursement_reference','—')} · {app.get('disbursed_at','—')[:10] if app.get('disbursed_at') else '—'}
                  </div>
                </div>
                <div style="text-align:right;">
                  <span class="rv-badge rv-badge-green">Disbursed</span>
                  <div style="font-size:1.3rem;font-weight:800;color:#00D48A;margin-top:0.3rem;">{format_inr(app.get('disbursed_amount',0))}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── DECLINED ───────────────────────────────────────────────────
with tab_declined:
    if not declined:
        st.markdown("""
        <div class="rv-card" style="text-align:center;padding:2.5rem;color:#8A8FA8;">
          <div style="font-size:1.5rem;margin-bottom:0.5rem;">✗</div>
          <div style="font-weight:600;">No declined applications</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for app in declined:
            bid = app["id"]
            st.markdown(f"""
            <div class="rv-card" style="padding:1.2rem;border-left:3px solid #FF3B57;margin-bottom:0.8rem;opacity:0.8;">
              <div style="display:flex;justify-content:space-between;">
                <div>
                  <div style="font-size:0.95rem;font-weight:700;color:#FFFFFF;">{app.get('business_name') or app.get('applicant_name','—')}</div>
                  <div style="font-size:0.75rem;font-family:monospace;color:#7B6BF8;">{bid}</div>
                </div>
                <div style="text-align:right;">
                  <span class="rv-badge rv-badge-red">Declined</span>
                  <div style="font-size:1.1rem;font-weight:700;color:#FF3B57;margin-top:0.3rem;">{format_inr(app.get('loan_amount',0))}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
