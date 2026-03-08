"""Pricing Agent — Rate calculation, term sheet generation.

Models: Deterministic engine for all math. claude-haiku-4-5-20251001 for term sheet formatting.
"""
from backend.agents.base_agent import BaseAgent
from backend.core.llm_gateway import llm_complete
from backend.database import SessionLocal, LoanApplication

BASE_PRIME_RATE = 7.75

RISK_SPREADS = {
    "excellent": 2.25, "good": 2.75, "fair": 3.50,
    "marginal": 4.50, "poor": 6.00,
}


def risk_tier(score: float) -> str:
    if score >= 90: return "excellent"
    if score >= 75: return "good"
    if score >= 60: return "fair"
    if score >= 45: return "marginal"
    return "poor"


def calculate_rate(risk_score: float) -> float:
    tier = risk_tier(risk_score)
    return round(BASE_PRIME_RATE + RISK_SPREADS[tier], 2)


def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    if annual_rate == 0 or term_months == 0:
        return principal / max(term_months, 1)
    r = annual_rate / 100 / 12
    return round(principal * (r * (1 + r)**term_months) / ((1 + r)**term_months - 1), 2)


class PricingAgent(BaseAgent):
    agent_name = "pricing"

    async def process(self, application_id: str, **kwargs) -> dict:
        db = SessionLocal()
        try:
            app = db.query(LoanApplication).filter_by(id=application_id).first()
            if not app:
                return {"error": "Application not found"}
            self.audit(application_id, "pricing_started")

            loan_amount = app.loan_amount or 300000
            risk_score = app.risk_score or 95
            term_months = 120
            rate = calculate_rate(risk_score)
            monthly = calculate_monthly_payment(loan_amount, rate, term_months)
            total_interest = round(monthly * term_months - loan_amount, 2)
            tier = risk_tier(risk_score)

            term_sheet = await llm_complete(
                system="You are a pricing analyst. Generate a term sheet summary.",
                prompt=f"Business: {app.business_name}, Loan: ${loan_amount:,.0f} SBA 7(a), "
                       f"Rate: {rate}%, Term: {term_months}mo, Monthly: ${monthly:,.2f}, "
                       f"Risk: {tier} ({risk_score}/100). Generate term sheet.",
            )

            pricing = {
                "interest_rate": rate, "term_months": term_months,
                "monthly_payment": monthly, "total_interest": total_interest,
                "risk_tier": tier, "prime_rate": BASE_PRIME_RATE,
                "spread": RISK_SPREADS[tier],
                "rate_rationale": f"Prime ({BASE_PRIME_RATE}%) + {RISK_SPREADS[tier]}% for {tier}",
                "term_sheet_text": term_sheet,
            }
            app.pricing_data = pricing
            db.commit()
            self.audit(application_id, "pricing_completed", {"rate": rate, "tier": tier})
            return pricing
        finally:
            db.close()


pricing_agent = PricingAgent()
