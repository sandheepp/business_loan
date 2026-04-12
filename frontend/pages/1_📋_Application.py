"""MSME Secured Loan Application — Stages 1–4 of India LOS."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
from styles import page_config_dark, sidebar_status, format_inr, status_badge

page_config_dark("Application", "📋")

API = st.session_state.get("api_url", "http://localhost:8000")

# ── Session State ─────────────────────────────────────────────
for key, default in [
    ("app_id", None), ("step", 1), ("completed_steps", set())
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar Summary ───────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:0.5rem 0 1rem;">
  <div style="font-size:1.3rem;font-weight:800;color:#FFFFFF;">Application</div>
  <div style="font-size:0.75rem;color:#8A8FA8;">MSME Secured Loan</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.app_id:
    st.sidebar.markdown(f"""
    <div style="background:#1A1E35;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:1rem;margin-bottom:1rem;">
      <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.3rem;">Application ID</div>
      <div style="font-size:0.9rem;font-weight:700;font-family:monospace;color:#7B6BF8;">{st.session_state.app_id}</div>
    </div>
    """, unsafe_allow_html=True)
    pct = min(st.session_state.step / 5, 1.0)
    st.sidebar.progress(pct, f"Step {st.session_state.step} of 5")

sidebar_status()

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="rv-hero" style="padding:2rem 2.5rem;">
  <div style="font-size:2rem;font-weight:800;letter-spacing:-0.03em;
              background:linear-gradient(135deg,#FFFFFF,#A09BFF);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    MSME Loan Application
  </div>
  <div style="font-size:0.95rem;color:#8A8FA8;margin-top:0.4rem;">
    Secured Business Loan · Powered by AI · RBI Compliant
  </div>
</div>
""", unsafe_allow_html=True)

