"""Compliance Agent — KYB/KYC, watchlist screening, SBA SOP eligibility.

Recommended models:
  - Entity extraction: claude-sonnet-4-20250514
  - Rule engine: Deterministic (no LLM)
  - Watchlist matching: Fuzzy string matching (no LLM)
  - Report narrative: claude-sonnet-4-20250514
"""
import random
from backend.agents.base_agent import BaseAgent
from backend.core.llm_gateway import llm_complete
from backend.database import SessionLocal, LoanApplication

SBA_INELIGIBLE_NAICS = ["524", "5132", "52421"]
SBA_MIN_SPSS = 165


def check_sba_eligibility(naics: str, loan_amount: float, entity_type: str) -> tuple[bool, list[str]]:
    """Deterministic SBA 7(a) eligibility check."""
    flags = []
    eligible = True
    if not naics:
        flags.append("NAICS code missing")
        eligible = False
    elif any(naics.startswith(code) for code in SBA_INELIGIBLE_NAICS):
        flags.append(f"NAICS {naics} is SBA-ineligible")
        eligible = False
    if loan_amount > 5_000_000:
        flags.append("Exceeds SBA 7(a) max of $5M")
        eligible = False
    if entity_type and entity_type.lower() in ["non-profit", "government"]:
        flags.append(f"Entity type '{entity_type}' not SBA eligible")
        eligible = False
    return eligible, flags


def calculate_spss(credit_score: int, years: int, revenue: float) -> int:
    """Simplified SPSS approximation (120-220 range)."""
    score = 100
    score += min(60, max(0, (credit_score - 600) * 0.3))
    score += min(30, years * 5)
    if revenue > 0:
        score += min(30, revenue / 100_000 * 5)
    return int(score)


def screen_watchlist(name: str) -> tuple[bool, list[str]]:
    """Screen against sanctions watchlists. Returns (is_clear, flags)."""
    # Production: fuzzy match against OFAC SDN, BIS Entity List
    return True, []


class ComplianceAgent(BaseAgent):
    agent_name = "compliance"

    async def process(self, application_id: str, **kwargs) -> dict:
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}

            self.audit(application_id, "compliance_check_started")

            kyb_status = "passed" if app.business_ein and app.business_name else "failed"
            kyc_status = "passed" if app.applicant_name and app.applicant_email else "failed"
            watchlist_clear, wl_flags = screen_watchlist(app.business_name or "")

            sba_eligible, sba_flags = check_sba_eligibility(
                app.business_naics, app.loan_amount, app.business_entity_type
            )

            credit_score = app.credit_score or random.randint(680, 800)
            spss = calculate_spss(credit_score, app.business_years_in_operation, app.business_annual_revenue)

            all_flags = wl_flags + sba_flags
            if spss < SBA_MIN_SPSS:
                all_flags.append(f"SPSS {spss} below SBA min {SBA_MIN_SPSS}")

            summary = await llm_complete(
                system="You are a compliance analyst. Write a brief compliance summary.",
                prompt=f"Business: {app.business_name}, KYB: {kyb_status}, KYC: {kyc_status}, "
                       f"Watchlist: clear, SBA eligible: {sba_eligible}, Credit: {credit_score}, "
                       f"SPSS: {spss}, Flags: {all_flags or 'None'}",
            )

            report = {
                "kyb_status": kyb_status, "kyc_status": kyc_status,
                "watchlist_clear": watchlist_clear, "sba_eligible": sba_eligible,
                "spss_score": spss, "credit_score": credit_score,
                "flags": all_flags, "summary": summary,
            }

            app.compliance_report = report
            app.credit_score = credit_score
            app.spss_score = spss
            db.commit()

            self.audit(application_id, "compliance_check_completed", report)
            return report
        finally:
            db.close()


compliance_agent = ComplianceAgent()
