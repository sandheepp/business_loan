"""Database models and session management — India MSME Secured Loan LOS."""
import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def now():
    return datetime.datetime.now(datetime.timezone.utc)


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(String, primary_key=True)
    status = Column(String, default="lead_created")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    # ── Stage 1: Lead Creation ────────────────────────────────
    lead_source = Column(String, default="web")          # web, rm, partner_api
    rm_assigned = Column(String, default="")             # Relationship Manager ID

    # ── Stage 2: Borrower Application ────────────────────────
    # Contact info
    applicant_name = Column(String, default="")
    applicant_email = Column(String, default="")
    applicant_phone = Column(String, default="")
    city = Column(String, default="")

    # Promoter / KYC identity
    promoter_pan = Column(String, default="")            # PAN card number
    promoter_aadhaar = Column(String, default="")        # Aadhaar number (masked)
    promoter_dob = Column(String, default="")            # Date of birth
    promoter_address = Column(Text, default="")          # Residential address
    shareholding_pct = Column(Float, default=100.0)      # Shareholding percentage

    # Business Details
    business_name = Column(String, default="")
    business_constitution = Column(String, default="")   # Proprietorship, LLP, Pvt Ltd
    business_gst = Column(String, default="")            # GST number
    business_address = Column(Text, default="")
    industry_type = Column(String, default="")           # Industry / sector
    business_nic_code = Column(String, default="")       # NIC code
    business_years_in_operation = Column(Integer, default=0)
    business_employees = Column(Integer, default=0)
    business_annual_revenue = Column(Float, default=0)   # Annual turnover (INR)
    business_state = Column(String, default="")

    # Loan Details
    loan_amount = Column(Float, default=0)               # Requested amount (INR)
    loan_purpose = Column(String, default="")
    loan_tenure_months = Column(Integer, default=60)     # Preferred tenure

    # Collateral Details
    collateral_type = Column(String, default="")         # Residential, Commercial, Industrial, Agricultural
    collateral_address = Column(Text, default="")
    collateral_estimated_value = Column(Float, default=0)
    collateral_owner_name = Column(String, default="")
    collateral_ownership_type = Column(String, default="")  # Self, Relative, Third-party

    # ── Stage 3: KYC Verification ────────────────────────────
    kyc_pan_status = Column(String, default="pending")   # pending, verified, failed
    kyc_aadhaar_status = Column(String, default="pending")
    kyc_ckyc_number = Column(String, default="")         # CKYC registry number
    kyc_ckyc_status = Column(String, default="pending")
    kyc_verified_at = Column(DateTime, nullable=True)
    kyc_flags = Column(JSON, default=list)               # Mismatch flags

    # ── Stage 4: Document Collection ─────────────────────────
    # documents_json: [{filename, doc_type, category, uploaded_at, ocr_status}]
    # Categories: identity, business, financial, collateral
    documents_json = Column(JSON, default=list)

    # ── Stage 5: Data Extraction ─────────────────────────────
    extracted_data = Column(JSON, default=dict)          # OCR/AI extracted fields

    # ── Stage 6: External Data Enrichment ────────────────────
    cibil_score = Column(Integer, default=0)             # CIBIL / Experian credit score
    cibil_report = Column(JSON, default=dict)
    gstn_data = Column(JSON, default=dict)               # GSTN revenue data
    mca_data = Column(JSON, default=dict)                # MCA company information
    bank_statement_data = Column(JSON, default=dict)     # Bank aggregation transactions

    # ── Stage 7: Financial Analysis ──────────────────────────
    avg_monthly_cashflow = Column(Float, default=0)
    annual_revenue_reported = Column(Float, default=0)
    net_profit = Column(Float, default=0)
    total_assets = Column(Float, default=0)
    total_liabilities = Column(Float, default=0)
    existing_emi_obligations = Column(Float, default=0)  # Monthly EMI obligations
    dscr = Column(Float, default=0)                      # Debt Service Coverage Ratio
    debt_equity_ratio = Column(Float, default=0)
    revenue_growth_pct = Column(Float, default=0)        # YoY revenue growth %
    operating_margin_pct = Column(Float, default=0)      # Operating margin %

    # ── Stage 8: Collateral Assessment ───────────────────────
    collateral_valuation_report = Column(JSON, default=dict)
    collateral_market_value = Column(Float, default=0)   # Valuer-assessed market value
    collateral_distress_value = Column(Float, default=0)
    ltv_ratio = Column(Float, default=0)                 # Loan-to-Value ratio
    collateral_legal_status = Column(String, default="pending")  # pending, clear, encumbered
    encumbrance_status = Column(String, default="pending")

    # ── Stage 9: Credit Underwriting ─────────────────────────
    risk_score = Column(Float, default=0)                # 0–100
    risk_rating = Column(String, default="")             # A, B, C, D, E
    underwriting_memo = Column(Text, default="")

    # ── Stage 10: Credit Memo (CAM) ──────────────────────────
    cam_draft = Column(Text, default="")
    cam_finalized_at = Column(DateTime, nullable=True)
    cam_analyst_notes = Column(Text, default="")
    recommended_loan_amount = Column(Float, default=0)
    recommended_interest_rate = Column(Float, default=0)

    # ── Stage 11: Approval Workflow ───────────────────────────
    approval_level = Column(String, default="")          # bcm, rch, credit_committee
    approved_by = Column(String, default="")
    approved_at = Column(DateTime, nullable=True)
    approval_conditions = Column(JSON, default=list)     # Conditions precedent

    # ── Stage 12: Sanction Letter ─────────────────────────────
    sanction_amount = Column(Float, default=0)
    sanction_interest_rate = Column(Float, default=0)
    sanction_tenure_months = Column(Integer, default=0)
    sanction_emi = Column(Float, default=0)
    sanction_letter_url = Column(String, default="")
    sanction_signed_at = Column(DateTime, nullable=True)

    # ── Stage 13: Legal Documentation ────────────────────────
    legal_docs_generated = Column(JSON, default=list)    # loan_agreement, mortgage_deed, etc.
    property_registered = Column(Boolean, default=False)
    legal_verified_at = Column(DateTime, nullable=True)

    # ── Stage 14: Disbursement ────────────────────────────────
    disbursement_checklist = Column(JSON, default=dict)  # {kyc, collateral, agreements}
    disbursement_account = Column(String, default="")    # Beneficiary account
    disbursed_amount = Column(Float, default=0)
    disbursed_at = Column(DateTime, nullable=True)
    disbursement_reference = Column(String, default="")  # CBS reference number

    # ── Stage 15: Post-Disbursement Monitoring ────────────────
    monitoring_alerts = Column(JSON, default=list)       # Missed EMI, revenue drop, etc.
    last_gst_filing_revenue = Column(Float, default=0)
    repayment_behavior = Column(String, default="")      # regular, irregular, npa

    # ── Tracking ──────────────────────────────────────────────
    current_step = Column(Integer, default=1)
    completion_pct = Column(Float, default=0)
    last_activity = Column(DateTime, default=now)
    churn_notified = Column(Integer, default=0)

    # Legacy compat fields (kept for existing API responses)
    applicant_phone_legacy = Column(String, default="")
    credit_score = Column(Integer, default=0)            # Alias for cibil_score
    spss_score = Column(Integer, default=0)
    compliance_report = Column(JSON, default=dict)
    pricing_data = Column(JSON, default=dict)
    loan_product = Column(String, default="msme_secured")
    loan_purpose_detail = Column(String, default="")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, index=True)
    role = Column(String)           # user, assistant
    content = Column(Text)
    channel = Column(String, default="web")  # web, sms, email
    created_at = Column(DateTime, default=now)


class AuditEntry(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, index=True)
    agent = Column(String)          # sarah, kyc, document, financial, collateral, underwriting, approval, disbursement, orchestrator
    action = Column(String)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=now)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