# ── Progress Steps ────────────────────────────────────────────
steps_info = [
    ("01", "Lead Info"),
    ("02", "Promoter"),
    ("03", "Business"),
    ("04", "Loan & Collateral"),
    ("05", "Documents"),
]
cols = st.columns(5)
for i, (num, label) in enumerate(steps_info, 1):
    with cols[i - 1]:
        if i < st.session_state.step:
            css = "rv-step-done"
            icon = "✓"
        elif i == st.session_state.step:
            css = "rv-step-active"
            icon = "●"
        else:
            css = "rv-step-pending"
            icon = num
        st.markdown(
            f'<div class="rv-step-pill {css}" style="width:100%;justify-content:center;">'
            f'{icon} {label}</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP 1 — Lead Information (Stage 1: Lead Creation)
# ─────────────────────────────────────────────────────────────
if st.session_state.step == 1:
    st.markdown("""
    <div class="rv-form-section">
      <div class="rv-form-section-title">👤 Step 1 — Lead Information</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("step1_form"):
        st.markdown('<div class="rv-form-section-title">Contact Details</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="Rajesh Kumar")
            email = st.text_input("Email Address", placeholder="rajesh@business.com")
        with col2:
            phone = st.text_input("Mobile Number", placeholder="+91 98765 43210")
            city = st.text_input("City", placeholder="Mumbai")

        col3, col4 = st.columns(2)
        with col3:
            biz_name = st.text_input("Business Name", placeholder="Kumar Enterprises Pvt Ltd")
        with col4:
            loan_req = st.number_input(
                "Loan Requirement (₹)", min_value=100000, max_value=100_000_000,
                value=5_000_000, step=100_000,
                help="Amount required (₹1L to ₹10 Cr for MSME Secured)"
            )

        submitted = st.form_submit_button("Continue →", type="primary", use_container_width=False)

    if submitted:
        if not name.strip() or not email.strip():
            st.error("Please enter your name and email to continue.")
        else:
            try:
                r = requests.post(f"{API}/api/applications/", json={
                    "applicant_name": name.strip(),
                    "applicant_email": email.strip(),
                    "applicant_phone": phone.strip(),
                    "city": city.strip(),
                    "business_name": biz_name.strip(),
                    "loan_amount": loan_req,
                    "lead_source": "web",
                })
                if r.status_code == 200:
                    data = r.json()
                    st.session_state.app_id = data["id"]
                    st.session_state.step = 2
                    st.session_state.completed_steps.add(1)
                    st.rerun()
                else:
                    st.error(f"Error: {r.text}")
            except Exception:
                st.error("Cannot connect to backend. Is the API running?")

# ─────────────────────────────────────────────────────────────
# STEP 2 — Promoter / KYC Details (Stage 2: Borrower Application)
# ─────────────────────────────────────────────────────────────
elif st.session_state.step == 2 and st.session_state.app_id:
    st.markdown("""
    <div class="rv-card rv-card-accent">
      <div class="rv-form-section-title" style="margin-bottom:0.3rem;">🪪 Step 2 — Promoter & KYC Details</div>
      <div style="font-size:0.82rem;color:#8A8FA8;">Identity information for PAN validation, Aadhaar verification, and CKYC lookup.</div>
    </div>
    """, unsafe_allow_html=True)

    import re

    with st.form("step2_form"):
        st.markdown('<div class="rv-form-section-title">🪪 Promoter Identity</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            pan = st.text_input(
                "PAN Card Number", placeholder="ABCDE1234F",
                help="10-character PAN (5 letters + 4 digits + 1 letter)"
            )
            aadhaar = st.text_input(
                "Aadhaar Number", placeholder="1234 5678 9012",
                help="12-digit Aadhaar (last 8 digits will be masked)"
            )
        with col2:
            dob = st.text_input("Date of Birth", placeholder="DD/MM/YYYY")
            shareholding = st.slider(
                "Shareholding %", 1, 100, 100,
                help="Promoter's ownership percentage in the business"
            )

        address = st.text_area(
            "Residential Address", placeholder="House No., Street, Area, City, State, PIN",
            height=80
        )

        col_next, col_back = st.columns([1, 4])
        with col_next:
            s2_submitted = st.form_submit_button("Continue →", type="primary", use_container_width=True)
        with col_back:
            s2_back = st.form_submit_button("← Back", use_container_width=False)

    # PAN format hint (outside form, purely cosmetic)
    if pan:
        valid_pan = bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan.upper()))
        if valid_pan:
            st.markdown('<div style="color:#00D48A;font-size:0.8rem;">✓ Valid PAN format</div>', unsafe_allow_html=True)
        elif len(pan) >= 10:
            st.markdown('<div style="color:#FF3B57;font-size:0.8rem;">✗ Invalid PAN format (expected: ABCDE1234F)</div>', unsafe_allow_html=True)

    if s2_back:
        st.session_state.step = 1
        st.rerun()

    if s2_submitted:
        if not pan.strip() or not aadhaar.strip():
            st.error("PAN and Aadhaar are required.")
        else:
            try:
                requests.patch(f"{API}/api/applications/{st.session_state.app_id}", json={
                    "promoter_pan": pan.upper().strip(),
                    "promoter_aadhaar": aadhaar.replace(" ", ""),
                    "promoter_dob": dob.strip(),
                    "promoter_address": address.strip(),
                    "shareholding_pct": shareholding,
                    "current_step": 3,
                })
                st.session_state.step = 3
                st.session_state.completed_steps.add(2)
                st.rerun()
            except Exception:
                st.error("Cannot save. Is the API running?")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Business Details (Stage 2: Borrower Application)
# ─────────────────────────────────────────────────────────────
elif st.session_state.step == 3 and st.session_state.app_id:
    st.markdown("""
    <div class="rv-card rv-card-accent">
      <div class="rv-form-section-title" style="margin-bottom:0.3rem;">🏢 Step 3 — Business Details</div>
      <div style="font-size:0.82rem;color:#8A8FA8;">Business registration, GST, and financial overview for MSME classification.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("step3_form"):
        st.markdown('<div class="rv-form-section-title">🏢 Business Registration</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            biz_name = st.text_input("Business Legal Name", placeholder="Kumar Enterprises Pvt Ltd")
            constitution = st.selectbox(
                "Business Constitution",
                ["Proprietorship", "Partnership", "LLP", "Pvt Ltd", "One Person Company"],
                help="Legal structure of the business entity"
            )
            gst = st.text_input(
                "GSTIN Number", placeholder="27ABCDE1234F1Z5",
                help="15-character GST Identification Number"
            )
        with col2:
            industry = st.selectbox(
                "Industry Type",
                [
                    "Manufacturing — Food & Beverages",
                    "Manufacturing — Textiles & Apparel",
                    "Manufacturing — Chemicals & Pharma",
                    "Manufacturing — Metal & Engineering",
                    "Manufacturing — Electronics",
                    "Trading — Wholesale",
                    "Trading — Retail",
                    "Services — IT & Technology",
                    "Services — Healthcare",
                    "Services — Hospitality & Tourism",
                    "Services — Education",
                    "Services — Logistics & Transport",
                    "Agriculture & Allied",
                    "Construction & Real Estate",
                    "Other",
                ],
            )
            nic_code = st.text_input("NIC Code", placeholder="10109",
                                     help="National Industry Classification code")
            biz_state = st.selectbox(
                "State of Registration",
                ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Gujarat", "Telangana",
                 "Rajasthan", "West Bengal", "Uttar Pradesh", "Kerala", "Punjab",
                 "Andhra Pradesh", "Madhya Pradesh", "Haryana", "Odisha", "Other"],
            )

        biz_address = st.text_area(
            "Registered Business Address", placeholder="Registered Office Address", height=60
        )

        col3, col4 = st.columns(2)
        with col3:
            years = st.number_input("Years in Operation", min_value=0, max_value=100, value=3)
            employees = st.number_input("Number of Employees", min_value=0, value=25)
        with col4:
            revenue = st.number_input(
                "Annual Turnover (₹)", min_value=0, value=10_000_000, step=500_000,
                help="Last financial year turnover. MSME limit: ₹25 Cr"
            )

        col_next, col_back = st.columns([1, 4])
        with col_next:
            s3_submitted = st.form_submit_button("Continue →", type="primary", use_container_width=True)
        with col_back:
            s3_back = st.form_submit_button("← Back", use_container_width=False)

    if s3_back:
        st.session_state.step = 2
        st.rerun()

    if s3_submitted:
        if not biz_name.strip() or not gst.strip():
            st.error("Business name and GSTIN are required.")
        else:
            try:
                requests.patch(f"{API}/api/applications/{st.session_state.app_id}", json={
                    "business_name": biz_name.strip(),
                    "business_constitution": constitution,
                    "business_gst": gst.upper().strip(),
                    "business_address": biz_address.strip(),
                    "industry_type": industry,
                    "business_nic_code": nic_code.strip(),
                    "business_state": biz_state,
                    "business_years_in_operation": int(years),
                    "business_employees": int(employees),
                    "business_annual_revenue": float(revenue),
                    "current_step": 4,
                })
                st.session_state.step = 4
                st.session_state.completed_steps.add(3)
                st.rerun()
            except Exception:
                st.error("Cannot save. Is the API running?")

# ─────────────────────────────────────────────────────────────
# STEP 4 — Loan & Collateral Details (Stage 2: Borrower Application)
# ─────────────────────────────────────────────────────────────
elif st.session_state.step == 4 and st.session_state.app_id:
    st.markdown("""
    <div class="rv-card rv-card-accent">
      <div class="rv-form-section-title" style="margin-bottom:0.3rem;">💰 Step 4 — Loan & Collateral Details</div>
      <div style="font-size:0.82rem;color:#8A8FA8;">Loan parameters and collateral declaration for LTV calculation.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("step4_form"):
        col_loan, col_collateral = st.columns(2)

        with col_loan:
            st.markdown('<div class="rv-form-section-title">💰 Loan Details</div>', unsafe_allow_html=True)

            loan_amount = st.number_input(
                "Loan Amount Required (₹)",
                min_value=100_000, max_value=100_000_000,
                value=5_000_000, step=100_000,
            )
            loan_purpose = st.selectbox(
                "Loan Purpose",
                [
                    "Working Capital Enhancement",
                    "Machinery & Equipment Purchase",
                    "Business Expansion / New Unit",
                    "Commercial Property Purchase",
                    "Trade Finance",
                    "Debt Consolidation",
                    "Technology Upgrade",
                    "Other",
                ],
            )
            tenure = st.select_slider(
                "Preferred Tenure",
                options=[12, 24, 36, 48, 60, 84, 120, 180],
                value=60,
                format_func=lambda x: f"{x} months ({x//12} yr{'s' if x//12 > 1 else ''})",
            )

        with col_collateral:
            st.markdown('<div class="rv-form-section-title">🏠 Collateral Details</div>', unsafe_allow_html=True)

            col_type = st.selectbox(
                "Property Type",
                ["Residential — Apartment / Flat", "Residential — Independent House",
                 "Residential — Plot", "Commercial — Office Space",
                 "Commercial — Shop / Showroom", "Industrial — Factory / Warehouse",
                 "Agricultural Land"],
            )
            col_value = st.number_input(
                "Estimated Property Value (₹)",
                min_value=100_000, max_value=500_000_000,
                value=10_000_000, step=500_000,
            )
            col_owner = st.text_input("Property Owner Name", placeholder="Rajesh Kumar")
            col_ownership = st.selectbox(
                "Ownership Type",
                ["Self-Owned", "Jointly Owned (Spouse)", "Jointly Owned (Family)", "Third-Party"],
            )
            col_address = st.text_area(
                "Property Address", placeholder="Survey No., Street, Locality, City, State, PIN",
                height=80
            )

        col_next, col_back = st.columns([1, 4])
        with col_next:
            s4_submitted = st.form_submit_button("Continue →", type="primary", use_container_width=True)
        with col_back:
            s4_back = st.form_submit_button("← Back", use_container_width=False)

    # Live previews (outside form, use session state values after submit)
    _loan_amt = st.session_state.get("FormSubmitter:step4_form-Continue →") and loan_amount or loan_amount
    r_rate = 12.5 / 100 / 12
    n = tenure
    emi = loan_amount * r_rate * ((1 + r_rate) ** n) / (((1 + r_rate) ** n) - 1)
    ltv = (loan_amount / col_value * 100) if col_value > 0 else 0
    ltv_color = "#00D48A" if ltv <= 60 else "#F5A623" if ltv <= 70 else "#FF3B57"
    ltv_msg = "Within limit" if ltv <= 60 else "Exceeds 60% limit"
    st.markdown(f"""
    <div style="display:flex;gap:1rem;margin-top:0.5rem;">
      <div style="flex:1;background:rgba(91,76,245,0.1);border:1px solid rgba(91,76,245,0.25);
                  border-radius:10px;padding:0.8rem 1rem;">
        <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;">Indicative EMI @ 12.5% p.a.</div>
        <div style="font-size:1.3rem;font-weight:800;color:#7B6BF8;">{format_inr(emi)}<span style="font-size:0.8rem;font-weight:400;color:#8A8FA8;">/mo</span></div>
      </div>
      <div style="flex:1;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);
                  border-radius:10px;padding:0.8rem 1rem;">
        <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;">Indicative LTV</div>
        <div style="font-size:1.3rem;font-weight:800;color:{ltv_color};">{ltv:.1f}% <span style="font-size:0.75rem;font-weight:400;">{ltv_msg}</span></div>
        <div style="font-size:0.75rem;color:#8A8FA8;">Max eligible: {format_inr(col_value * 0.6)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if s4_back:
        st.session_state.step = 3
        st.rerun()

    if s4_submitted:
        try:
            requests.patch(f"{API}/api/applications/{st.session_state.app_id}", json={
                "loan_amount": float(loan_amount),
                "loan_purpose": loan_purpose,
                "loan_tenure_months": int(tenure),
                "collateral_type": col_type,
                "collateral_estimated_value": float(col_value),
                "collateral_owner_name": col_owner.strip(),
                "collateral_ownership_type": col_ownership,
                "collateral_address": col_address.strip(),
                "current_step": 5,
            })
            st.session_state.step = 5
            st.session_state.completed_steps.add(4)
            st.rerun()
        except Exception:
            st.error("Cannot save. Is the API running?")

# ─────────────────────────────────────────────────────────────
# STEP 5 — Document Upload (Stage 4: Document Collection)
# ─────────────────────────────────────────────────────────────
elif st.session_state.step == 5 and st.session_state.app_id:
    doc_categories = [
        ("🪪", "Identity",   "identity_documents",  ["PAN Card", "Aadhaar Card"]),
        ("🏢", "Business",   "business_documents",  ["GST Certificate", "Incorporation Certificate", "Partnership Deed", "Board Resolution"]),
        ("💼", "Financial",  "financial_documents", ["ITR — Last 2-3 Years", "Balance Sheet & P&L", "Bank Statements — 12 Months", "CA Certified Financials"]),
        ("🏠", "Collateral", "collateral_documents",["Sale Deed / Title Document", "Property Tax Receipts", "Encumbrance Certificate", "Approved Building Plan"]),
    ]

    # ── Overview cards ────────────────────────────────────────
    # Gradient palettes per category: (from_color, to_color, border_color, icon_bg)
    cat_gradients = [
        ("rgba(91,76,245,0.25)",  "rgba(91,76,245,0.05)",  "rgba(91,76,245,0.4)",  "#5B4CF5"),   # Identity — purple
        ("rgba(0,180,255,0.2)",   "rgba(0,180,255,0.03)",  "rgba(0,180,255,0.35)", "#00B4FF"),   # Business — blue
        ("rgba(0,212,138,0.2)",   "rgba(0,212,138,0.03)",  "rgba(0,212,138,0.35)", "#00D48A"),   # Financial — green
        ("rgba(245,166,35,0.2)",  "rgba(245,166,35,0.03)", "rgba(245,166,35,0.35)","#F5A623"),   # Collateral — amber
    ]

    overview_cols = st.columns(4)
    for i, (icon, label, key, docs) in enumerate(doc_categories):
        uploaded_count = len(st.session_state.get(f"upload_{key}", []) or [])
        done = uploaded_count >= 1
        g_from, g_to, g_border, g_accent = cat_gradients[i]
        if done:
            bg = "linear-gradient(135deg, rgba(0,212,138,0.18), rgba(0,212,138,0.04))"
            border = "rgba(0,212,138,0.4)"
            accent = "#00D48A"
            status_text = f"✓ {uploaded_count} file{'s' if uploaded_count != 1 else ''}"
        else:
            bg = f"linear-gradient(135deg, {g_from}, {g_to})"
            border = g_border
            accent = g_accent
            status_text = f"{len(docs)} required"

        with overview_cols[i]:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};
                        border-radius:14px;padding:1.1rem 1rem;text-align:center;margin-bottom:1rem;
                        box-shadow:0 4px 20px rgba(0,0,0,0.2);">
              <div style="width:42px;height:42px;border-radius:50%;margin:0 auto 0.5rem;
                          background:linear-gradient(135deg,{accent}33,{accent}11);
                          border:1px solid {accent}55;display:flex;align-items:center;
                          justify-content:center;font-size:1.2rem;">{icon}</div>
              <div style="font-size:0.88rem;font-weight:700;color:#FFFFFF;">{label}</div>
              <div style="font-size:0.72rem;color:{accent};margin-top:0.25rem;font-weight:600;">{status_text}</div>
              <div style="height:3px;background:rgba(0,0,0,0.3);border-radius:3px;margin-top:0.7rem;overflow:hidden;">
                <div style="height:100%;width:{'100' if done else '0'}%;
                            background:linear-gradient(90deg,{accent},{accent}99);
                            border-radius:3px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tabbed upload areas ───────────────────────────────────
    tab_labels = [f"{icon} {label}" for icon, label, _, _ in doc_categories]
    tabs = st.tabs(tab_labels)

    for tab, ((icon, label, key, docs), (g_from, g_to, g_border, g_accent)) in zip(tabs, zip(doc_categories, cat_gradients)):
        with tab:
            col_left, col_right = st.columns([1, 1], gap="large")

            with col_left:
                doc_rows = "".join(
                    f'<div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0;'
                    f'border-bottom:1px solid rgba(255,255,255,0.04);">'
                    f'<span style="width:6px;height:6px;border-radius:50%;background:{g_accent};'
                    f'flex-shrink:0;display:inline-block;"></span>'
                    f'<span style="font-size:0.83rem;color:#C5C8D8;">{doc}</span></div>'
                    for doc in docs
                )
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,{g_from},{g_to});
                            border:1px solid {g_border};border-radius:12px;padding:1.1rem 1.3rem;height:100%;">
                  <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.7rem;">
                    <div style="width:28px;height:28px;border-radius:8px;background:{g_accent}22;
                                border:1px solid {g_accent}44;display:flex;align-items:center;
                                justify-content:center;font-size:0.9rem;">{icon}</div>
                    <div>
                      <div style="font-size:0.7rem;color:#8A8FA8;text-transform:uppercase;letter-spacing:0.08em;">Required for {label}</div>
                    </div>
                  </div>
                  {doc_rows}
                </div>
                """, unsafe_allow_html=True)

            with col_right:
                uploaded = st.file_uploader(
                    "Drop files here",
                    accept_multiple_files=True,
                    type=["pdf", "jpg", "jpeg", "png", "tiff"],
                    key=f"upload_{key}",
                    label_visibility="visible",
                )
                if uploaded:
                    file_rows = "".join(
                        f'<div style="display:flex;align-items:center;gap:0.5rem;padding:0.35rem 0;'
                        f'border-bottom:1px solid rgba(255,255,255,0.05);">'
                        f'<span style="color:#00D48A;font-size:0.8rem;">✓</span>'
                        f'<span style="font-size:0.82rem;color:#FFFFFF;flex:1;">{f.name}</span>'
                        f'<span style="font-size:0.72rem;color:#8A8FA8;">{len(f.getvalue())//1024} KB</span>'
                        f'</div>'
                        for f in uploaded
                    )
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,rgba(0,212,138,0.1),rgba(0,212,138,0.02));
                                border:1px solid rgba(0,212,138,0.2);border-radius:10px;
                                padding:0.7rem 0.9rem;margin-top:0.5rem;">
                      {file_rows}
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Submission
    col_submit, col_back = st.columns([1, 4])
    with col_submit:
        if st.button("🚀 Submit Application", type="primary", use_container_width=True):
            try:
                r = requests.post(f"{API}/api/applications/{st.session_state.app_id}/submit")
                if r.status_code == 200:
                    st.balloons()
                    st.markdown("""
                    <div style="background:rgba(0,212,138,0.1);border:1px solid rgba(0,212,138,0.3);
                                border-radius:12px;padding:1.2rem 1.5rem;margin-top:1rem;">
                      <div style="font-size:1rem;font-weight:700;color:#00D48A;">✓ Application Submitted Successfully</div>
                      <div style="font-size:0.85rem;color:#8A8FA8;margin-top:0.3rem;">
                        Your MSME loan application is now in the pipeline.<br>
                        KYC verification will begin shortly. Go to <strong>Dashboard</strong> to track progress.
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.completed_steps.add(5)
                else:
                    st.error(f"Submission failed: {r.text}")
            except Exception:
                st.error("Cannot connect to backend. Is the API running?")
    with col_back:
        if st.button("← Back", use_container_width=False, key="s5_back"):
            st.session_state.step = 4
            st.rerun()

    # Run pipeline button (for demo)
    if st.session_state.app_id and 5 in st.session_state.completed_steps:
        st.markdown("---")
        st.markdown('<div class="rv-section-title">DEMO — RUN AI PIPELINE</div>', unsafe_allow_html=True)
        if st.button("⚡ Run Full AI Pipeline (KYC → Underwriting → CAM)", use_container_width=False):
            with st.spinner("Running 15-stage pipeline..."):
                try:
                    r = requests.post(
                        f"{API}/api/applications/{st.session_state.app_id}/run-pipeline",
                        timeout=60
                    )
                    if r.status_code == 200:
                        res = r.json()
                        st.success("Pipeline complete! Go to Underwriting page to view results.")
                        with st.expander("Pipeline Results"):
                            st.json(res)
                    else:
                        st.error(f"Pipeline error: {r.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
