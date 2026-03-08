"""Pydantic schemas for API models."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Application Schemas ──────────────────────────────────────

class OwnerInfo(BaseModel):
    name: str = ""
    ownership_pct: float = 0
    ssn_last4: str = ""
    dob: str = ""


class ApplicationCreate(BaseModel):
    applicant_name: str = ""
    applicant_email: str = ""
    applicant_phone: str = ""


class ApplicationUpdate(BaseModel):
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    applicant_phone: Optional[str] = None
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    loan_product: Optional[str] = None
    business_name: Optional[str] = None
    business_ein: Optional[str] = None
    business_address: Optional[str] = None
    business_entity_type: Optional[str] = None
    business_naics: Optional[str] = None
    business_state: Optional[str] = None
    business_employees: Optional[int] = None
    business_annual_revenue: Optional[float] = None
    business_years_in_operation: Optional[int] = None
    owners_json: Optional[list] = None
    current_step: Optional[int] = None


class ApplicationResponse(BaseModel):
    id: str
    status: str
    applicant_name: str
    applicant_email: str
    business_name: str
    loan_amount: float
    loan_purpose: str
    loan_product: str
    current_step: int
    completion_pct: float
    risk_score: float
    dscr: float
    credit_score: int
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
    draft: int = 0
    submitted: int = 0
    in_review: int = 0
    approved: int = 0
    declined: int = 0
    avg_completion: float = 0
    churned_count: int = 0
    reactivated_count: int = 0


class AuditEntryResponse(BaseModel):
    id: int
    application_id: str
    agent: str
    action: str
    details: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ── Agent Output Schemas ─────────────────────────────────────

class ComplianceReport(BaseModel):
    kyb_status: str = "pending"  # passed, failed, pending
    kyc_status: str = "pending"
    watchlist_clear: bool = False
    sba_eligible: bool = False
    spss_score: int = 0
    credit_score: int = 0
    flags: list[str] = Field(default_factory=list)
    summary: str = ""


class UnderwritingResult(BaseModel):
    net_income: float = 0
    add_backs: dict = Field(default_factory=dict)
    adjusted_income: float = 0
    annual_personal_debt: float = 0
    existing_debt_service: float = 0
    new_debt_service: float = 0
    dscr: float = 0
    risk_score: float = 0
    memo: str = ""


class PricingResult(BaseModel):
    interest_rate: float = 0
    term_months: int = 0
    monthly_payment: float = 0
    total_interest: float = 0
    rate_rationale: str = ""
    term_sheet_text: str = ""
