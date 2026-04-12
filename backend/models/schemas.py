"""Pydantic schemas — India MSME Secured Loan LOS."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Application Schemas ──────────────────────────────────────

class ApplicationCreate(BaseModel):
    applicant_name: str = ""
    applicant_email: str = ""
    applicant_phone: str = ""
    city: str = ""
    business_name: str = ""
    loan_amount: float = 0
    lead_source: str = "web"


class ApplicationUpdate(BaseModel):
    # Contact
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    applicant_phone: Optional[str] = None
    city: Optional[str] = None

    # Promoter KYC
    promoter_pan: Optional[str] = None
    promoter_aadhaar: Optional[str] = None
    promoter_dob: Optional[str] = None
    promoter_address: Optional[str] = None
    shareholding_pct: Optional[float] = None

    # Business
    business_name: Optional[str] = None
    business_constitution: Optional[str] = None
    business_gst: Optional[str] = None
    business_address: Optional[str] = None
    industry_type: Optional[str] = None
    business_nic_code: Optional[str] = None
    business_years_in_operation: Optional[int] = None
    business_employees: Optional[int] = None
    business_annual_revenue: Optional[float] = None
    business_state: Optional[str] = None

    # Loan
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    loan_tenure_months: Optional[int] = None

    # Collateral
    collateral_type: Optional[str] = None
    collateral_address: Optional[str] = None
    collateral_estimated_value: Optional[float] = None
    collateral_owner_name: Optional[str] = None
    collateral_ownership_type: Optional[str] = None

    # Documents
    documents_json: Optional[list] = None

    # Tracking
    current_step: Optional[int] = None
    status: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: str
    status: str
    applicant_name: str = ""
    applicant_email: str = ""
    applicant_phone: str = ""
    city: str = ""
    business_name: str = ""
    business_constitution: str = ""
    business_gst: str = ""
    loan_amount: float = 0
    loan_purpose: str = ""
    loan_tenure_months: int = 60
    collateral_type: str = ""
    collateral_estimated_value: float = 0
    collateral_market_value: float = 0
    ltv_ratio: float = 0
    dscr: float = 0
    risk_score: float = 0
    risk_rating: str = ""
    cibil_score: int = 0
    credit_score: int = 0
    avg_monthly_cashflow: float = 0
    annual_revenue_reported: float = 0
    net_profit: float = 0
    debt_equity_ratio: float = 0
    revenue_growth_pct: float = 0
    operating_margin_pct: float = 0
    existing_emi_obligations: float = 0
    cam_draft: str = ""
    cam_analyst_notes: str = ""
    underwriting_memo: str = ""
    recommended_loan_amount: float = 0
    recommended_interest_rate: float = 0
    sanction_amount: float = 0
    sanction_interest_rate: float = 0
    sanction_tenure_months: int = 0
    sanction_emi: float = 0
    disbursed_amount: float = 0
    disbursed_at: Optional[datetime] = None
    disbursement_reference: str = ""
    collateral_legal_status: str = "pending"
    encumbrance_status: str = "pending"
    kyc_pan_status: str = "pending"
    kyc_aadhaar_status: str = "pending"
    kyc_ckyc_number: str = ""
    industry_type: str = ""
    business_annual_revenue: float = 0
    business_years_in_operation: int = 0
    current_step: int = 1
    completion_pct: float = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Chat Schemas ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    application_id: str
    message: str
    channel: str = "web"


class ChatResponse(BaseModel):
    role: str
    content: str
    created_at: datetime


# ── Dashboard Schemas ────────────────────────────────────────

class PipelineStats(BaseModel):
    total_applications: int = 0
    lead_created: int = 0
    application_draft: int = 0
    kyc_pending: int = 0
    document_collection: int = 0
    underwriting: int = 0
    sanctioned: int = 0
    disbursed: int = 0
    declined: int = 0
    avg_completion: float = 0
    total_loan_value: float = 0


class AuditEntryResponse(BaseModel):
    id: int
    application_id: str
    agent: str
    action: str
    details: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ── KYC Schemas ──────────────────────────────────────────────

class KYCResult(BaseModel):
    pan_status: str = "pending"       # pending, verified, failed
    aadhaar_status: str = "pending"
    ckyc_number: str = ""
    ckyc_status: str = "pending"
    flags: list[str] = Field(default_factory=list)
    summary: str = ""


# ── Financial Analysis Schemas ────────────────────────────────

class FinancialMetrics(BaseModel):
    avg_monthly_cashflow: float = 0
    annual_revenue_reported: float = 0
    net_profit: float = 0
    dscr: float = 0
    debt_equity_ratio: float = 0
    revenue_growth_pct: float = 0
    operating_margin_pct: float = 0
    summary: str = ""


# ── Collateral Assessment Schemas ─────────────────────────────

class CollateralAssessment(BaseModel):
    market_value: float = 0
    distress_value: float = 0
    ltv_ratio: float = 0
    legal_status: str = "pending"
    encumbrance_status: str = "pending"
    max_eligible_loan: float = 0
    summary: str = ""


# ── Underwriting Schemas ──────────────────────────────────────

class UnderwritingResult(BaseModel):
    risk_score: float = 0
    risk_rating: str = ""
    dscr: float = 0
    ltv_ratio: float = 0
    cibil_score: int = 0
    recommendation: str = ""         # approve, decline, refer
    recommended_amount: float = 0
    recommended_rate: float = 0
    cam_draft: str = ""
    memo: str = ""


# ── CAM Schemas ───────────────────────────────────────────────

class CAMReport(BaseModel):
    borrower_profile: str = ""
    financial_summary: str = ""
    collateral_details: str = ""
    credit_risk: str = ""
    recommended_loan: str = ""
    analyst_notes: str = ""


# ── Approval Schemas ──────────────────────────────────────────

class ApprovalRequest(BaseModel):
    application_id: str
    decision: str                    # approve, decline, refer_back
    conditions: list[str] = Field(default_factory=list)
    approved_by: str = ""
    notes: str = ""


# ── Sanction Schemas ──────────────────────────────────────────

class SanctionDetails(BaseModel):
    loan_amount: float = 0
    interest_rate: float = 0
    tenure_months: int = 0
    emi: float = 0
    collateral_description: str = ""
    conditions: list[str] = Field(default_factory=list)


# ── Disbursement Schemas ──────────────────────────────────────

class DisbursementRequest(BaseModel):
    application_id: str
    account_number: str
    ifsc_code: str
    amount: float


# ── Compliance / Agent Output Schemas (legacy compat) ─────────

class ComplianceReport(BaseModel):
    kyb_status: str = "pending"
    kyc_status: str = "pending"
    pan_verified: bool = False
    aadhaar_verified: bool = False
    ckyc_status: str = "pending"
    watchlist_clear: bool = False
    cibil_score: int = 0
    flags: list[str] = Field(default_factory=list)
    summary: str = ""


class PricingResult(BaseModel):
    interest_rate: float = 0
    term_months: int = 0
    monthly_emi: float = 0
    total_interest: float = 0
    rate_rationale: str = ""
    term_sheet_text: str = ""
