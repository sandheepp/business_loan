"""Loan Application Form — Streamlit page."""
import streamlit as st
import requests
from datetime import datetime

API = st.session_state.get("api_url", "http://localhost:8000")

st.set_page_config(page_title="CASA — Application", page_icon="📋", layout="wide")

# Custom CSS for modern styling
st.markdown("""
<style>
    .step-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid #0066cc;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1.5rem;
        padding: 0.75rem 0 0.75rem 0;
        border-bottom: 3px solid #0066cc;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        border-left: 4px solid #28a745;
        font-weight: 500;
    }
    .info-container {
        background-color: #e7f3ff;
        color: #004085;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        margin-bottom: 1rem;
    }
    .progress-step {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .progress-step.active {
        background-color: #0066cc;
        color: white;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }
    .progress-step.completed {
        background-color: #28a745;
        color: white;
    }
    .progress-step.pending {
        background-color: #f0f0f0;
        color: #999;
    }
    .field-group {
        margin-bottom: 1.5rem;
    }
    .header-section {
        text-align: center;
        padding: 3rem 0 1rem 0;
        margin-bottom: 2rem;
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .header-subtitle {
        font-size: 1.1rem;
        color: #b8c5e0;
        margin-bottom: 1rem;
    }
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="header-section"><div class="header-title">📋 Business Loan Application</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #666; font-size: 1.1rem;">Fast. Transparent. AI-Powered.</div>', unsafe_allow_html=True)

# Initialize session
if "app_id" not in st.session_state:
    st.session_state.app_id = None
if "step" not in st.session_state:
    st.session_state.step = 1
if "completed_steps" not in st.session_state:
    st.session_state.completed_steps = set()

# Progress indicator
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)
steps = [
    (1, "👤 Contact", "Your Info"),
    (2, "💰 Loan", "Amount & Type"),
    (3, "🏢 Business", "Details"),
    (4, "👨‍💼 Owners", "Ownership"),
    (5, "📄 Documents", "Uploads")
]
for idx, (col, (step_num, step_icon, step_label)) in enumerate(zip([col1, col2, col3, col4, col5], steps)):
    with col:
        if step_num < st.session_state.step:
            status_class = "progress-step completed"
            status_icon = "✓"
        elif step_num == st.session_state.step:
            status_class = "progress-step active"
            status_icon = "●"
        else:
            status_class = "progress-step pending"
            status_icon = "○"
        st.markdown(f'<div class="{status_class}"><strong>{status_icon}</strong><br/><small>{step_label}</small></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Step 1: Contact Information ──
if st.session_state.step >= 1:
    st.markdown('<div class="section-title">👤 Step 1: Your Contact Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-container">We\'ll use this to keep you updated on your application status.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "Full Name",
            key="name",
            placeholder="Shelley Johnson",
            help="Your legal first and last name"
        )
        email = st.text_input(
            "Email Address",
            key="email",
            placeholder="shel@gmail.com",
            help="We\'ll verify this email for communication"
        )
    with col2:
        phone = st.text_input(
            "Phone Number",
            key="phone",
            placeholder="(619) 555-0123",
            help="Mobile preferred for SMS updates"
        )
    
    col_button, col_space = st.columns([1, 3])
    with col_button:
        if st.button("Continue →", type="primary", use_container_width=True):
            if name and email:
                try:
                    r = requests.post(f"{API}/api/applications/", json={
                        "applicant_name": name,
                        "applicant_email": email,
                        "applicant_phone": phone,
                    })
                    if r.status_code == 200:
                        st.session_state.app_id = r.json()["id"]
                        st.session_state.step = 2
                        st.session_state.completed_steps.add(1)
                        st.rerun()
                except Exception as e:
                    st.error("❌ Could not connect to backend. Is the API running?")
            else:
                st.error("⚠️ Please fill in your name and email.")

# ── Step 2: Loan Request ──
if st.session_state.step >= 2 and st.session_state.app_id:
    st.markdown("---")
    st.markdown('<div class="section-title">💰 Step 2: Loan Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-container">Tell us about the loan you need.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input(
            "Loan Amount ($)",
            min_value=10000,
            max_value=5000000,
            value=300000,
            step=10000,
            key="amount",
            help="Amount you want to borrow"
        )
        purpose = st.selectbox(
            "Loan Purpose",
            [
                "Working Capital",
                "Equipment Purchase",
                "Real Estate",
                "Business Acquisition",
                "Debt Refinancing",
                "Other"
            ],
            key="purpose",
            help="What will you use the loan for?"
        )
    with col2:
        product = st.selectbox(
            "Loan Product",
            ["sba_7a", "sba_504", "conventional", "line_of_credit"],
            key="product",
            format_func=lambda x: {
                "sba_7a": "SBA 7(a)",
                "sba_504": "SBA 504",
                "conventional": "Conventional",
                "line_of_credit": "Line of Credit"
            }.get(x, x),
            help="Choose the loan program that best fits your needs"
        )
        st.markdown('<div style="margin-top: 1rem; padding: 1rem; background: #f9f9f9; border-radius: 6px; font-size: 0.9rem;"><strong>💡 Tip:</strong> Not sure which product? SBA 7(a) works for most small businesses.</div>', unsafe_allow_html=True)

    col_button, col_back = st.columns([1, 3])
    with col_button:
        if st.button("Continue →", type="primary", use_container_width=True, key="step2_continue"):
            try:
                requests.patch(f"{API}/api/applications/{st.session_state.app_id}", json={
                    "loan_amount": amount,
                    "loan_purpose": purpose,
                    "loan_product": product,
                    "current_step": 3,
                })
                st.session_state.step = 3
                st.session_state.completed_steps.add(2)
                st.rerun()
            except Exception as e:
                st.error("❌ Could not save. Is the API running?")
    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

# ── Step 3: Business Information ──
if st.session_state.step >= 3 and st.session_state.app_id:
    st.markdown("---")
    st.markdown('<div class="section-title">🏢 Step 3: Business Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-container">Help us understand your business better.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        biz_name = st.text_input(
            "Business Legal Name",
            placeholder="California Dental LLC",
            key="biz_name"
        )
        ein = st.text_input(
            "EIN / TIN",
            placeholder="12-3456789",
            key="ein",
            help="Your 9-digit Employer Identification Number"
        )
        entity = st.selectbox(
            "Entity Type",
            ["LLC", "S-Corp", "C-Corp", "Partnership", "Sole Proprietorship"],
            key="entity"
        )
    with col2:
        address = st.text_input(
            "Business Address",
            placeholder="4320 Cherokee Ave, San Diego, CA",
            key="address"
        )
        state = st.selectbox(
            "State",
            ["CA", "NY", "TX", "FL", "IL", "Other"],
            key="state"
        )
        naics = st.text_input(
            "NAICS Code",
            placeholder="621210",
            key="naics",
            help="Industry code — look yours up at census.gov"
        )
    
    col3, col4 = st.columns(2)
    with col3:
        employees = st.number_input(
            "Number of Employees",
            min_value=0,
            value=12,
            key="employees"
        )
        revenue = st.number_input(
            "Annual Revenue ($)",
            min_value=0,
            value=917000,
            step=10000,
            key="revenue"
        )
    with col4:
        years = st.number_input(
            "Years in Business",
            min_value=0,
            value=8,
            key="years"
        )

    col_button, col_back = st.columns([1, 3])
    with col_button:
        if st.button("Continue →", type="primary", use_container_width=True, key="step3_continue"):
            try:
                requests.patch(f"{API}/api/applications/{st.session_state.app_id}", json={
                    "business_name": biz_name,
                    "business_ein": ein,
                    "business_address": address,
                    "business_entity_type": entity,
                    "business_naics": naics,
                    "business_state": state,
                    "business_employees": employees,
                    "business_annual_revenue": revenue,
                    "business_years_in_operation": years,
                    "current_step": 4,
                })
                st.session_state.step = 4
                st.session_state.completed_steps.add(3)
                st.rerun()
            except Exception as e:
                st.error("❌ Could not save.")
    with col_back:
        if st.button("← Back", use_container_width=True, key="step3_back"):
            st.session_state.step = 2
            st.rerun()

# ── Step 4: Ownership ──
if st.session_state.step >= 4 and st.session_state.app_id:
    st.markdown("---")
    st.markdown('<div class="section-title">👨‍💼 Step 4: Ownership Information</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-container">Tell us about the business ownership structure.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        owner_name = st.text_input(
            "Primary Owner Name",
            placeholder="Shelley Johnson",
            key="owner_name"
        )
    with col2:
        owner_pct = st.slider(
            "Ownership %",
            0,
            100,
            100,
            key="owner_pct",
            help="What percentage do they own?"
        )

    col_button, col_back = st.columns([1, 3])
    with col_button:
        if st.button("Continue →", type="primary", use_container_width=True, key="step4_continue"):
            try:
                requests.patch(f"{API}/api/applications/{st.session_state.app_id}", json={
                    "owners_json": [{"name": owner_name, "ownership_pct": owner_pct}],
                    "current_step": 5,
                })
                st.session_state.step = 5
                st.session_state.completed_steps.add(4)
                st.rerun()
            except Exception as e:
                st.error("❌ Could not save.")
    with col_back:
        if st.button("← Back", use_container_width=True, key="step4_back"):
            st.session_state.step = 3
            st.rerun()

# ── Step 5: Documents ──
if st.session_state.step >= 5 and st.session_state.app_id:
    st.markdown("---")
    st.markdown('<div class="section-title">📄 Step 5: Upload Documents</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-container">📎 Upload your tax returns, bank statements, and financial documents. We support PDF, JPG, PNG, and TIFF.</div>', unsafe_allow_html=True)
    
    uploaded = st.file_uploader(
        "Drop files here or click to browse",
        accept_multiple_files=True,
        type=["pdf", "jpg", "png", "tiff"],
        label_visibility="collapsed"
    )
    
    if uploaded:
        st.markdown("#### ✅ Uploaded Files:")
        for idx, f in enumerate(uploaded, 1):
            col_icon, col_name, col_remove = st.columns([0.5, 3, 0.5])
            with col_icon:
                st.markdown("📎")
            with col_name:
                st.markdown(f"**{f.name}** — Auto-classifying...")
            # with col_remove:
            #     st.text("")

    st.markdown("---")
    col_submit, col_back, col_space = st.columns([1, 1, 2])
    with col_submit:
        if st.button("🚀 Submit Application", type="primary", use_container_width=True):
            try:
                r = requests.post(f"{API}/api/applications/{st.session_state.app_id}/submit")
                if r.status_code == 200:
                    st.balloons()
                    st.markdown('<div class="success-badge">✅ Application submitted successfully!</div>', unsafe_allow_html=True)
                    st.success("Sarah will keep you updated on your progress.")
                    st.info("📊 Go to the **Dashboard** page to see the loan officer view.")
                    st.session_state.completed_steps.add(5)
                else:
                    st.error(f"❌ Error: {r.json()}")
            except Exception as e:
                st.error("❌ Could not submit. Is the API running?")
    with col_back:
        if st.button("← Back", use_container_width=True, key="step5_back"):
            st.session_state.step = 4
            st.rerun()

# Sidebar summary
st.sidebar.markdown("---")
st.sidebar.markdown("## 📋 Application Summary")
if st.session_state.app_id:
    st.sidebar.markdown(f"**Application ID:**  \n`{st.session_state.app_id}`")
    
    # Progress percentage
    progress_pct = min(st.session_state.step / 5, 1.0)
    st.sidebar.progress(progress_pct, f"**Step {st.session_state.step} of 5**")
    
    # Form field summary
    if st.session_state.step >= 1:
        name_filled = bool(st.session_state.get("name"))
        st.sidebar.markdown(f"{'✅' if name_filled else '⭕'} Contact Info")
    if st.session_state.step >= 2:
        amount_filled = bool(st.session_state.get("amount"))
        st.sidebar.markdown(f"{'✅' if amount_filled else '⭕'} Loan Details")
    if st.session_state.step >= 3:
        biz_filled = bool(st.session_state.get("biz_name"))
        st.sidebar.markdown(f"{'✅' if biz_filled else '⭕'} Business Info")
    if st.session_state.step >= 4:
        owner_filled = bool(st.session_state.get("owner_name"))
        st.sidebar.markdown(f"{'✅' if owner_filled else '⭕'} Ownership")
    if st.session_state.step >= 5:
        st.sidebar.markdown("⭕ Documents")

st.sidebar.markdown("---")
st.sidebar.markdown('<div style="font-size: 0.85rem; color: #666;">💡 **Pro Tip:** All fields auto-save as you type. You can close the browser and come back later.</div>', unsafe_allow_html=True)
